"""TV series whose worst episode is in the last season and best episode in the first two.

A series qualifies when:
- it is a tvSeries or tvMiniSeries with at least MIN_LONG_SEASONS seasons of
  >= MIN_EPISODES episodes (all episodes listed in title.episode count);
- among its rated episodes (>= MIN_VOTES votes, season >= 1), the lowest rating is only
  reached in the last season and the highest rating only in seasons 1 and 2 (strict:
  a tie with an episode from another season disqualifies the series).

The last season is the highest season number that has rated episodes.

Usage: python -m imdb_project.exploration.series
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from imdb_project.config import RESULTS_DIR
from imdb_project.exploration.common import to_markdown
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

SERIES_TYPES = ["tvSeries", "tvMiniSeries"]
MIN_EPISODES = 10
MIN_LONG_SEASONS = 3
MIN_VOTES = 10


def long_series(basics: DataFrame, episodes: DataFrame, min_episodes: int = MIN_EPISODES,
                min_long_seasons: int = MIN_LONG_SEASONS) -> DataFrame:
    """Series with at least min_long_seasons seasons of >= min_episodes episodes."""
    seasons = (
        episodes.where(F.col("seasonNumber") >= 1)
        .groupBy("parentTconst", "seasonNumber").count()
        .where(F.col("count") >= min_episodes)
        .groupBy("parentTconst").agg(F.count("*").alias("long_seasons"))
        .where(F.col("long_seasons") >= min_long_seasons)
    )
    series = basics.where(F.col("titleType").isin(SERIES_TYPES)).select(
        F.col("tconst").alias("parentTconst"), "primaryTitle", "startYear"
    )
    return series.join(seasons, "parentTconst")


def worst_last_best_first(series: DataFrame, episodes: DataFrame, ratings: DataFrame,
                          min_votes: int = MIN_VOTES) -> DataFrame:
    """Series whose worst rated episode is in the last season and best in seasons 1-2."""
    rated = (
        episodes.where(F.col("seasonNumber") >= 1)
        .join(series.select("parentTconst"), "parentTconst")
        .join(ratings.where(F.col("numVotes") >= min_votes), "tconst")
    )
    last = rated.groupBy("parentTconst").agg(F.max("seasonNumber").alias("last_season"))
    tagged = rated.join(last, "parentTconst").withColumn(
        "zone",
        F.when(F.col("seasonNumber") == F.col("last_season"), "last")
        .when(F.col("seasonNumber") <= 2, "first")
        .otherwise("middle"),
    )
    r = F.col("averageRating")
    agg = tagged.groupBy("parentTconst", "last_season").agg(
        F.count("*").alias("rated_episodes"),
        F.min(F.when(F.col("zone") == "last", r)).alias("worst_last"),
        F.min(F.when(F.col("zone") != "last", r)).alias("worst_other"),
        F.max(F.when(F.col("zone") == "first", r)).alias("best_first"),
        F.max(F.when(F.col("zone") != "first", r)).alias("best_other"),
    )
    return (
        agg.where(
            (F.col("last_season") >= 3)
            & (F.col("worst_last") < F.col("worst_other"))
            & (F.col("best_first") > F.col("best_other"))
        )
        .join(series, "parentTconst")
        .select(
            F.col("parentTconst").alias("tconst"), "primaryTitle", "startYear",
            "long_seasons", "last_season", "rated_episodes",
            "best_first", "worst_last",
        )
    )


def main():
    spark = get_spark("imdb-series")
    basics = read_imdb(spark, "title.basics")
    episodes = read_imdb(spark, "title.episode").cache()
    ratings = read_imdb(spark, "title.ratings")
    series = long_series(basics, episodes).cache()
    result = (
        worst_last_best_first(series, episodes, ratings)
        .join(ratings.select(F.col("tconst"), F.col("numVotes").alias("series_votes")),
              "tconst", "left")
        .orderBy(F.desc_nulls_last("series_votes"))
        .cache()
    )
    out = RESULTS_DIR / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "series_worst_last_best_first.md").write_text(to_markdown(result))
    result.show(50, truncate=False)
    print(f"{result.count()} series out of {series.count()} with "
          f">= {MIN_LONG_SEASONS} seasons of >= {MIN_EPISODES} episodes")
    spark.stop()


if __name__ == "__main__":
    main()
