"""Actors and actresses successful in films of several original languages.

IMDb has no original language for films (title.akas.language is the language of each
release title), so it comes from the "Language" row of the film's English Wikipedia
infobox, collected by the enrichment pipeline (first language listed = original
language). Run the enrichment scope, collect and build steps first.

A film is a success with a rating >= SUCCESS_RATING and at least SUCCESS_VOTES votes.

Usage: python -m imdb_project.exploration.languages
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from imdb_project.config import ENRICHED_DIR, RESULTS_DIR
from imdb_project.enrichment.scope import SUCCESS_RATING, SUCCESS_VOTES, successful_films
from imdb_project.exploration.common import feature_films, to_markdown
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

ACTING = ["actor", "actress"]


def original_language(film_languages: DataFrame) -> DataFrame:
    """One original language per film: the first one listed in the infobox."""
    return film_languages.where(F.size("languages") > 0).select(
        "tconst", F.col("languages")[0].alias("language")
    )


def multilingual_actors(success: DataFrame, languages: DataFrame,
                        principals: DataFrame) -> DataFrame:
    """Per actor: successful films and the distinct original languages of those films."""
    cast = principals.where(F.col("category").isin(ACTING)).select("tconst", "nconst")
    films = success.join(languages, "tconst").join(cast, "tconst").dropDuplicates(
        ["nconst", "tconst"]
    )
    return films.groupBy("nconst").agg(
        F.count("*").alias("successful_films"),
        F.array_sort(F.collect_set("language")).alias("languages"),
    ).withColumn("language_count", F.size("languages"))


def language_coverage(success: DataFrame, languages: DataFrame) -> DataFrame:
    """How many successful films have an original language."""
    return success.join(languages, "tconst", "left").agg(
        F.count("*").alias("successful_films"),
        F.count("language").alias("with_language"),
    )


def main():
    spark = get_spark("imdb-languages")
    films = feature_films(read_imdb(spark, "title.basics"))
    success = successful_films(films, read_imdb(spark, "title.ratings")).cache()
    languages = original_language(spark.read.parquet(str(ENRICHED_DIR / "film_languages")))
    actors = multilingual_actors(success, languages, read_imdb(spark, "title.principals"))
    names = read_imdb(spark, "name.basics").select("nconst", "primaryName")
    multi = (
        actors.where(F.col("language_count") >= 2).join(names, "nconst", "left")
        .select("primaryName", "language_count", "successful_films",
                F.array_join("languages", ", ").alias("languages"))
        .orderBy(F.desc("language_count"), F.desc("successful_films"), "primaryName")
        .cache()
    )
    counts = actors.groupBy("language_count").count().orderBy("language_count")
    top_languages = (
        success.join(languages, "tconst").groupBy("language").count()
        .orderBy(F.desc("count")).limit(15)
    )
    out = RESULTS_DIR / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "languages_coverage.md").write_text(
        f"Success: rating >= {SUCCESS_RATING} and votes >= {SUCCESS_VOTES}.\n\n"
        + to_markdown(language_coverage(success, languages))
    )
    (out / "languages_actor_counts.md").write_text(to_markdown(counts))
    (out / "languages_top_languages.md").write_text(to_markdown(top_languages))
    (out / "languages_3_or_more.md").write_text(
        to_markdown(multi.where(F.col("language_count") >= 3))
    )
    (out / "languages_2_top50.md").write_text(
        to_markdown(multi.where(F.col("language_count") == 2).limit(50))
    )
    counts.show()
    multi.show(30, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
