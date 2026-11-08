"""Clean the IMDb tables: typed parquet tables in data/clean, quality flags and quarantine.

Policy: nothing is silently lost.
- Rows whose key points to a missing parent (a principal whose person is not in
  name.basics, a rating of an unknown title...) are moved to data/clean/quarantine with the
  reason, so they can be counted and inspected.
- Values that are impossible are kept and flagged in a dq_flags array column (for example
  a death year before the birth year), so each analysis decides whether to use them.
- Runtimes of 0 minutes or less, or above MAX_RUNTIME minutes, are set to null in
  runtimeMinutes; the original value is kept in runtimeMinutes_raw.
- Comma separated lists become arrays (genres, professions, known for titles, characters),
  and the ids of known for titles that do not exist are removed from the array.

Tables written (parquet): name_basics, title_basics, title_ratings, title_principals,
title_directors, title_writers, title_episode, title_akas, quarantine.
A summary of rows in, rows out, quarantined rows and flags per table is written to
results/preparation/cleaning_summary.md.

Usage: python -m imdb_project.preparation.cleaning [--max-runtime 600]
"""
import argparse
from datetime import date
from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from imdb_project.config import CLEAN_DIR, RESULTS_DIR
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

MAX_RUNTIME = 600            # minutes; 10 hours
CURRENT_YEAR = date.today().year
QUARANTINE_SCHEMA = "table string, reason string, record string"


def flags(*rules) -> Column:
    """Array of the names of the rules whose condition is true (nulls count as false)."""
    return F.filter(F.array(*[F.when(cond, F.lit(name)) for name, cond in rules]),
                    lambda x: x.isNotNull())


def split_list(col: str) -> Column:
    return F.when(F.col(col).isNull(), F.array().cast("array<string>")).otherwise(
        F.split(F.col(col), ","))


def quarantine(df: DataFrame, table: str, reason: str) -> DataFrame:
    return df.select(F.lit(table).alias("table"), F.lit(reason).alias("reason"),
                     F.to_json(F.struct(*df.columns)).alias("record"))


def split_by_parent(child: DataFrame, key: str, parent_keys: DataFrame, table: str,
                    reason: str):
    """(rows whose key exists in parent_keys, quarantined rows)."""
    keys = parent_keys.select(F.col(parent_keys.columns[0]).alias(key)).distinct()
    return (child.join(keys, key, "left_semi"),
            quarantine(child.join(keys, key, "left_anti"), table, reason))


def clean_titles(basics: DataFrame, max_runtime: int = MAX_RUNTIME,
                 current_year: int = CURRENT_YEAR) -> DataFrame:
    runtime = F.col("runtimeMinutes")
    return basics.select(
        "tconst", "titleType", "primaryTitle", "originalTitle",
        (F.col("isAdult") == 1).alias("isAdult"), "startYear", "endYear",
        F.when((runtime > 0) & (runtime <= max_runtime), runtime).alias("runtimeMinutes"),
        F.col("runtimeMinutes").alias("runtimeMinutes_raw"),
        split_list("genres").alias("genres"),
        flags(("runtime_not_positive", runtime <= 0),
              ("runtime_over_max", runtime > max_runtime),
              ("start_after_current_year", F.col("startYear") > current_year),
              ("end_before_start", F.col("endYear") < F.col("startYear"))).alias("dq_flags"),
    )


def clean_names(names: DataFrame, title_keys: DataFrame) -> DataFrame:
    """Typed people, with knownForTitles restricted to existing titles."""
    birth, death = F.col("birthYear"), F.col("deathYear")
    base = names.select(
        "nconst", "primaryName", "birthYear", "deathYear",
        split_list("primaryProfession").alias("primaryProfession"),
        flags(("death_before_birth", death < birth),
              ("birth_before_1000", birth < 1000),
              ("lifespan_over_110", death - birth > 110),
              ("alive_born_before_1900", death.isNull() & (birth < 1900))).alias("dq_flags"),
        split_list("knownForTitles").alias("known_raw"),
    )
    known = (
        base.select("nconst", F.explode("known_raw").alias("tconst"))
        .join(title_keys, "tconst", "left_semi")
        .groupBy("nconst").agg(F.collect_list("tconst").alias("knownForTitles"))
    )
    return (
        base.join(known, "nconst", "left")
        .withColumn("knownForTitles", F.coalesce("knownForTitles",
                                                 F.array().cast("array<string>")))
        .withColumn("dq_flags", F.when(
            F.size("knownForTitles") < F.size("known_raw"),
            F.array_append("dq_flags", F.lit("unknown_known_for_title"))
        ).otherwise(F.col("dq_flags")))
        .drop("known_raw")
    )


def clean_principals(principals: DataFrame, titles: DataFrame, names: DataFrame):
    """(principals, quarantine). Flags use the release year and the life of the person."""
    characters = F.from_json("characters", T.ArrayType(T.StringType()))
    typed = principals.select("tconst", "ordering", "nconst", "category", "job",
                              F.coalesce(characters, F.array().cast("array<string>"))
                              .alias("characters"))
    kept, q1 = split_by_parent(typed, "tconst", titles.select("tconst"), "title_principals",
                               "tconst missing in title.basics")
    kept, q2 = split_by_parent(kept, "nconst", names.select("nconst"), "title_principals",
                               "nconst missing in name.basics")
    start, birth, death = F.col("startYear"), F.col("birthYear"), F.col("deathYear")
    flagged = (
        kept.join(titles.select("tconst", "startYear"), "tconst")
        .join(names.select("nconst", "birthYear", "deathYear"), "nconst")
        .withColumn("dq_flags", flags(
            ("born_after_release", birth > start),
            # usually archive footage or an adapted author, kept but flagged
            ("died_before_release", death < start - 1),
            ("aged_over_100_at_release", start - birth > 100)))
        .drop("startYear", "birthYear", "deathYear")
    )
    return flagged, q1.unionByName(q2)


def clean_crew(crew: DataFrame, titles: DataFrame, names: DataFrame, column: str):
    """(one row per (tconst, nconst) for directors or writers, quarantine)."""
    table = "title_" + column
    exploded = crew.where(F.col(column).isNotNull()).select(
        "tconst", F.explode(F.split(column, ",")).alias("nconst"))
    kept, q1 = split_by_parent(exploded, "tconst", titles.select("tconst"), table,
                               "tconst missing in title.basics")
    kept, q2 = split_by_parent(kept, "nconst", names.select("nconst"), table,
                               "nconst missing in name.basics")
    return kept.dropDuplicates(), q1.unionByName(q2)


def clean_episodes(episodes: DataFrame, titles: DataFrame):
    kept, q1 = split_by_parent(episodes, "tconst", titles.select("tconst"), "title_episode",
                               "tconst missing in title.basics")
    kept, q2 = split_by_parent(kept, "parentTconst", titles.select("tconst"), "title_episode",
                               "parentTconst missing in title.basics")
    kept = kept.withColumn("dq_flags", flags(
        ("no_season_or_episode_number",
         F.col("seasonNumber").isNull() | F.col("episodeNumber").isNull())))
    return kept, q1.unionByName(q2)


def clean_akas(akas: DataFrame, titles: DataFrame):
    typed = akas.withColumn("isOriginalTitle", F.col("isOriginalTitle") == 1)
    keys = titles.select(F.col("tconst").alias("titleId"))
    return (typed.join(keys, "titleId", "left_semi"),
            quarantine(typed.join(keys, "titleId", "left_anti"), "title_akas",
                       "titleId missing in title.basics"))


def flag_counts(df: DataFrame, table: str) -> DataFrame:
    return (df.select(F.explode("dq_flags").alias("flag")).groupBy("flag").count()
            .select(F.lit(table).alias("table"), "flag", "count"))


def to_markdown(df: DataFrame) -> str:
    rows = df.collect()
    lines = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    for r in rows:
        lines.append("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-runtime", type=int, default=MAX_RUNTIME)
    args = parser.parse_args()

    spark = get_spark("imdb-cleaning", driver_memory="8g")
    spark.conf.set("spark.sql.shuffle.partitions", "64")

    def save(df, name):
        df.write.mode("overwrite").parquet(str(CLEAN_DIR / name))
        return spark.read.parquet(str(CLEAN_DIR / name))

    raw = {t: read_imdb(spark, t) for t in ("title.basics", "name.basics", "title.ratings",
                                            "title.principals", "title.crew",
                                            "title.episode", "title.akas")}
    titles = save(clean_titles(raw["title.basics"], args.max_runtime), "title_basics")
    names = save(clean_names(raw["name.basics"], titles.select("tconst")), "name_basics")

    ratings, q_ratings = split_by_parent(raw["title.ratings"], "tconst", titles.select("tconst"),
                                         "title_ratings", "tconst missing in title.basics")
    principals, q_principals = clean_principals(raw["title.principals"], titles, names)
    directors, q_directors = clean_crew(raw["title.crew"], titles, names, "directors")
    writers, q_writers = clean_crew(raw["title.crew"], titles, names, "writers")
    episodes, q_episodes = clean_episodes(raw["title.episode"], titles)
    akas, q_akas = clean_akas(raw["title.akas"], titles)

    out = {"title_ratings": save(ratings, "title_ratings"),
           "title_principals": save(principals, "title_principals"),
           "title_directors": save(directors, "title_directors"),
           "title_writers": save(writers, "title_writers"),
           "title_episode": save(episodes, "title_episode"),
           "title_akas": save(akas, "title_akas")}
    q = save(reduce(DataFrame.unionByName,
                    [q_ratings, q_principals, q_directors, q_writers, q_episodes, q_akas]),
             "quarantine")

    q_counts = {r.table: r["count"] for r in q.groupBy("table").count().collect()}
    sizes = [("title_basics", raw["title.basics"].count(), titles.count()),
             ("name_basics", raw["name.basics"].count(), names.count())]
    sizes += [(t, None, df.count()) for t, df in out.items()]
    # for the tables split by parent key, rows in = rows out + quarantined rows
    summary = spark.createDataFrame(
        [(t, rows_in if rows_in is not None else rows_out + q_counts.get(t, 0), rows_out,
          q_counts.get(t, 0)) for t, rows_in, rows_out in sizes],
        "table string, rows_in long, rows_out long, quarantined long")
    flagged = reduce(DataFrame.unionByName, [
        flag_counts(titles, "title_basics"), flag_counts(names, "name_basics"),
        flag_counts(out["title_principals"], "title_principals"),
        flag_counts(out["title_episode"], "title_episode")]).orderBy("table", F.desc("count"))
    reasons = q.groupBy("table", "reason").count().orderBy("table", "reason")

    res = RESULTS_DIR / "preparation"
    res.mkdir(parents=True, exist_ok=True)
    (res / "cleaning_summary.md").write_text(to_markdown(summary))
    (res / "cleaning_flags.md").write_text(to_markdown(flagged))
    (res / "cleaning_quarantine.md").write_text(to_markdown(reasons))
    for df in (summary, flagged, reasons):
        df.show(50, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
