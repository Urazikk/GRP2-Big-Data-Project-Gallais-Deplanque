"""Feature films whose runtime is notably different from the average of their genre.

A runtime is notable when it falls outside the Tukey fences of its genre, computed on
log(runtime) because runtimes are right-skewed: below exp(Q1 - k * IQR) or above
exp(Q3 + k * IQR), with Q1, Q3 and IQR taken on the log scale (k = 1.5 by default).

Usage: python -m imdb_project.exploration.runtime_outliers
"""
import csv

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from imdb_project.config import DATA_DIR, RESULTS_DIR
from imdb_project.exploration.common import explode_genres, feature_films, to_markdown
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

IQR_FACTOR = 1.5
MIN_GENRE_SIZE = 30


def genre_runtime_stats(by_genre: DataFrame, k: float = IQR_FACTOR,
                        min_size: int = MIN_GENRE_SIZE) -> DataFrame:
    """Runtime statistics and Tukey fences (log scale) per genre.

    Genres with fewer than min_size films are dropped. Fences are given in minutes.
    """
    stats = by_genre.groupBy("genre").agg(
        F.count("*").alias("films"),
        F.round(F.avg("runtimeMinutes"), 1).alias("mean"),
        F.round(F.stddev("runtimeMinutes"), 1).alias("std"),
        F.percentile_approx("runtimeMinutes", 0.5, 10000).alias("median"),
        F.percentile_approx(F.log("runtimeMinutes"), [0.25, 0.75], 10000).alias("lq"),
    )
    log_iqr = F.col("lq")[1] - F.col("lq")[0]
    return stats.where(F.col("films") >= min_size).select(
        "genre", "films", "mean", "std", "median",
        F.round(F.exp(F.col("lq")[0] - k * log_iqr), 1).alias("low_fence"),
        F.round(F.exp(F.col("lq")[1] + k * log_iqr), 1).alias("high_fence"),
    )


def runtime_outliers(by_genre: DataFrame, stats: DataFrame) -> DataFrame:
    """Films outside the fences of their genre, with their gap to the genre mean."""
    joined = by_genre.join(stats.select("genre", "mean", "low_fence", "high_fence"), "genre")
    return (
        joined.where(
            (F.col("runtimeMinutes") < F.col("low_fence"))
            | (F.col("runtimeMinutes") > F.col("high_fence"))
        )
        .withColumn(
            "direction",
            F.when(F.col("runtimeMinutes") > F.col("high_fence"), "longer").otherwise("shorter"),
        )
        .withColumn("gap_to_mean", F.round(F.col("runtimeMinutes") - F.col("mean"), 1))
        .select("genre", "tconst", "primaryTitle", "startYear", "runtimeMinutes",
                "mean", "gap_to_mean", "direction")
    )


def summary(stats: DataFrame, outliers: DataFrame) -> DataFrame:
    """Per genre: statistics, fences and number of outliers in each direction."""
    counts = outliers.groupBy("genre").agg(
        F.sum((F.col("direction") == "shorter").cast("int")).alias("shorter"),
        F.sum((F.col("direction") == "longer").cast("int")).alias("longer"),
    )
    return (
        stats.join(counts, "genre", "left")
        .fillna(0, ["shorter", "longer"])
        .withColumn("outlier_pct",
                    F.round(100 * (F.col("shorter") + F.col("longer")) / F.col("films"), 2))
        .orderBy(F.desc("films"))
    )


def write_csv(df: DataFrame, path) -> None:
    """Write a small DataFrame to a single CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(df.columns)
        writer.writerows(df.toLocalIterator())


def main():
    spark = get_spark("imdb-runtime-outliers")
    films = feature_films(read_imdb(spark, "title.basics"))
    by_genre = explode_genres(films).cache()
    stats = genre_runtime_stats(by_genre).cache()
    outliers = runtime_outliers(by_genre, stats).cache()
    table = summary(stats, outliers)

    out = RESULTS_DIR / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "runtime_outliers_by_genre.md").write_text(to_markdown(table))
    extremes = outliers.orderBy(F.desc(F.abs("gap_to_mean"))).limit(20)
    (out / "runtime_outliers_top20.md").write_text(to_markdown(extremes))
    # Full list (tens of thousands of rows) kept out of git, under data/
    full = DATA_DIR / "exploration"
    full.mkdir(parents=True, exist_ok=True)
    write_csv(outliers.orderBy("genre", "runtimeMinutes"), full / "runtime_outliers.csv")
    table.show(40, truncate=False)
    print(f"{outliers.count()} (film, genre) outliers, "
          f"{outliers.select('tconst').distinct().count()} distinct films")
    spark.stop()


if __name__ == "__main__":
    main()
