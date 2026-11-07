"""Shared definitions for the exploration questions."""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

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
