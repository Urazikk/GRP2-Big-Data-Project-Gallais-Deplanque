from imdb_project.preparation.cleaning import (
    clean_crew,
    clean_episodes,
    clean_names,
    clean_principals,
    clean_titles,
)

BASICS = ("tconst string, titleType string, primaryTitle string, originalTitle string, "
          "isAdult int, startYear int, endYear int, runtimeMinutes int, genres string")


def titles(spark):
    return clean_titles(spark.createDataFrame(
        [("t1", "movie", "A", "A", 0, 2000, None, 90, "Drama,Comedy"),
         ("t2", "movie", "B", "B", 1, 2030, None, 51420, None),
         ("t3", "tvSeries", "C", "C", 0, 2010, 2005, 0, "Drama")], BASICS),
        max_runtime=600, current_year=2026)


def test_clean_titles(spark):
    rows = {r.tconst: r for r in titles(spark).collect()}
    assert rows["t1"].runtimeMinutes == 90 and rows["t1"].genres == ["Drama", "Comedy"]
    assert rows["t1"].dq_flags == [] and rows["t1"].isAdult is False
    assert rows["t2"].runtimeMinutes is None and rows["t2"].runtimeMinutes_raw == 51420
    assert set(rows["t2"].dq_flags) == {"runtime_over_max", "start_after_current_year"}
    assert rows["t2"].genres == []
    assert set(rows["t3"].dq_flags) == {"runtime_not_positive", "end_before_start"}


def names_df(spark):
    return spark.createDataFrame(
        [("n1", "Aeschylus", 525, 456, "writer", "t1"),
         ("n2", "Old Alive", 1850, None, "actor", "t1,t9"),
         ("n3", "Normal", 1970, None, None, None)],
        "nconst string, primaryName string, birthYear int, deathYear int, "
        "primaryProfession string, knownForTitles string")


def test_clean_names_flags_and_known_for(spark):
    rows = {r.nconst: r for r in clean_names(names_df(spark), titles(spark).select("tconst"))
            .collect()}
    assert set(rows["n1"].dq_flags) == {"death_before_birth", "birth_before_1000"}
    assert rows["n2"].knownForTitles == ["t1"]
    assert set(rows["n2"].dq_flags) == {"alive_born_before_1900", "unknown_known_for_title"}
    assert rows["n3"].dq_flags == [] and rows["n3"].knownForTitles == []


def test_clean_principals_quarantine_and_flags(spark):
    names = clean_names(names_df(spark), titles(spark).select("tconst"))
    principals = spark.createDataFrame(
        [("t1", 1, "n1", "writer", None, None),
         ("t1", 2, "n3", "actor", None, '["Bob"]'),
         ("t1", 3, "n404", "actor", None, None),
         ("t404", 1, "n3", "actor", None, None)],
        "tconst string, ordering int, nconst string, category string, job string, "
        "characters string")
    kept, q = clean_principals(principals, titles(spark), names)
    rows = {(r.tconst, r.nconst): r for r in kept.collect()}
    assert set(rows) == {("t1", "n1"), ("t1", "n3")}
    assert "died_before_release" in rows[("t1", "n1")].dq_flags
    assert rows[("t1", "n3")].characters == ["Bob"]
    assert sorted(r.reason for r in q.collect()) == ["nconst missing in name.basics",
                                                     "tconst missing in title.basics"]


def test_clean_crew_and_episodes(spark):
    names = clean_names(names_df(spark), titles(spark).select("tconst"))
    crew = spark.createDataFrame([("t1", "n1,n404", None), ("t404", "n1", "n3")],
                                 "tconst string, directors string, writers string")
    directors, q = clean_crew(crew, titles(spark), names, "directors")
    assert [(r.tconst, r.nconst) for r in directors.collect()] == [("t1", "n1")]
    assert q.count() == 2
    episodes = spark.createDataFrame([("t1", "t3", 1, 1), ("t2", "t3", None, None),
                                      ("t9", "t3", 1, 2)],
                                     "tconst string, parentTconst string, seasonNumber int, "
                                     "episodeNumber int")
    kept, q = clean_episodes(episodes, titles(spark))
    flags = {r.tconst: r.dq_flags for r in kept.collect()}
    assert flags == {"t1": [], "t2": ["no_season_or_episode_number"]}
    assert q.count() == 1
