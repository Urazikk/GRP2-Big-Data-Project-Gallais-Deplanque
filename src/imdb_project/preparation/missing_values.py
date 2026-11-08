"""Percentage of null, missing or empty values per column of each IMDb table.

The tables are read with typed=False: every column is a string and the IMDb null marker "\\N"
is kept as it is, so the three cases can be counted separately:

- null_marker: the value is "\\N" (how IMDb writes a missing value)
- spark_null: Spark returned null (a line with fewer fields than the header)
- empty: empty string or only whitespace

Usage: python -m imdb_project.preparation.missing_values
"""
from functools import reduce

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from imdb_project.config import IMDB_TABLES, RESULTS_DIR
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

IMDB_NULL = "\\N"

PROFILE_SCHEMA = (
    "table string, column string, total_rows long, null_marker long, spark_null long, "
    "empty long, missing long, missing_pct double"
)


def missing_profile(df: DataFrame, table: str) -> DataFrame:
    """One row per column of df, computed in a single pass over the data."""
    aggs = [F.count(F.lit(1)).alias("__total")]
    for c in df.columns:
        col = F.col(c)
        aggs += [
            F.sum((col == IMDB_NULL).cast("long")).alias(f"{c}__marker"),
            F.sum(col.isNull().cast("long")).alias(f"{c}__null"),
            F.sum((F.trim(col) == "").cast("long")).alias(f"{c}__empty"),
        ]
    row = df.agg(*aggs).first()
    total = row["__total"]
    rows = []
    for c in df.columns:
        marker, null, empty = (row[f"{c}__{k}"] or 0 for k in ("marker", "null", "empty"))
        missing = marker + null + empty
        pct = round(100.0 * missing / total, 2) if total else 0.0
        rows.append((table, c, total, marker, null, empty, missing, pct))
    return df.sparkSession.createDataFrame(rows, PROFILE_SCHEMA)


def profile_all(spark, tables=IMDB_TABLES) -> DataFrame:
    profiles = [missing_profile(read_imdb(spark, t, typed=False), t) for t in tables]
    return reduce(DataFrame.unionByName, profiles)


def to_markdown(df: DataFrame) -> str:
    rows = df.collect()
    lines = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    for r in rows:
        lines.append("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
    return "\n".join(lines) + "\n"


def main():
    spark = get_spark("imdb-missing-values", driver_memory="6g")
    profile = profile_all(spark).cache()
    by_column = profile.orderBy("table", "column")
    top5 = profile.orderBy(F.desc("missing_pct"), "table", "column").limit(5)

    out = RESULTS_DIR / "preparation"
    out.mkdir(parents=True, exist_ok=True)
    (out / "missing_per_column.md").write_text(to_markdown(by_column))
    (out / "top5_missing_columns.md").write_text(to_markdown(top5))
    by_column.show(100, truncate=False)
    top5.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
