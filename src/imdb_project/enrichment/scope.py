"""Select the films and people to enrich, and write them as JSON lines for the collector.

Films: the top N feature films per (year, genre) by IMDb votes, over a year range.
People: the principals of those films in credit order, up to MAX_PRINCIPALS each, so
that at least three biographies can be found when some are missing.

Films with a successful rating (used by the languages exploration question) are added
to the film list with need_people = false: only their page is fetched, not their cast.

All limits are parameters, the same code runs on the full dataset with --top-n 0.

Usage: python -m imdb_project.enrichment.scope [--first-year 1980] [--last-year 2025]
       [--top-n 10]
"""
import argparse
import json

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from imdb_project.enrichment.collect import SCOPE_DIR
from imdb_project.exploration.common import explode_genres, feature_films
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

MAX_PRINCIPALS = 5
SUCCESS_RATING = 7.0
SUCCESS_VOTES = 10000


def top_films(films: DataFrame, ratings: DataFrame, first_year: int, last_year: int,
              top_n: int) -> DataFrame:
    """Top n feature films per (year, genre) by votes, one row per film (top_n <= 0: all)."""
    rated = (
        explode_genres(films.where(F.col("startYear").between(first_year, last_year)))
        .join(ratings, "tconst")
    )
    if top_n > 0:
        w = Window.partitionBy("startYear", "genre").orderBy(F.desc("numVotes"), "tconst")
        rated = rated.withColumn("rank", F.row_number().over(w)).where(F.col("rank") <= top_n)
    return rated.groupBy("tconst").agg(F.collect_set("genre").alias("top_genres"))


def successful_films(films: DataFrame, ratings: DataFrame, min_rating: float = SUCCESS_RATING,
                     min_votes: int = SUCCESS_VOTES) -> DataFrame:
    """Feature films rated >= min_rating with at least min_votes votes."""
    return films.join(ratings, "tconst").where(
        (F.col("averageRating") >= min_rating) & (F.col("numVotes") >= min_votes)
    ).select("tconst")


def film_scope(films: DataFrame, top: DataFrame, success: DataFrame) -> DataFrame:
    """Films to fetch, with titles and year, and whether their principals are needed."""
    wanted = (
        top.select("tconst", F.lit(True).alias("need_people"))
        .unionByName(success.select("tconst", F.lit(False).alias("need_people")))
        .groupBy("tconst").agg(F.max("need_people").alias("need_people"))
    )
    return films.select("tconst", "primaryTitle", "originalTitle", "startYear").join(
        wanted, "tconst"
    )


def people_scope(top: DataFrame, principals: DataFrame, names: DataFrame,
                 max_principals: int = MAX_PRINCIPALS) -> DataFrame:
    """Principals of the top films in credit order (ordering <= max_principals)."""
    return (
        principals.join(top.select("tconst"), "tconst")
        .where(F.col("ordering") <= max_principals)
        .join(names.select("nconst", "primaryName", "primaryProfession"), "nconst", "left")
        .select("tconst", "ordering", "nconst", "category", "primaryName", "primaryProfession")
    )


def write_jsonl(df: DataFrame, path) -> int:
    """Write a DataFrame as one JSON object per line, return the number of lines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for row in df.toLocalIterator():
            f.write(json.dumps(row.asDict(recursive=True), ensure_ascii=False) + "\n")
            n += 1
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-year", type=int, default=1980)
    parser.add_argument("--last-year", type=int, default=2025)
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    spark = get_spark("imdb-enrichment-scope")
    films = feature_films(read_imdb(spark, "title.basics"))
    ratings = read_imdb(spark, "title.ratings")
    top = top_films(films, ratings, args.first_year, args.last_year, args.top_n).cache()
    scope = film_scope(films, top, successful_films(films, ratings)).orderBy("tconst")
    people = people_scope(top, read_imdb(spark, "title.principals"),
                          read_imdb(spark, "name.basics")).orderBy("tconst", "ordering")

    top.write.mode("overwrite").parquet(str(SCOPE_DIR / "top_films"))
    n_films = write_jsonl(scope, SCOPE_DIR / "films.jsonl")
    n_people = write_jsonl(people, SCOPE_DIR / "people.jsonl")
    print(f"{top.count()} top films, {n_films} films to fetch, {n_people} credits")
    spark.stop()


if __name__ == "__main__":
    main()
