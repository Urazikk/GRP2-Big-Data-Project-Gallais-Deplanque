"""Static lookup table: English Wikipedia page title -> IMDb id, built in Spark.

The stream gives page titles only, so each IMDb title or person gets the page titles it is
likely to have on English Wikipedia (the naming conventions of Wikipedia):
- films (titleType movie): "Title (2019 film)", "Title (film)";
- series (tvSeries, tvMiniSeries): "Title (2019 TV series)", "Title (TV series)",
  "Title (miniseries)";
- people (actors, actresses, directors, writers of these titles): "Name (actor)",
  "Name (actress)", "Name (director)", "Name (filmmaker)", "Name (writer)";
- the bare title or name, only for popular entries (PLAIN_MIN_VOTES), because a bare
  title is often another article ("Heat", "Up").

A page title claimed by several entries is resolved to the one with the most votes; the
number of competing entries is kept in the table. Only titles with at least MIN_VOTES votes
are used, which keeps the table small enough to be broadcast to the streaming join.

Usage: python -m imdb_project.streaming.lookup [--min-votes 1000] [--plain-min-votes 20000]
"""
import argparse

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from imdb_project.config import DATA_DIR
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

STREAMING_DIR = DATA_DIR / "streaming"
LOOKUP_PATH = STREAMING_DIR / "lookup"
MIN_VOTES = 1000
PLAIN_MIN_VOTES = 20000
SERIES = ["tvSeries", "tvMiniSeries"]
PEOPLE_CATEGORIES = ["actor", "actress", "director", "writer"]
PERSON_SUFFIXES = {"actor": ["actor"], "actress": ["actress", "actor"],
                   "director": ["director", "filmmaker"], "writer": ["writer"]}


def _suffixed(base: Column, suffixes: Column) -> Column:
    """Array of 'base (suffix)' for every suffix."""
    return F.transform(suffixes, lambda s: F.concat(base, F.lit(" ("), s, F.lit(")")))


def title_pages(titles: DataFrame, ratings: DataFrame, min_votes: int = MIN_VOTES,
                plain_min_votes: int = PLAIN_MIN_VOTES) -> DataFrame:
    """Candidate page titles of films and series: one row per (page_title, tconst)."""
    rated = (
        titles.where(F.col("titleType").isin(["movie"] + SERIES))
        .join(ratings.where(F.col("numVotes") >= min_votes), "tconst")
    )
    kind = F.when(F.col("titleType") == "movie", "film").otherwise("series")
    year = F.col("startYear").cast("string")
    film_forms = F.array(F.concat(F.col("primaryTitle"), F.lit(" ("), year, F.lit(" film)")),
                         F.concat(F.col("primaryTitle"), F.lit(" (film)")))
    series_forms = F.array(F.concat(F.col("primaryTitle"), F.lit(" ("), year,
                                    F.lit(" TV series)")),
                           F.concat(F.col("primaryTitle"), F.lit(" (TV series)")),
                           F.concat(F.col("primaryTitle"), F.lit(" (miniseries)")))
    forms = F.when(kind == "film", film_forms).otherwise(series_forms)
    forms = F.when(F.col("numVotes") >= plain_min_votes,
                   F.concat(forms, F.array(F.col("primaryTitle")))).otherwise(forms)
    return (
        rated.select(F.col("tconst").alias("imdb_id"), kind.alias("kind"),
                     F.col("primaryTitle").alias("label"), "startYear",
                     F.col("numVotes").alias("votes"), F.explode(forms).alias("page_title"))
        .where(F.col("page_title").isNotNull())
    )


def person_pages(pages_of_titles: DataFrame, principals: DataFrame, names: DataFrame,
                 plain_min_votes: int = PLAIN_MIN_VOTES) -> DataFrame:
    """Candidate page titles of the people credited on the selected titles."""
    credits = (
        principals.where(F.col("category").isin(PEOPLE_CATEGORIES))
        .join(pages_of_titles.select(F.col("imdb_id").alias("tconst"), "votes").distinct(),
              "tconst")
        .groupBy("nconst").agg(F.collect_set("category").alias("categories"),
                               F.max("votes").alias("votes"))
    )
    mapping = F.create_map(*[F.lit(x) for k, v in PERSON_SUFFIXES.items()
                             for x in (k, F.array(*[F.lit(s) for s in v]))])
    suffixes = F.array_distinct(F.flatten(F.transform("categories", lambda c: mapping[c])))
    people = credits.join(names.select("nconst", "primaryName"), "nconst")
    forms = _suffixed(F.col("primaryName"), suffixes)
    forms = F.when(F.col("votes") >= plain_min_votes,
                   F.concat(forms, F.array(F.col("primaryName")))).otherwise(forms)
    return people.select(F.col("nconst").alias("imdb_id"), F.lit("person").alias("kind"),
                         F.col("primaryName").alias("label"),
                         F.lit(None).cast("int").alias("startYear"), "votes",
                         F.explode(forms).alias("page_title"))


def resolve(candidates: DataFrame) -> DataFrame:
    """One row per page title: the entry with the most votes, and how many competed."""
    w = Window.partitionBy("page_title").orderBy(F.desc("votes"), "imdb_id")
    return (
        candidates.dropDuplicates(["page_title", "imdb_id"])
        .withColumn("competitors", F.count("*").over(Window.partitionBy("page_title")))
        .withColumn("rank", F.row_number().over(w))
        .where(F.col("rank") == 1).drop("rank")
    )


def build_lookup(basics: DataFrame, ratings: DataFrame, principals: DataFrame,
                 names: DataFrame, min_votes: int = MIN_VOTES,
                 plain_min_votes: int = PLAIN_MIN_VOTES) -> DataFrame:
    titles = title_pages(basics, ratings, min_votes, plain_min_votes).cache()
    people = person_pages(titles, principals, names, plain_min_votes)
    return resolve(titles.unionByName(people))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-votes", type=int, default=MIN_VOTES)
    parser.add_argument("--plain-min-votes", type=int, default=PLAIN_MIN_VOTES)
    args = parser.parse_args()

    spark = get_spark("imdb-streaming-lookup", driver_memory="6g")
    lookup = build_lookup(read_imdb(spark, "title.basics"), read_imdb(spark, "title.ratings"),
                          read_imdb(spark, "title.principals"), read_imdb(spark, "name.basics"),
                          args.min_votes, args.plain_min_votes)
    lookup.coalesce(4).write.mode("overwrite").parquet(str(LOOKUP_PATH))
    saved = spark.read.parquet(str(LOOKUP_PATH))
    saved.groupBy("kind").agg(F.count("*").alias("page_titles"),
                              F.countDistinct("imdb_id").alias("imdb_entries")).show()
    print(f"lookup written to {LOOKUP_PATH}")
    spark.stop()


if __name__ == "__main__":
    main()
