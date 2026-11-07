"""Open question, step 1: candidate (original, remake) pairs of feature films, in Spark.

Two rated feature films are a candidate pair when their original titles are the same after
normalisation (lower case, punctuation removed) and the second one was released at least
MIN_GAP years after the first. Both films need at least MIN_VOTES votes. A title match alone
gives many false positives (two unrelated films called "Heat"), so every candidate is checked
on Wikipedia by imdb_project.open_question.remakes_collect.

All limits are parameters; the same code runs on the full dataset with --min-votes 0.

Usage: python -m imdb_project.open_question.remakes_scope [--min-votes 1000] [--min-gap 10]
"""
import argparse
import json

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from imdb_project.config import DATA_DIR
from imdb_project.exploration.common import feature_films
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

REMAKES_DIR = DATA_DIR / "open_question"
CANDIDATES_PATH = REMAKES_DIR / "candidates.jsonl"
MIN_VOTES = 1000
MIN_GAP = 10
MIN_KEY_LENGTH = 2


def title_key(col: Column) -> Column:
    """Normalised title: lower case, every run of non letters / digits replaced by a space."""
    return F.trim(F.regexp_replace(F.lower(col), r"[^\p{L}\p{N}]+", " "))


def rated_films(films: DataFrame, ratings: DataFrame, min_votes: int = MIN_VOTES) -> DataFrame:
    """Feature films with a release year, a usable title key and at least min_votes votes."""
    return (
        films.where(F.col("startYear").isNotNull())
        .join(ratings.where(F.col("numVotes") >= min_votes), "tconst")
        .withColumn("key", title_key(F.col("originalTitle")))
        .where(F.length("key") >= MIN_KEY_LENGTH)
        .select("tconst", "primaryTitle", "originalTitle", "startYear", "key")
    )


def candidate_pairs(rated: DataFrame, min_gap: int = MIN_GAP) -> DataFrame:
    """One row per (original, remake): same title key, remake at least min_gap years later."""
    o, r = rated.alias("o"), rated.alias("r")
    return (
        o.join(r, (F.col("o.key") == F.col("r.key"))
               & (F.col("r.startYear") >= F.col("o.startYear") + min_gap))
        .select(
            F.col("o.tconst").alias("original_tconst"),
            F.col("o.primaryTitle").alias("original_title"),
            F.col("o.startYear").alias("original_year"),
            F.col("r.tconst").alias("remake_tconst"),
            F.col("r.primaryTitle").alias("remake_title"),
            F.col("r.originalTitle").alias("remake_original_title"),
            F.col("r.startYear").alias("remake_year"),
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-votes", type=int, default=MIN_VOTES)
    parser.add_argument("--min-gap", type=int, default=MIN_GAP)
    args = parser.parse_args()

    spark = get_spark("imdb-remakes-scope")
    films = feature_films(read_imdb(spark, "title.basics"))
    pairs = candidate_pairs(
        rated_films(films, read_imdb(spark, "title.ratings"), args.min_votes), args.min_gap
    ).orderBy("remake_tconst", "original_year")

    REMAKES_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(CANDIDATES_PATH, "w", encoding="utf-8") as f:
        for row in pairs.toLocalIterator():
            f.write(json.dumps(row.asDict(), ensure_ascii=False) + "\n")
            n += 1
    print(f"{n} candidate pairs written to {CANDIDATES_PATH}")
    spark.stop()


if __name__ == "__main__":
    main()
