from imdb_project.exploration.careers import acted_films, early_peak_actors
from imdb_project.exploration.multi_talented import (
    film_roles,
    multi_talented,
    performance_by_person,
    summary_by_combo,
)

FILMS = "tconst string, primaryTitle string, startYear int"
RATINGS = "tconst string, averageRating double, numVotes int"
PRINCIPALS = "tconst string, nconst string, category string"


def _career(spark, ratings_by_year):
    films, principals, ratings = [], [], []
    for i, (year, rating) in enumerate(ratings_by_year):
        films.append((f"t{i}", f"F{i}", year))
        principals.append((f"t{i}", "n1", "actor"))
        ratings.append((f"t{i}", rating, 500))
    return (spark.createDataFrame(films, FILMS), spark.createDataFrame(principals, PRINCIPALS),
            spark.createDataFrame(ratings, RATINGS))


def test_early_peak_actor(spark):
    years = [2000 + 2 * i for i in range(16)]           # 30-year career, 16 films
    rating = [9.0] + [8.0] * 4 + [6.0] * 11
    acted = acted_films(*_career(spark, list(zip(years, rating))), min_votes=100)
    rows = early_peak_actors(acted, min_films=15, min_years=20).collect()
    assert len(rows) == 1
    assert (rows[0].best_year, rows[0].best_rating) == (2000, 9.0)
    assert rows[0].early_avg > rows[0].late_avg


def test_late_peak_actor_excluded(spark):
    years = [2000 + 2 * i for i in range(16)]
    rating = [6.0] * 15 + [9.0]
    acted = acted_films(*_career(spark, list(zip(years, rating))), min_votes=100)
    assert early_peak_actors(acted, min_films=15, min_years=20).count() == 0


def test_short_career_excluded(spark):
    years = [2000 + i for i in range(16)]               # 15-year span
    acted = acted_films(*_career(spark, [(y, 9.0 if y == 2000 else 6.0) for y in years]))
    assert early_peak_actors(acted, min_films=15, min_years=20).count() == 0


def test_multi_talented_roles_and_gap(spark):
    films = spark.createDataFrame([(f"t{i}", f"F{i}", 2000) for i in range(6)], FILMS)
    # n1 acts in t0-t5 and directs t0-t2 (multi-role on t0-t2), n2 only acts
    principals = spark.createDataFrame(
        [(f"t{i}", "n1", "actor") for i in range(6)] + [("t0", "n2", "actress")], PRINCIPALS
    )
    crew = spark.createDataFrame(
        [("t0", "n1", None), ("t1", "n1", None), ("t2", "n1", "n3")],
        "tconst string, directors string, writers string",
    )
    ratings = spark.createDataFrame(
        [("t0", 8.0, 500), ("t1", 8.0, 500), ("t2", 8.0, 500),
         ("t3", 6.0, 500), ("t4", 6.0, 500), ("t5", 6.0, 500)],
        RATINGS,
    )
    roles = film_roles(films, principals, crew, ratings, min_votes=100)
    talented = multi_talented(roles, min_films=3).collect()
    assert [(r.nconst, r.talent_combo) for r in talented] == [("n1", "act+direct")]

    perf = performance_by_person(roles, multi_talented(roles, min_films=3)).collect()[0]
    assert (perf.multi_films, perf.single_films) == (3, 3)
    assert perf.rating_gap == 2.0
    summary = summary_by_combo(performance_by_person(roles, multi_talented(roles, 3))).collect()
    assert summary[0].pct_better_multi == 100.0
