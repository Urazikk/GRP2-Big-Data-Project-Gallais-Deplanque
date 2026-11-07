import datetime

from pyspark.sql import functions as F

from imdb_project.enrichment.build import (
    CREDIT_SCHEMA,
    ENRICHED_SCHEMA,
    RAW_FILM_SCHEMA,
    RAW_PERSON_SCHEMA,
    clean_films,
    clean_people,
    enriched_films,
)
from imdb_project.enrichment.collect import match
from imdb_project.enrichment.wikipedia import (
    WikipediaClient,
    film_candidates,
    infobox_languages,
    person_candidates,
    plot_section,
)
from imdb_project.exploration.languages import multilingual_actors, original_language

WIKITEXT = """{{Infobox film
| name = Movie
| language = {{Plainlist|
* English
* [[French language|French]]<ref>a source</ref>
}}
}}
Movie is a film.

== Plot ==
A man<ref>x</ref> walks [[Paris|in Paris]].[[File:a.jpg|thumb|caption]]

=== Second part ===
Then {{cite web|url=u}}more.

== Cast ==
* Someone
"""


def test_plot_section_and_languages():
    plot, heading = plot_section(WIKITEXT)
    assert heading == "Plot"
    assert plot == "A man walks in Paris.\nSecond part\nThen more."
    assert infobox_languages(WIKITEXT) == ["English", "French"]
    assert plot_section("No sections here.") == ("", None)


def test_candidates():
    assert film_candidates("Amélie", "Le fabuleux destin", 2001)[:3] == [
        "Amélie (2001 film)", "Amélie (film)", "Amélie"]
    assert person_candidates("Jane Doe", "actress") == [
        "Jane Doe", "Jane Doe (actress)", "Jane Doe (actor)"]


class FakeResponse:
    status_code, headers = 200, {}

    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


class FakeSession:
    """Answers a batch query: one redirect, one disambiguation, one missing page."""

    def __init__(self):
        self.headers, self.calls = {}, 0

    def get(self, url, timeout):
        self.calls += 1
        return FakeResponse({"query": {
            "redirects": [{"from": "Movie (film)", "to": "Movie (2001 film)"}],
            "pages": [
                {"title": "Movie (2001 film)",
                 "extlinks": [{"url": "https://www.imdb.com/title/tt0000001/"}]},
                {"title": "Movie", "pageprops": {"disambiguation": ""}},
                {"title": "Other", "missing": True},
            ]}})


def test_imdb_pages_resolves_batches_and_caches(tmp_path):
    session = FakeSession()
    client = WikipediaClient(tmp_path / "cache.sqlite", min_interval=0, session=session)
    titles = ["Movie (film)", "Movie", "Other"]
    found = client.imdb_pages(titles, "title")
    assert found == {"Movie (film)": ("Movie (2001 film)", {"tt0000001"}),
                     "Movie": None, "Other": None}
    client.imdb_pages(titles, "title")
    assert session.calls == 1  # the second lookup is served from the cache


def test_match_keeps_first_page_linking_to_the_id():
    found = {"A (film)": ("A (film)", {"tt2"}), "A": ("A", {"tt1"})}
    out = match({"tt1": ["A (film)", "A"], "tt9": ["B"], "tt2": ["A (film)"]},
                {"tt1": "tt1", "tt9": "tt9", "tt2": "tt2"}, found)
    assert out["tt1"] == ("A", None)
    assert out["tt2"] == ("A (film)", None)
    assert out["tt9"][0] is None and "no English Wikipedia page found" in out["tt9"][1]
    out = match({"tt3": ["A"]}, {"tt3": "tt3"}, found)
    assert "no English Wikipedia page linking to tt3" in out["tt3"][1]


def test_build_cleans_and_imposes_schema(spark):
    raw_films = spark.createDataFrame(
        [("t1", "Movie", "https://en.wikipedia.org/wiki/Movie", "2026-11-06T10:00:00+00:00",
          "A  story[1] with   spaces[ 12 ] .\n\n Then more[citation needed].", "Plot",
          ["French[2]", " ", "Silent film with French intertitles"], None),
         ("t2", None, None, None, None, None, [], "no English Wikipedia page found for: X")],
        RAW_FILM_SCHEMA,
    )
    raw_people = spark.createDataFrame(
        [("n1", "A", "https://en.wikipedia.org/wiki/A", "2026-11-06T10:00:00+00:00",
          "A is an actor[1].", None),
         ("n2", None, None, None, None, "no English Wikipedia page found for: B")],
        RAW_PERSON_SCHEMA,
    )
    films = clean_films(raw_films)
    row = films.where("tconst = 't1'").first()
    assert row.synopsis == "A story with spaces.\nThen more."
    assert row.languages == ["French"]

    top = spark.createDataFrame([("t1", ["Drama"]), ("t2", ["Comedy"])],
                                "tconst string, top_genres array<string>")
    basics = spark.createDataFrame(
        [("t1", "Movie", 2001, 100, "Drama"), ("t2", "Other", 2002, 90, "Comedy")],
        "tconst string, primaryTitle string, startYear int, runtimeMinutes int, genres string",
    )
    ratings = spark.createDataFrame([("t1", 7.5, 1000)],
                                    "tconst string, averageRating double, numVotes int")
    credits = spark.createDataFrame(
        [("t1", 1, "n1", "actor", "A", "actor"), ("t1", 2, "n2", "actress", "B", "actress"),
         ("t1", 3, "n3", "director", "C", "director")],
        CREDIT_SCHEMA,
    )
    out = enriched_films(top, basics, ratings, films, credits, clean_people(raw_people))
    assert out.schema.simpleString() == ENRICHED_SCHEMA.simpleString()
    t1 = out.where("tconst = 't1'").first()
    assert [p.nconst for p in t1.principals] == ["n1", "n2"]  # n3 was not looked up
    assert t1.biographies_found == 1
    assert t1.principals[0].biography == "A is an actor."
    assert isinstance(t1.synopsis_retrieved_at, datetime.datetime)
    t2 = out.where("tconst = 't2'").first()
    assert t2.synopsis is None and t2.synopsis_note.startswith("no English Wikipedia page")
    assert t2.principals == [] and t2.biographies_found == 0


def test_multilingual_actors(spark):
    film_languages = spark.createDataFrame(
        [("t1", ["English", "French"]), ("t2", ["French"]), ("t3", ["Japanese"]),
         ("t4", [])],
        "tconst string, languages array<string>",
    )
    success = spark.createDataFrame([("t1",), ("t2",), ("t3",), ("t4",)], "tconst string")
    principals = spark.createDataFrame(
        [("t1", "n1", "actor"), ("t2", "n1", "actor"), ("t3", "n1", "actor"),
         ("t4", "n1", "actor"), ("t1", "n2", "director")],
        "tconst string, nconst string, category string",
    )
    actors = multilingual_actors(success, original_language(film_languages), principals)
    row = actors.first()
    assert actors.count() == 1
    assert (row.nconst, row.languages, row.language_count) == (
        "n1", ["English", "French", "Japanese"], 3)
    assert row.successful_films == 3
    assert actors.where(F.col("language_count") >= 2).count() == 1
