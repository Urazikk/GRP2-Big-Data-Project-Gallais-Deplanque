from imdb_project.exploration.common import clean_to_raw_layout, explode_genres


def test_clean_tables_in_raw_layout(spark, tmp_path):
    spark.createDataFrame(
        [("t1", "movie", "A", "A", True, 2000, None, 90, None, ["Drama", "Comedy"], []),
         ("t2", "movie", "B", "B", False, 2001, None, None, 700, [], ["runtime_over_max"])],
        "tconst string, titleType string, primaryTitle string, originalTitle string, "
        "isAdult boolean, startYear int, endYear int, runtimeMinutes int, "
        "runtimeMinutes_raw int, genres array<string>, dq_flags array<string>",
    ).write.parquet(str(tmp_path / "title_basics"))
    for name, rows in (("title_directors", [("t1", "n2"), ("t1", "n1")]),
                       ("title_writers", [("t2", "n3")])):
        spark.createDataFrame(rows, "tconst string, nconst string").write.parquet(
            str(tmp_path / name))

    basics = clean_to_raw_layout(spark, "title.basics", tmp_path)
    rows = {r.tconst: r for r in basics.collect()}
    assert rows["t1"].genres == "Drama,Comedy" and rows["t1"].isAdult == 1
    assert rows["t2"].genres is None and rows["t2"].runtimeMinutes is None
    assert explode_genres(basics).count() == 2

    crew = {r.tconst: (r.directors, r.writers)
            for r in clean_to_raw_layout(spark, "title.crew", tmp_path).collect()}
    assert crew == {"t1": ("n1,n2", None), "t2": (None, "n3")}
