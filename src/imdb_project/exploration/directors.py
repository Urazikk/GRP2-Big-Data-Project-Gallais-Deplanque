"""Directors with exactly one feature film rated >= 8.0 and several others averaging <= 6.0.

Only feature films with at least MIN_VOTES votes count as rated. "Several" means at
least MIN_OTHERS other rated films, and their average is a simple (unweighted) mean.

Usage: python -m imdb_project.exploration.directors
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from imdb_project.config import RESULTS_DIR
from imdb_project.exploration.common import feature_films, to_markdown
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

HIGH_RATING = 8.0
LOW_AVERAGE = 6.0
MIN_VOTES = 100
MIN_OTHERS = 2


def directed_films(films: DataFrame, crew: DataFrame, ratings: DataFrame,
                   min_votes: int = MIN_VOTES) -> DataFrame:
    """One row per (director, rated film)."""
    directors = crew.where(F.col("directors").isNotNull()).select(
        "tconst", F.explode(F.split("directors", ",")).alias("nconst")
    )
    rated = ratings.where(F.col("numVotes") >= min_votes)
    return (
        films.select("tconst", "primaryTitle", "startYear")
        .join(rated, "tconst")
        .join(directors, "tconst")
    )


def one_hit_directors(directed: DataFrame, high: float = HIGH_RATING,
                      low_avg: float = LOW_AVERAGE, min_others: int = MIN_OTHERS) -> DataFrame:
    """Directors with exactly one film >= high whose other films average <= low_avg."""
    is_hit = F.col("averageRating") >= high
    stats = directed.groupBy("nconst").agg(
        F.sum(is_hit.cast("int")).alias("hits"),
        F.count("*").alias("rated_films"),
        F.avg(F.when(~is_hit, F.col("averageRating"))).alias("others_avg"),
        F.max_by(F.struct("tconst", "primaryTitle", "startYear", "averageRating", "numVotes"),
                 is_hit.cast("int")).alias("hit"),
    )
    return (
        stats.where(
            (F.col("hits") == 1)
            & (F.col("rated_films") - 1 >= min_others)
            & (F.col("others_avg") <= low_avg)
        )
        .select(
            "nconst",
            (F.col("rated_films") - 1).alias("other_films"),
            F.round("others_avg", 2).alias("others_avg"),
            F.col("hit.tconst").alias("hit_tconst"),
            F.col("hit.primaryTitle").alias("hit_title"),
            F.col("hit.startYear").alias("hit_year"),
            F.col("hit.averageRating").alias("hit_rating"),
            F.col("hit.numVotes").alias("hit_votes"),
        )
    )


def main():
    spark = get_spark("imdb-directors")
    films = feature_films(read_imdb(spark, "title.basics"))
    directed = directed_films(films, read_imdb(spark, "title.crew"),
                              read_imdb(spark, "title.ratings"))
    names = read_imdb(spark, "name.basics").select("nconst", "primaryName")
    result = (
        one_hit_directors(directed).join(names, "nconst", "left")
        .select("nconst", "primaryName", "other_films", "others_avg",
                "hit_title", "hit_year", "hit_rating", "hit_votes")
        .orderBy(F.desc("hit_votes"))
        .cache()
    )
    out = RESULTS_DIR / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "one_hit_directors.md").write_text(to_markdown(result))
    result.show(50, truncate=False)
    print(f"{result.count()} directors")
    spark.stop()


if __name__ == "__main__":
    main()
