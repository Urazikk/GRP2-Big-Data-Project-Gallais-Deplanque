"""Clean the collected Wikipedia records and join them with IMDb, in Spark.

Inputs: the scope (imdb_project.enrichment.scope) and the raw records
(imdb_project.enrichment.collect). Outputs, with an imposed schema:
- data/enriched/films: one row per top film with its synopsis, original languages and
  the biographies of its principals, each with its source URL (lineage) or a note;
- data/enriched/film_languages: original languages of every fetched film.

Usage: python -m imdb_project.enrichment.build
"""
from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

from imdb_project.config import ENRICHED_DIR, RESULTS_DIR
from imdb_project.enrichment.collect import RAW_DIR, SCOPE_DIR
from imdb_project.exploration.common import to_markdown
from imdb_project.imdb_io import read_imdb
from imdb_project.spark_session import get_spark

RAW_FILM_SCHEMA = T.StructType([
    T.StructField("tconst", T.StringType(), False),
    T.StructField("page_title", T.StringType()),
    T.StructField("source_url", T.StringType()),
    T.StructField("retrieved_at", T.StringType()),
    T.StructField("synopsis", T.StringType()),
    T.StructField("synopsis_section", T.StringType()),
    T.StructField("languages", T.ArrayType(T.StringType())),
    T.StructField("note", T.StringType()),
])

RAW_PERSON_SCHEMA = T.StructType([
    T.StructField("nconst", T.StringType(), False),
    T.StructField("page_title", T.StringType()),
    T.StructField("source_url", T.StringType()),
    T.StructField("retrieved_at", T.StringType()),
    T.StructField("biography", T.StringType()),
    T.StructField("note", T.StringType()),
])

CREDIT_SCHEMA = T.StructType([
    T.StructField("tconst", T.StringType(), False),
    T.StructField("ordering", T.IntegerType()),
    T.StructField("nconst", T.StringType(), False),
    T.StructField("category", T.StringType()),
    T.StructField("primaryName", T.StringType()),
    T.StructField("primaryProfession", T.StringType()),
])

PRINCIPAL_TYPE = T.StructType([
    T.StructField("ordering", T.IntegerType()),
    T.StructField("nconst", T.StringType()),
    T.StructField("name", T.StringType()),
    T.StructField("category", T.StringType()),
    T.StructField("biography", T.StringType()),
    T.StructField("source_url", T.StringType()),
    T.StructField("retrieved_at", T.TimestampType()),
    T.StructField("note", T.StringType()),
])

ENRICHED_SCHEMA = T.StructType([
    T.StructField("tconst", T.StringType(), False),
    T.StructField("title", T.StringType()),
    T.StructField("year", T.IntegerType()),
    T.StructField("runtime_minutes", T.IntegerType()),
    T.StructField("genres", T.ArrayType(T.StringType())),
    T.StructField("top_genres", T.ArrayType(T.StringType())),
    T.StructField("average_rating", T.DoubleType()),
    T.StructField("num_votes", T.IntegerType()),
    T.StructField("synopsis", T.StringType()),
    T.StructField("synopsis_source_url", T.StringType()),
    T.StructField("synopsis_retrieved_at", T.TimestampType()),
    T.StructField("synopsis_note", T.StringType()),
    T.StructField("original_languages", T.ArrayType(T.StringType())),
    T.StructField("principals", T.ArrayType(PRINCIPAL_TYPE)),
    T.StructField("biographies_found", T.IntegerType()),
])

# citation markers left by the HTML text: [1], [ 12 ], [a], [note 3], [citation needed]
CITATION = r"\[\s*(?:\d+|[a-z]|note \d+|nb \d+|citation needed|clarification needed)\s*\]"


def clean_text(col: Column) -> Column:
    """Remove citation markers, normalise spaces, empty text becomes null."""
    text = F.regexp_replace(col, CITATION, "")
    text = F.regexp_replace(text, r"[ \t ]+", " ")
    text = F.regexp_replace(text, r" +([,.;:)])", "$1")
    text = F.regexp_replace(text, r"\( +", "(")
    text = F.trim(F.regexp_replace(text, r"\s*\n\s*", "\n"))
    return F.when(F.length(text) > 0, text)


def _language(x: Column) -> Column:
    """'Silent film with Swedish intertitles' -> 'Swedish'; other names are trimmed."""
    x = F.trim(F.regexp_replace(x, CITATION, ""))
    intertitles = F.regexp_extract(x, r"([A-Z][a-z]+) intertitles", 1)
    return F.when(x.rlike(r"(?i)\bsilent\b"),
                  F.when(intertitles != "", intertitles).otherwise(F.lit("Silent"))
                  ).otherwise(x)


def clean_languages(col: Column) -> Column:
    """Clean infobox language names, dropping empty items and duplicates."""
    return F.array_distinct(F.filter(F.transform(col, _language), lambda x: F.length(x) > 0))


def read_raw(spark: SparkSession, path, schema) -> DataFrame:
    return spark.read.schema(schema).json(str(path))


def clean_films(raw: DataFrame) -> DataFrame:
    return raw.select(
        "tconst",
        clean_text(F.col("synopsis")).alias("synopsis"),
        "source_url",
        F.to_timestamp("retrieved_at").alias("retrieved_at"),
        F.coalesce(
            "note",
            F.when(clean_text(F.col("synopsis")).isNull() & F.col("source_url").isNotNull(),
                   F.lit("synopsis empty after cleaning")),
        ).alias("note"),
        clean_languages(F.coalesce("languages", F.array())).alias("languages"),
    )


def clean_people(raw: DataFrame) -> DataFrame:
    bio = clean_text(F.col("biography"))
    return raw.select(
        "nconst",
        bio.alias("biography"),
        "source_url",
        F.to_timestamp("retrieved_at").alias("retrieved_at"),
        F.coalesce("note", F.when(bio.isNull() & F.col("source_url").isNotNull(),
                                  F.lit("biography empty after cleaning"))).alias("note"),
    )


def enriched_films(top: DataFrame, basics: DataFrame, ratings: DataFrame, films: DataFrame,
                   credits: DataFrame, people: DataFrame) -> DataFrame:
    """Join everything into one row per top film, with the imposed schema."""
    principals = (
        credits.join(people, "nconst")  # only the people the collector looked up
        .groupBy("tconst")
        .agg(
            F.array_sort(F.collect_list(F.struct(
                F.col("ordering").cast("int").alias("ordering"),
                F.col("nconst"),
                F.col("primaryName").alias("name"),
                F.col("category"),
                F.col("biography"),
                F.col("source_url"),
                F.col("retrieved_at"),
                F.col("note"),
            ))).alias("principals")
        )
        .withColumn("biographies_found",
                    F.size(F.filter("principals", lambda p: p["biography"].isNotNull())))
    )
    df = (
        top.join(basics, "tconst")
        .join(ratings, "tconst", "left")
        .join(films, "tconst", "left")
        .join(principals, "tconst", "left")
        .select(
            "tconst",
            F.col("primaryTitle").alias("title"),
            F.col("startYear").alias("year"),
            F.col("runtimeMinutes").alias("runtime_minutes"),
            F.split("genres", ",").alias("genres"),
            F.array_sort("top_genres").alias("top_genres"),
            F.col("averageRating").alias("average_rating"),
            F.col("numVotes").alias("num_votes"),
            "synopsis",
            F.col("source_url").alias("synopsis_source_url"),
            F.col("retrieved_at").alias("synopsis_retrieved_at"),
            F.coalesce("note", F.when(F.col("source_url").isNull() & F.col("synopsis").isNull(),
                                      F.lit("film not collected"))).alias("synopsis_note"),
            F.coalesce("languages", F.array().cast("array<string>")).alias("original_languages"),
            F.coalesce("principals", F.array().cast(T.ArrayType(PRINCIPAL_TYPE)))
            .alias("principals"),
            F.coalesce("biographies_found", F.lit(0)).cast("int").alias("biographies_found"),
        )
    )
    return conform(df, ENRICHED_SCHEMA)


def conform(df: DataFrame, schema: T.StructType) -> DataFrame:
    """Cast to the target schema and fail if a column is missing or extra."""
    if [f.name for f in df.schema] != [f.name for f in schema]:
        raise ValueError(f"columns {df.columns} do not match {schema.fieldNames()}")
    out = df.select([F.col(f.name).cast(f.dataType).alias(f.name) for f in schema])
    for got, want in zip(out.schema, schema):
        if got.dataType != want.dataType:
            raise ValueError(f"{got.name}: {got.dataType} instead of {want.dataType}")
    return out


def coverage(enriched: DataFrame) -> DataFrame:
    """Share of top films with a synopsis, languages and three biographies."""
    return enriched.agg(
        F.count("*").alias("films"),
        F.sum(F.col("synopsis").isNotNull().cast("int")).alias("with_synopsis"),
        F.sum((F.size("original_languages") > 0).cast("int")).alias("with_languages"),
        F.sum((F.col("biographies_found") >= 3).cast("int")).alias("with_3_biographies"),
        F.round(F.avg("biographies_found"), 2).alias("avg_biographies"),
    )


def main():
    spark = get_spark("imdb-enrichment-build")
    top = spark.read.parquet(str(SCOPE_DIR / "top_films"))
    credits = spark.read.schema(CREDIT_SCHEMA).json(str(SCOPE_DIR / "people.jsonl"))
    films = clean_films(read_raw(spark, RAW_DIR / "films.jsonl", RAW_FILM_SCHEMA)).cache()
    people = clean_people(read_raw(spark, RAW_DIR / "people.jsonl", RAW_PERSON_SCHEMA))
    enriched = enriched_films(top, read_imdb(spark, "title.basics"),
                              read_imdb(spark, "title.ratings"), films, credits,
                              people).cache()

    enriched.write.mode("overwrite").parquet(str(ENRICHED_DIR / "films"))
    films.select("tconst", "languages", "source_url").write.mode("overwrite").parquet(
        str(ENRICHED_DIR / "film_languages")
    )
    out = RESULTS_DIR / "enrichment"
    out.mkdir(parents=True, exist_ok=True)
    cov = coverage(enriched)
    (out / "coverage.md").write_text(to_markdown(cov))
    notes = (
        enriched.where(F.col("synopsis").isNull())
        .groupBy(F.regexp_replace("synopsis_note", r":.*", "").alias("synopsis_note"))
        .count().orderBy(F.desc("count"))
    )
    (out / "missing_synopsis_notes.md").write_text(to_markdown(notes))
    enriched.printSchema()
    cov.show()
    spark.stop()


if __name__ == "__main__":
    main()
