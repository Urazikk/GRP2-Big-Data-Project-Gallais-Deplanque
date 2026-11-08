import json

from pyspark.sql import functions as F

from imdb_project.open_question.remakes_analysis import compare, confirmed_pairs, shared_principals
from imdb_project.open_question.remakes_collect import IntroClient, check_remake, is_remake_of
from imdb_project.open_question.remakes_scope import candidate_pairs, rated_films, title_key


def test_title_key_ignores_case_and_punctuation(spark):
    df = spark.createDataFrame([("Ocean's  Eleven!",), ("OCEAN S ELEVEN",), ("Up!",)], "t string")
    keys = [r.k for r in df.select(title_key(F.col("t")).alias("k")).collect()]
    assert keys == ["ocean s eleven", "ocean s eleven", "up"]


def test_candidate_pairs_need_same_title_votes_and_gap(spark):
    films = spark.createDataFrame(
        [("t1", "movie", "Heat", "Heat", 1972, 100, "Drama"),
         ("t2", "movie", "Heat", "Heat", 1995, 170, "Crime"),
         ("t3", "movie", "Heat", "Heat", 1980, 90, "Drama"),   # gap 8 with t1, 15 with t2
         ("t4", "movie", "Heat", "Heat", 2010, 90, "Drama")],  # too few votes
        "tconst string, titleType string, primaryTitle string, originalTitle string, "
        "startYear int, runtimeMinutes int, genres string",
    )
    ratings = spark.createDataFrame(
        [("t1", 6.1, 2000), ("t2", 8.3, 900000), ("t3", 5.0, 1500), ("t4", 5.0, 10)],
        "tconst string, averageRating double, numVotes int",
    )
    pairs = candidate_pairs(rated_films(films, ratings, min_votes=1000), min_gap=10).collect()
    assert sorted((p.original_tconst, p.remake_tconst) for p in pairs) == [
        ("t1", "t2"), ("t3", "t2")]


def test_is_remake_of_rules():
    assert is_remake_of("It is a remake of the 1935 film, starring Irene Dunne.", 1935)[0]
    # a later remake of this film is not evidence that this film is a remake
    assert not is_remake_of("State Fair was remade in 1962, starring Pat Boone.", 1933)[0]
    # negation
    assert not is_remake_of("Although named after the 1914 serial, it is not a remake of it.",
                            1914)[0]
    # remake of another version: the year must be in the same sentence
    ok, note = is_remake_of("Heat is a 1995 film. It is a remake of L.A. Takedown (1989).", 1972)
    assert not ok and "1972" in note
    assert not is_remake_of("", 1972)[0]


class FakeClient(IntroClient):
    """IntroClient answering from a dict instead of the network."""

    def __init__(self, tmp_path, pages):
        super().__init__(cache_path=tmp_path / "cache.sqlite", min_interval=0)
        self.pages = pages

    def _get(self, params):
        titles = params["titles"].split("|")
        return {"query": {"pages": [
            {"title": t, **self.pages[t]} if t in self.pages else {"title": t, "missing": True}
            for t in titles]}}


def test_check_remake_requires_imdb_link(tmp_path):
    pages = {
        "Scarface (1983 film)": {
            "extract": "Scarface is a 1983 film. It is a remake of the 1932 film of the same name.",
            "extlinks": [{"url": "https://www.imdb.com/title/tt0086250/"}]},
        "Heat (1995 film)": {
            "extract": "It is a remake of the 1972 film.",
            "extlinks": [{"url": "https://www.imdb.com/title/tt9999999/"}]},  # wrong film
    }
    client = FakeClient(tmp_path, pages)
    scarface = {"remake_tconst": "tt0086250", "remake_title": "Scarface",
                "remake_original_title": "Scarface", "remake_year": 1983}
    heat = {"remake_tconst": "tt0113277", "remake_title": "Heat",
            "remake_original_title": "Heat", "remake_year": 1995}
    client.prefetch(["Scarface (1983 film)", "Scarface (film)", "Scarface",
                     "Heat (1995 film)", "Heat (film)", "Heat"])
    rec = check_remake(client, scarface, [{"original_tconst": "tt0023427", "original_year": 1932}])
    assert rec[0]["confirmed"] and rec[0]["source_url"].endswith("Scarface_(1983_film)")
    rec = check_remake(client, heat, [{"original_tconst": "t1", "original_year": 1972}])
    assert not rec[0]["confirmed"] and rec[0]["note"].startswith("no English Wikipedia page")
    json.dumps(rec)  # records must be serialisable


def test_comparison_and_shared_people(spark):
    candidates = spark.createDataFrame(
        [("o1", "A", 1950, "r1", "A", "A", 1990), ("o2", "B", 1960, "r2", "B", "B", 2000)],
        "original_tconst string, original_title string, original_year int, remake_tconst string, "
        "remake_title string, remake_original_title string, remake_year int",
    )
    checks = spark.createDataFrame(
        [("o1", "r1", "A", "u1", "2026-11-07T10:00:00+00:00", True, "remake of 1950", None),
         ("o2", "r2", "B", "u2", "2026-11-07T10:00:00+00:00", True, "remake of 1960", None)],
        "original_tconst string, remake_tconst string, page_title string, source_url string, "
        "retrieved_at string, confirmed boolean, evidence string, note string",
    )
    ratings = spark.createDataFrame(
        [("o1", 8.0, 1000), ("r1", 6.0, 4000), ("o2", 6.0, 1000), ("r2", 7.0, 500)],
        "tconst string, averageRating double, numVotes int",
    )
    basics = spark.createDataFrame([("r1", "Drama"), ("r2", "Comedy,Drama")],
                                   "tconst string, genres string")
    principals = spark.createDataFrame([("o1", "p1"), ("r1", "p1"), ("o2", "p2"), ("r2", "p3")],
                                       "tconst string, nconst string")
    pairs = shared_principals(confirmed_pairs(candidates, checks, ratings, basics), principals)
    overall = compare(pairs).collect()[0]
    assert overall.pairs == 2 and overall.avg_diff == -0.5
    assert overall.pct_remake_better == 50.0 and overall.pct_remake_more_votes == 50.0
    shared = {r.remake_tconst: r.shared_people for r in pairs.collect()}
    assert shared == {"r1": 1, "r2": 0}
