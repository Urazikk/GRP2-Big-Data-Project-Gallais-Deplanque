"""Read the raw IMDb TSV files with an explicit schema."""
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from imdb_project.config import RAW_DIR


def _schema(*fields):
    return StructType([StructField(name, dtype, True) for name, dtype in fields])


S, I, D = StringType(), IntegerType(), DoubleType()

SCHEMAS = {
    "name.basics": _schema(
        ("nconst", S), ("primaryName", S), ("birthYear", I), ("deathYear", I),
        ("primaryProfession", S), ("knownForTitles", S),
    ),
    "title.akas": _schema(
        ("titleId", S), ("ordering", I), ("title", S), ("region", S),
        ("language", S), ("types", S), ("attributes", S), ("isOriginalTitle", I),
    ),
    "title.basics": _schema(
        ("tconst", S), ("titleType", S), ("primaryTitle", S), ("originalTitle", S),
        ("isAdult", I), ("startYear", I), ("endYear", I), ("runtimeMinutes", I),
        ("genres", S),
    ),
    "title.crew": _schema(("tconst", S), ("directors", S), ("writers", S)),
    "title.episode": _schema(
        ("tconst", S), ("parentTconst", S), ("seasonNumber", I), ("episodeNumber", I),
    ),
    "title.principals": _schema(
        ("tconst", S), ("ordering", I), ("nconst", S), ("category", S),
        ("job", S), ("characters", S),
    ),
    "title.ratings": _schema(
        ("tconst", S), ("averageRating", D), ("numVotes", I),
    ),
}


def read_imdb(spark, table, raw_dir=RAW_DIR, typed=True):
    """Read one IMDb table.

    typed=True applies the schema above and turns the IMDb null marker "\\N" into null.
    typed=False keeps every column as a string with "\\N" untouched, which is what the
    data quality analysis needs (a value that fails the cast would otherwise become null).
    """
    if table not in SCHEMAS:
        raise ValueError(f"Unknown IMDb table: {table}")
    schema = SCHEMAS[table]
    if not typed:
        schema = _schema(*[(f.name, S) for f in schema.fields])
    reader = (
        spark.read.option("sep", "\t")
        .option("header", True)
        # IMDb does not quote fields, and titles can contain a lone double quote
        .option("quote", "")
        .schema(schema)
    )
    if typed:
        reader = reader.option("nullValue", "\\N")
    return reader.csv(str(raw_dir / f"{table}.tsv.gz"))
