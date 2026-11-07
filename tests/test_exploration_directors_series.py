from imdb_project.exploration.directors import directed_films, one_hit_directors
from imdb_project.exploration.series import long_series, worst_last_best_first

FILMS = "tconst string, primaryTitle string, startYear int"
RATINGS = "tconst string, averageRating double, numVotes int"


def test_one_hit_directors(spark):
    films = spark.createDataFrame(
        [(f"t{i}", f"F{i}", 2000 + i) for i in range(1, 10)], FILMS
    )
    crew = spark.createDataFrame(
        [("t1", "nA"), ("t2", "nA"), ("t3", "nA"),        # A: hit + 2 bad -> kept
         ("t4", "nB"), ("t5", "nB"),                      # B: hit + 1 bad -> too few
         ("t6", "nC,nD"), ("t7", "nC"), ("t8", "nC"),     # C: hit + avg 6.5 -> too high
         ("t9", "nD")],                                   # D: t9 has too few votes
        "tconst string, directors string",
    )
    ratings = spark.createDataFrame(
        [("t1", 8.5, 500), ("t2", 5.0, 500), ("t3", 6.0, 500),
         ("t4", 9.0, 500), ("t5", 4.0, 500),
         ("t6", 8.0, 500), ("t7", 6.0, 500), ("t8", 7.0, 500),
         ("t9", 3.0, 5)],
        RATINGS,
    )
    rows = one_hit_directors(directed_films(films, crew, ratings, min_votes=100)).collect()
    assert [(r.nconst, r.hit_tconst, r.other_films, r.others_avg) for r in rows] == [
        ("nA", "t1", 2, 5.5)
    ]


def _series_data(spark, ratings_by_season):
    basics = spark.createDataFrame(
        [("s1", "tvSeries", "Show", 2010)],
        "tconst string, titleType string, primaryTitle string, startYear int",
    )
    episodes, ratings = [], []
    for season, values in ratings_by_season.items():
        for i in range(10):
            tconst = f"e{season}_{i}"
            episodes.append((tconst, "s1", season, i + 1))
            ratings.append((tconst, values[i] if i < len(values) else 7.0, 50))
    episodes = spark.createDataFrame(
        episodes, "tconst string, parentTconst string, seasonNumber int, episodeNumber int"
    )
    return basics, episodes, spark.createDataFrame(ratings, RATINGS)


def test_series_worst_last_best_first(spark):
    basics, episodes, ratings = _series_data(spark, {1: [9.5], 2: [8.0], 3: [5.0]})
    series = long_series(basics, episodes)
    rows = worst_last_best_first(series, episodes, ratings).collect()
    assert [(r.tconst, r.last_season, r.best_first, r.worst_last) for r in rows] == [
        ("s1", 3, 9.5, 5.0)
    ]


def test_series_tie_disqualifies(spark):
    basics, episodes, ratings = _series_data(spark, {1: [9.5, 5.0], 2: [8.0], 3: [5.0]})
    series = long_series(basics, episodes)
    assert worst_last_best_first(series, episodes, ratings).count() == 0


def test_series_needs_three_long_seasons(spark):
    basics, episodes, ratings = _series_data(spark, {1: [9.5], 2: [5.0]})
    assert long_series(basics, episodes).count() == 0
