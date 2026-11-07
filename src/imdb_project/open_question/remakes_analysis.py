"""Open question, step 3: are remakes rated lower than the films they remake? In Spark.

Inputs: the candidate pairs (remakes_scope) and the Wikipedia checks (remakes_collect),
read with an imposed schema. Only confirmed pairs are kept; each keeps its source URL
(lineage) and the sentence used as evidence. Outputs:
- data/open_question/remakes: confirmed pairs with ratings, votes and lineage (parquet);
- results/open_question/*.md: tables copied into REPORT.md.

Comparisons (remake minus original): overall, by gap between the two releases, by decade
of the remake, by genre of the remake, and depending on whether the remake shares at
least one principal (cast or crew) with the original.

Usage: python -m imdb_project.open_question.remakes_analysis
"""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

from imdb_project.config import RESULTS_DIR
from imdb_project.exploration.common import to_markdown
from imdb_project.imdb_io import read_imdb
from imdb_project.open_question.remakes_collect import CHECKS_PATH
from imdb_project.open_question.remakes_scope import CANDIDATES_PATH, REMAKES_DIR
from imdb_project.spark_session import get_spark

CANDIDATE_SCHEMA = T.StructType([
    T.StructField("original_tconst", T.StringType(), False),
    T.StructField("original_title", T.StringType()),
    T.StructField("original_year", T.IntegerType()),
    T.StructField("remake_tconst", T.StringType(), False),
    T.StructField("remake_title", T.StringType()),
    T.StructField("remake_original_title", T.StringType()),
    T.StructField("remake_year", T.IntegerType()),
])

CHECK_SCHEMA = T.StructType([
    T.StructField("original_tconst", T.StringType(), False),
    T.StructField("remake_tconst", T.StringType(), False),
    T.StructField("page_title", T.StringType()),
    T.StructField("source_url", T.StringType()),
    T.StructField("retrieved_at", T.StringType()),
    T.StructField("confirmed", T.BooleanType()),
    T.StructField("evidence", T.StringType()),
    T.StructField("note", T.StringType()),
])

GAP_BUCKETS = [(10, 19, "10-19 years"), (20, 29, "20-29 years"), (30, 49, "30-49 years"),
               (50, 1000, "50+ years")]
MIN_GROUP = 10  # groups (genres) with fewer confirmed pairs are not shown


def read_jsonl(spark: SparkSession, path, schema: T.StructType) -> DataFrame:
    return spark.read.schema(schema).json(str(path))


def funnel(candidates: DataFrame, checks: DataFrame) -> DataFrame:
    """How many candidates survive each step of the Wikipedia check."""
    remakes = checks.groupBy("remake_tconst").agg(
        F.max(F.col("source_url").isNotNull()).alias("has_page"),
        F.max("confirmed").alias("confirmed"),
    )
    rows = [
        ("candidate pairs (same title, gap >= 10 years)", candidates.count()),
        ("distinct remake candidates", candidates.select("remake_tconst").distinct().count()),
        ("remake candidates with a Wikipedia page linking to their IMDb id",
         remakes.where("has_page").count()),
        ("remakes confirmed by their Wikipedia introduction", remakes.where("confirmed").count()),
        ("confirmed (original, remake) pairs", checks.where("confirmed").count()),
    ]
    return candidates.sparkSession.createDataFrame(rows, "step string, count long")


def confirmed_pairs(candidates: DataFrame, checks: DataFrame, ratings: DataFrame,
                    basics: DataFrame) -> DataFrame:
    """Confirmed pairs with both ratings, the gap, the remake genres and the lineage."""
    o_r = ratings.select(F.col("tconst").alias("original_tconst"),
                         F.col("averageRating").alias("original_rating"),
                         F.col("numVotes").alias("original_votes"))
    r_r = ratings.select(F.col("tconst").alias("remake_tconst"),
                         F.col("averageRating").alias("remake_rating"),
                         F.col("numVotes").alias("remake_votes"))
    genres = basics.select(F.col("tconst").alias("remake_tconst"),
                           F.split("genres", ",").alias("remake_genres"))
    return (
        checks.where("confirmed")
        .join(candidates, ["original_tconst", "remake_tconst"])
        .join(o_r, "original_tconst").join(r_r, "remake_tconst")
        .join(genres, "remake_tconst", "left")
        .withColumn("gap_years", F.col("remake_year") - F.col("original_year"))
        .withColumn("rating_diff", F.round(F.col("remake_rating") - F.col("original_rating"), 2))
        .withColumn("votes_ratio", F.col("remake_votes") / F.col("original_votes"))
        .withColumn("retrieved_at", F.to_timestamp("retrieved_at"))
        .select("original_tconst", "original_title", "original_year", "original_rating",
                "original_votes", "remake_tconst", "remake_title", "remake_year",
                "remake_rating", "remake_votes", "remake_genres", "gap_years",
                "rating_diff", "votes_ratio", "source_url", "retrieved_at", "evidence")
    )


def compare(pairs: DataFrame, *group_cols) -> DataFrame:
    """Rating and votes of remakes against their originals, overall or per group."""
    agg = [
        F.count("*").alias("pairs"),
        F.round(F.avg("original_rating"), 2).alias("avg_original_rating"),
        F.round(F.avg("remake_rating"), 2).alias("avg_remake_rating"),
        F.round(F.avg("rating_diff"), 2).alias("avg_diff"),
        F.round(F.percentile_approx("rating_diff", 0.5, 10000), 2).alias("median_diff"),
        F.round(100 * F.avg((F.col("rating_diff") > 0).cast("int")), 1).alias("pct_remake_better"),
        F.round(100 * F.avg((F.col("rating_diff") < 0).cast("int")), 1).alias("pct_remake_worse"),
        F.round(F.percentile_approx("votes_ratio", 0.5, 10000), 2).alias("median_votes_ratio"),
        F.round(100 * F.avg((F.col("votes_ratio") > 1).cast("int")), 1)
        .alias("pct_remake_more_votes"),
    ]
    grouped = pairs.groupBy(*group_cols) if group_cols else pairs.groupBy()
    return grouped.agg(*agg)


def gap_bucket(col: str = "gap_years"):
    expr = None
    for low, high, label in GAP_BUCKETS:
        cond = F.col(col).between(low, high)
        expr = F.when(cond, label) if expr is None else expr.when(cond, label)
    return expr


def shared_principals(pairs: DataFrame, principals: DataFrame) -> DataFrame:
    """Number of people credited as principals on both the original and the remake."""
    people = principals.select("tconst", "nconst").distinct()
    o = people.select(F.col("tconst").alias("original_tconst"), "nconst")
    r = people.select(F.col("tconst").alias("remake_tconst"), "nconst")
    shared = (
        pairs.select("original_tconst", "remake_tconst")
        .join(o, "original_tconst").join(r, ["remake_tconst", "nconst"])
        .groupBy("original_tconst", "remake_tconst").agg(F.count("*").alias("shared_people"))
    )
    return (
        pairs.join(shared, ["original_tconst", "remake_tconst"], "left")
        .fillna(0, ["shared_people"])
        .withColumn("shares_people", F.col("shared_people") > 0)
    )


def extremes(pairs: DataFrame, n: int = 10, ascending: bool = True) -> DataFrame:
    order = F.col("rating_diff").asc() if ascending else F.col("rating_diff").desc()
    return pairs.orderBy(order, F.desc("remake_votes")).limit(n).select(
        "original_title", "original_year", "original_rating", "remake_title", "remake_year",
        "remake_rating", "rating_diff", "source_url")


def main():
    spark = get_spark("imdb-remakes-analysis")
    candidates = read_jsonl(spark, CANDIDATES_PATH, CANDIDATE_SCHEMA)
    checks = read_jsonl(spark, CHECKS_PATH, CHECK_SCHEMA).cache()
    pairs = confirmed_pairs(candidates, checks, read_imdb(spark, "title.ratings"),
                            read_imdb(spark, "title.basics"))
    pairs = shared_principals(pairs, read_imdb(spark, "title.principals")).cache()
    pairs.write.mode("overwrite").parquet(str(REMAKES_DIR / "remakes"))

    by_genre = (
        compare(pairs.withColumn("genre", F.explode("remake_genres")), "genre")
        .where(F.col("pairs") >= MIN_GROUP).orderBy(F.desc("pairs"))
    )
    tables = {
        "remakes_funnel": funnel(candidates, checks),
        "remakes_overall": compare(pairs),
        "remakes_by_gap": compare(pairs.withColumn("gap", gap_bucket()), "gap").orderBy("gap"),
        "remakes_by_decade": compare(
            pairs.withColumn("remake_decade", (F.floor(F.col("remake_year") / 10) * 10)
                             .cast("int")), "remake_decade").orderBy("remake_decade"),
        "remakes_by_genre": by_genre,
        "remakes_shared_people": compare(pairs, "shares_people").orderBy("shares_people"),
        "remakes_largest_drops": extremes(pairs, ascending=True),
        "remakes_largest_gains": extremes(pairs, ascending=False),
    }
    out = RESULTS_DIR / "open_question"
    out.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        (out / f"{name}.md").write_text(to_markdown(df))
        print(name)
        df.show(40, truncate=60)
    spark.stop()


if __name__ == "__main__":
    main()
