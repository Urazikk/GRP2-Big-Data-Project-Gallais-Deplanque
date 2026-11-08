"""Shared definitions for the exploration questions."""
import csv

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from imdb_project.config import CLEAN_DIR
from imdb_project.imdb_io import read_imdb

# A feature film runs more than 40 minutes (Academy of Motion Picture Arts and Sciences rule)
MIN_FEATURE_RUNTIME = 40


def feature_films(basics: DataFrame, min_runtime: int = MIN_FEATURE_RUNTIME) -> DataFrame:
    """Movies whose runtime is strictly above min_runtime minutes."""
    return basics.where(
        (F.col("titleType") == "movie") & (F.col("runtimeMinutes") > min_runtime)
    )


def explode_genres(films: DataFrame) -> DataFrame:
    """One row per (film, genre); films without genre are dropped.

    IMDb lists the genres of a title in alphabetical order, so there is no main genre:
    a film counts in each of its genres.
    """
    return films.where(F.col("genres").isNotNull()).withColumn(
        "genre", F.explode(F.split("genres", ","))
    )


def to_markdown(df: DataFrame) -> str:
    """Render a small DataFrame as a markdown table."""
    rows = df.collect()
    lines = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    for r in rows:
        lines.append("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
    return "\n".join(lines) + "\n"


def write_csv(df: DataFrame, path) -> None:
    """Write a small DataFrame to a single CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(df.columns)
        writer.writerows(df.toLocalIterator())


def _join_list(col: str) -> Column:
    """array -> comma separated string, empty array -> null (raw IMDb layout)."""
    return F.when(F.size(col) > 0, F.array_join(col, ","))


def clean_to_raw_layout(spark, table: str, clean_dir) -> DataFrame:
    """A cleaned table (imdb_project.preparation.cleaning) in the layout of the raw file."""
    read = lambda name: spark.read.parquet(str(clean_dir / name))  # noqa: E731
    if table == "title.basics":
        return read("title_basics").select(
            "tconst", "titleType", "primaryTitle", "originalTitle",
            F.col("isAdult").cast("int").alias("isAdult"), "startYear", "endYear",
            "runtimeMinutes", _join_list("genres").alias("genres"))
    if table == "name.basics":
        return read("name_basics").select(
            "nconst", "primaryName", "birthYear", "deathYear",
            _join_list("primaryProfession").alias("primaryProfession"),
            _join_list("knownForTitles").alias("knownForTitles"))
    if table == "title.crew":
        lists = [read(f"title_{c}").groupBy("tconst")
                 .agg(F.array_join(F.array_sort(F.collect_list("nconst")), ",").alias(c))
                 for c in ("directors", "writers")]
        return lists[0].join(lists[1], "tconst", "full")
    if table == "title.principals":
        return read("title_principals").select("tconst", "ordering", "nconst", "category",
                                               "job")
    if table == "title.episode":
        return read("title_episode").select("tconst", "parentTconst", "seasonNumber",
                                            "episodeNumber")
    if table == "title.ratings":
        return read("title_ratings").select("tconst", "averageRating", "numVotes")
    raise ValueError(f"no cleaned version of {table}")


def read_table(spark, table: str) -> DataFrame:
    """IMDb table used by the analyses: the cleaned table when data/clean exists
    (run imdb_project.preparation.cleaning first), the raw file otherwise."""
    if (CLEAN_DIR / "title_basics").exists():
        return clean_to_raw_layout(spark, table, CLEAN_DIR)
    return read_imdb(spark, table, typed=True)
