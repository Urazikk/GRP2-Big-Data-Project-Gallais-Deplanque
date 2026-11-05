"""Actors and actresses with a 20+ year film career whose popularity peaked early.

Films are rated feature films (at least MIN_VOTES votes). An actor qualifies with at least
MIN_FILMS such films spanning at least MIN_YEARS years (first to last release year).
The career is split into thirds by year. Popularity peaked early when:
- the actor's highest rated film was released in the first third, and
- the average rating of the first third is above the average rating of the last third.

Usage: python -m imdb_project.exploration.careers
"""
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from imdb_project.config import RESULTS_DIR
from imdb_project.exploration.common import feature_films, to_markdown
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

ACTING = ["actor", "actress"]
MIN_VOTES = 100
MIN_FILMS = 15
MIN_YEARS = 20


def acted_films(films: DataFrame, principals: DataFrame, ratings: DataFrame,
                min_votes: int = MIN_VOTES) -> DataFrame:
    """One row per (actor, rated feature film with a release year)."""
    cast = principals.where(F.col("category").isin(ACTING)).select("tconst", "nconst")
    rated = ratings.where(F.col("numVotes") >= min_votes)
    return (
        films.where(F.col("startYear").isNotNull())
        .select("tconst", "primaryTitle", "startYear")
        .join(rated, "tconst")
        .join(cast, "tconst")
        .dropDuplicates(["nconst", "tconst"])
    )


def early_peak_actors(acted: DataFrame, min_films: int = MIN_FILMS,
                      min_years: int = MIN_YEARS) -> DataFrame:
    """Actors whose best film is in the first third of the career and who declined after."""
    w = Window.partitionBy("nconst")
    career = (
        acted.withColumn("first_year", F.min("startYear").over(w))
        .withColumn("last_year", F.max("startYear").over(w))
        .withColumn("films", F.count("*").over(w))
        .where((F.col("films") >= min_films)
               & (F.col("last_year") - F.col("first_year") >= min_years))
        .withColumn("third", (F.col("last_year") - F.col("first_year")) / 3)
        .withColumn(
            "period",
            F.when(F.col("startYear") < F.col("first_year") + F.col("third"), "early")
            .when(F.col("startYear") > F.col("last_year") - F.col("third"), "late")
            .otherwise("middle"),
        )
    )
    best = F.struct(F.col("averageRating"), F.col("numVotes"), F.col("primaryTitle"),
                    F.col("startYear"), F.col("period"))
    stats = career.groupBy("nconst", "films", "first_year", "last_year").agg(
        F.max(best).alias("best"),
        F.avg(F.when(F.col("period") == "early", F.col("averageRating"))).alias("early_avg"),
        F.avg(F.when(F.col("period") == "late", F.col("averageRating"))).alias("late_avg"),
    )
    return (
        stats.where((F.col("best.period") == "early") & (F.col("early_avg") > F.col("late_avg")))
        .select(
            "nconst", "films", "first_year", "last_year",
            F.col("best.primaryTitle").alias("best_film"),
            F.col("best.startYear").alias("best_year"),
            F.col("best.averageRating").alias("best_rating"),
            F.round("early_avg", 2).alias("early_avg"),
            F.round("late_avg", 2).alias("late_avg"),
            F.round(F.col("early_avg") - F.col("late_avg"), 2).alias("decline"),
        )
    )


def main():
    spark = get_spark("imdb-careers")
    films = feature_films(read_imdb(spark, "title.basics"))
    acted = acted_films(films, read_imdb(spark, "title.principals"),
                        read_imdb(spark, "title.ratings")).cache()
    names = read_imdb(spark, "name.basics").select("nconst", "primaryName")
    result = (
        early_peak_actors(acted).join(names, "nconst", "left")
        .select("nconst", "primaryName", "films", "first_year", "last_year", "best_film",
                "best_year", "best_rating", "early_avg", "late_avg", "decline")
        .orderBy(F.desc("decline"), "nconst")
        .cache()
    )
    eligible = (
        acted.groupBy("nconst")
        .agg(F.count("*").alias("n"), (F.max("startYear") - F.min("startYear")).alias("span"))
        .where((F.col("n") >= MIN_FILMS) & (F.col("span") >= MIN_YEARS))
        .count()
    )
    out = RESULTS_DIR / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "early_peak_actors.md").write_text(to_markdown(result))
    result.show(30, truncate=False)
    print(f"{result.count()} early peak actors out of {eligible} with "
          f">= {MIN_FILMS} films over >= {MIN_YEARS} years")
    spark.stop()


if __name__ == "__main__":
    main()
