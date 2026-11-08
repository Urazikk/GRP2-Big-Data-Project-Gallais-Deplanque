from imdb_project.preparation.missing_values import missing_profile


def test_missing_profile_counts_each_case(spark):
    df = spark.createDataFrame(
        [("tt1", "\\N"), ("tt2", ""), ("tt3", "  "), ("tt4", None), ("tt5", "Drama")],
        "tconst string, genres string",
    )
    rows = {r.column: r for r in missing_profile(df, "title.basics").collect()}
    genres = rows["genres"]
    assert genres.total_rows == 5
    assert (genres.null_marker, genres.empty, genres.spark_null) == (1, 2, 1)
    assert genres.missing == 4
    assert genres.missing_pct == 80.0
    assert rows["tconst"].missing == 0
