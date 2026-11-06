import datetime
from urllib.parse import unquote

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
from imdb_project.enrichment.wikipedia import (
    WikipediaClient,
    film_candidates,
    parse_page,
    person_candidates,
)
from imdb_project.exploration.languages import multilingual_actors, original_language

FILM_HTML = """<html><body>
<section data-mw-section-id="0">
<table class="infobox"><tr><th>Directed by</th><td>X</td></tr>
<tr><th>Languages</th><td><a>French</a><sup>[1]</sup><br/><a>English</a> sign</td></tr></table>
<p>Lead text<sup>[2]</sup> about the film.</p></section>
<section data-mw-section-id="1"><h2 id="Plot">Plot</h2><p>First part.</p>
<section data-mw-section-id="2"><h3 id="Part_two">Part two</h3><p>Second part.</p></section>
</section>
<section data-mw-section-id="2"><h2 id="External_links">External links</h2>
<p><a href="https://www.imdb.com/title/tt0000001/">IMDb</a></p></section>
</body></html>"""


def test_parse_page():
    page = parse_page(FILM_HTML)
    assert page["imdb_ids"] == ["tt0000001"]
    assert page["languages"] == ["French", "English sign"]
    assert page["plot"] == "First part.\nSecond part."
    assert page["plot_section"] == "Plot"
    assert page["lead"].startswith("Lead text")


def test_candidates():
    assert film_candidates("Amélie", "Le fabuleux destin", 2001)[:3] == [
        "Amélie (2001 film)", "Amélie (film)", "Amélie"]
    assert person_candidates("Jane Doe", "actress") == [
        "Jane Doe", "Jane Doe (actress)", "Jane Doe (actor)"]


class FakeResponse:
    def __init__(self, status, text="", data=None):
        self.status_code, self.text, self._data, self.headers = status, text, data, {}

    def json(self):
        return self._data


class FakeSession:
    """Answers like the REST API: one film page under 'Movie (2001 film)'."""

    def __init__(self):
        self.headers, self.calls = {}, []

    def get(self, url, timeout):
        self.calls.append(url)
        url = unquote(url)
        if url.endswith("summary/Movie_(2001_film)"):
            return FakeResponse(200, data={"type": "standard", "title": "Movie (2001 film)"})
        if url.endswith("summary/Movie_(film)"):
            return FakeResponse(200, data={"type": "disambiguation", "title": "Movie (film)"})
        if url.endswith("html/Movie_(2001_film)"):
            return FakeResponse(200, text=FILM_HTML)
        return FakeResponse(404)


def test_find_checks_imdb_id_and_caches(tmp_path):
    session = FakeSession()
    client = WikipediaClient(tmp_path / "cache.sqlite", min_interval=0, session=session)
    title, page, fetched_at, note = client.find(film_candidates("Movie", None, 2001),
                                                "tt0000001")
    assert title == "Movie (2001 film)" and note is None and fetched_at
    calls = len(session.calls)
    client.find(film_candidates("Movie", None, 2001), "tt0000001")
    assert len(session.calls) == calls  # second lookup served from the cache

    title, page, _, note = client.find(film_candidates("Movie", None, 2001), "tt9999999")
    assert title is None and "no English Wikipedia page linking to tt9999999" in note


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
