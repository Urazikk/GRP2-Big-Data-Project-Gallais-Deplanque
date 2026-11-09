"""Top 3 most popular genres per year (1980-2025) and comparison with the other genres.

Popularity of a genre in a year = total number of IMDb votes received by the feature
films of that genre released that year. A film counts in each of its genres.

Usage: python -m imdb_project.exploration.popular_genres
"""
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from imdb_project.config import RESULTS_DIR
from imdb_project.exploration.common import explode_genres, feature_films, to_markdown, read_table
from imdb_project.spark_session import get_spark

FIRST_YEAR, LAST_YEAR = 1980, 2025
TOP_N = 3


def genre_year_popularity(by_genre: DataFrame, ratings: DataFrame,
                          first_year: int = FIRST_YEAR, last_year: int = LAST_YEAR) -> DataFrame:
    """Per (year, genre): films, rated films, total votes and vote-weighted rating."""
    films = (
        by_genre.where(F.col("startYear").between(first_year, last_year))
        .join(ratings, "tconst", "left")
        .withColumn("votes", F.coalesce(F.col("numVotes"), F.lit(0)).cast("long"))
    )
    return films.groupBy(F.col("startYear").alias("year"), "genre").agg(
        F.count("*").alias("films"),
        F.count("averageRating").alias("rated_films"),
        F.sum("votes").alias("votes"),
        F.sum(F.col("averageRating") * F.col("votes")).alias("rating_x_votes"),
    )


def rank_genres(popularity: DataFrame) -> DataFrame:
    """Add the popularity rank of each genre within its year (1 = most votes)."""
    w = Window.partitionBy("year").orderBy(F.desc("votes"), "genre")
    return popularity.withColumn("rank", F.row_number().over(w))


def top_genres(ranked: DataFrame, n: int = TOP_N) -> DataFrame:
    """Top n genres per year, one row per (year, rank)."""
    return (
        ranked.where(F.col("rank") <= n)
        .withColumn("weighted_rating",
                    F.round(F.col("rating_x_votes") / F.col("votes"), 2))
        .select("year", "rank", "genre", "films", "votes", "weighted_rating")
        .orderBy("year", "rank")
    )


def compare_top_vs_rest(ranked: DataFrame, n: int = TOP_N) -> DataFrame:
    """Per year, the top n genres taken together against all other genres.

    Shares are computed over (film, genre) pairs, so a film with several genres
    is counted once per genre.
    """
    grouped = ranked.withColumn(
        "group", F.when(F.col("rank") <= n, "top").otherwise("rest")
    ).groupBy("year", "group").agg(
        F.count("*").alias("genres"),
        F.sum("films").alias("films"),
        F.sum("votes").alias("votes"),
        F.sum("rating_x_votes").alias("rating_x_votes"),
    )
    pivot = grouped.groupBy("year").pivot("group", ["top", "rest"]).agg(
        F.first("genres").alias("genres"),
        F.first("films").alias("films"),
        F.first("votes").alias("votes"),
        F.first("rating_x_votes").alias("rxv"),
    )
    return (
        pivot.select(
            "year",
            F.col("rest_genres").alias("other_genres"),
            F.round(100 * F.col("top_votes") / (F.col("top_votes") + F.col("rest_votes")), 1)
            .alias("top_vote_share_pct"),
            F.round(100 * F.col("top_films") / (F.col("top_films") + F.col("rest_films")), 1)
            .alias("top_film_share_pct"),
            F.round(F.col("top_votes") / F.col("top_films"), 0).alias("top_votes_per_film"),
            F.round(F.col("rest_votes") / F.col("rest_films"), 0).alias("rest_votes_per_film"),
            F.round(F.col("top_rxv") / F.col("top_votes"), 2).alias("top_weighted_rating"),
            F.round(F.col("rest_rxv") / F.col("rest_votes"), 2).alias("rest_weighted_rating"),
        )
        .orderBy("year")
    )


def top_genre_frequency(top: DataFrame) -> DataFrame:
    """How many years each genre appears in the top n, and how many times at rank 1."""
    return (
        top.groupBy("genre")
        .agg(F.count("*").alias("years_in_top"),
             F.sum((F.col("rank") == 1).cast("int")).alias("years_at_rank_1"))
        .orderBy(F.desc("years_in_top"), F.desc("years_at_rank_1"))
    )


def main():
    spark = get_spark("imdb-popular-genres")
    by_genre = explode_genres(feature_films(read_table(spark, "title.basics")))
    ratings = read_table(spark, "title.ratings")
    ranked = rank_genres(genre_year_popularity(by_genre, ratings)).cache()
    top = top_genres(ranked).cache()
    comparison = compare_top_vs_rest(ranked)
    frequency = top_genre_frequency(top)

    out = RESULTS_DIR / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "top3_genres_per_year.md").write_text(to_markdown(top))
    (out / "top3_vs_rest_per_year.md").write_text(to_markdown(comparison))
    (out / "top3_genre_frequency.md").write_text(to_markdown(frequency))
    top.show(150, truncate=False)
    comparison.show(50, truncate=False)
    frequency.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
