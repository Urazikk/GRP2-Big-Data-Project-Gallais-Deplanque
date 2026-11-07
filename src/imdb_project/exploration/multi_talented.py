"""Multi-talented film professionals and how they perform when they combine roles.

Roles on rated feature films (at least MIN_VOTES votes) come from what people actually
did, not from their declared profession:
- act: title.principals category actor or actress;
- direct: title.principals category director, or title.crew directors;
- write: title.principals category writer, or title.crew writers.

A person is multi-talented with at least two roles held on MIN_FILMS_PER_ROLE films each.
Their films are split into multi-role films (two roles or more on the same film) and
single-role films, and the two groups are compared per person.

Usage: python -m imdb_project.exploration.multi_talented
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from imdb_project.config import RESULTS_DIR
from imdb_project.exploration.common import feature_films, to_markdown
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

ROLE_OF_CATEGORY = {"actor": "act", "actress": "act", "director": "direct", "writer": "write"}
MIN_VOTES = 100
MIN_FILMS_PER_ROLE = 3


def film_roles(films: DataFrame, principals: DataFrame, crew: DataFrame,
               ratings: DataFrame, min_votes: int = MIN_VOTES) -> DataFrame:
    """One row per (person, rated feature film) with the sorted list of roles held."""
    mapping = F.create_map(*[F.lit(x) for kv in ROLE_OF_CATEGORY.items() for x in kv])
    from_principals = principals.where(F.col("category").isin(list(ROLE_OF_CATEGORY))).select(
        "tconst", "nconst", mapping[F.col("category")].alias("role")
    )
    from_crew = [
        crew.where(F.col(column).isNotNull()).select(
            "tconst", F.explode(F.split(column, ",")).alias("nconst"), F.lit(role).alias("role")
        )
        for column, role in (("directors", "direct"), ("writers", "write"))
    ]
    roles = from_principals.unionByName(from_crew[0]).unionByName(from_crew[1])
    rated = (
        films.select("tconst")
        .join(ratings.where(F.col("numVotes") >= min_votes), "tconst")
    )
    return (
        roles.join(rated, "tconst")
        .groupBy("nconst", "tconst", "averageRating", "numVotes")
        .agg(F.array_sort(F.collect_set("role")).alias("roles"))
    )


def multi_talented(roles: DataFrame, min_films: int = MIN_FILMS_PER_ROLE) -> DataFrame:
    """People holding at least two roles on min_films films each, with their role set."""
    per_role = (
        roles.select("nconst", F.explode("roles").alias("role"))
        .groupBy("nconst", "role").count()
        .where(F.col("count") >= min_films)
    )
    return (
        per_role.groupBy("nconst")
        .agg(F.array_sort(F.collect_list("role")).alias("talents"))
        .where(F.size("talents") >= 2)
        .withColumn("talent_combo", F.array_join("talents", "+"))
    )


def performance_by_person(roles: DataFrame, talented: DataFrame) -> DataFrame:
    """Per multi-talented person: rating and votes on multi-role vs single-role films."""
    films = roles.join(talented.select("nconst", "talent_combo"), "nconst").withColumn(
        "multi", F.size("roles") >= 2
    )

    def stats(flag, prefix):
        return [
            F.sum(flag.cast("int")).alias(f"{prefix}_films"),
            F.avg(F.when(flag, F.col("averageRating"))).alias(f"{prefix}_rating"),
            F.percentile_approx(F.when(flag, F.col("numVotes")), 0.5, 1000)
            .alias(f"{prefix}_median_votes"),
        ]

    return (
        films.groupBy("nconst", "talent_combo")
        .agg(*stats(F.col("multi"), "multi"), *stats(~F.col("multi"), "single"))
        .where((F.col("multi_films") > 0) & (F.col("single_films") > 0))
        .withColumn("rating_gap", F.col("multi_rating") - F.col("single_rating"))
    )


def summary_by_combo(perf: DataFrame) -> DataFrame:
    """Per talent combination: people compared and how multi-role films fare."""
    return (
        perf.groupBy("talent_combo")
        .agg(
            F.count("*").alias("people"),
            F.sum("multi_films").alias("multi_films"),
            F.sum("single_films").alias("single_films"),
            F.round(F.avg("multi_rating"), 2).alias("avg_multi_rating"),
            F.round(F.avg("single_rating"), 2).alias("avg_single_rating"),
            F.round(F.avg("rating_gap"), 2).alias("avg_rating_gap"),
            F.round(F.expr("percentile_approx(rating_gap, 0.5, 1000)"), 2)
            .alias("median_rating_gap"),
            F.round(100 * F.avg((F.col("rating_gap") > 0).cast("int")), 1)
            .alias("pct_better_multi"),
            F.round(F.avg("multi_median_votes"), 0).alias("avg_multi_median_votes"),
            F.round(F.avg("single_median_votes"), 0).alias("avg_single_median_votes"),
        )
        .orderBy(F.desc("people"))
    )


def main():
    spark = get_spark("imdb-multi-talented")
    films = feature_films(read_imdb(spark, "title.basics"))
    roles = film_roles(films, read_imdb(spark, "title.principals"),
                       read_imdb(spark, "title.crew"), read_imdb(spark, "title.ratings")).cache()
    talented = multi_talented(roles).cache()
    perf = performance_by_person(roles, talented).cache()
    names = read_imdb(spark, "name.basics").select("nconst", "primaryName")

    combos = talented.groupBy("talent_combo").count().orderBy(F.desc("count"))
    summary = summary_by_combo(perf)
    top = (
        perf.join(names, "nconst", "left")
        .select("primaryName", "talent_combo", "multi_films", "single_films",
                F.round("multi_rating", 2).alias("multi_rating"),
                F.round("single_rating", 2).alias("single_rating"),
                F.round("rating_gap", 2).alias("rating_gap"))
        .orderBy(F.desc("multi_films"), "primaryName")
        .limit(30)
    )
    out = RESULTS_DIR / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "multi_talented_counts.md").write_text(to_markdown(combos))
    (out / "multi_talented_performance.md").write_text(to_markdown(summary))
    (out / "multi_talented_top30.md").write_text(to_markdown(top))
    combos.show(truncate=False)
    summary.show(truncate=False)
    top.show(30, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
