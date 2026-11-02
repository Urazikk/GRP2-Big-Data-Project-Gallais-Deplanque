"""Spark session factory used by every job and notebook."""
import pyspark
from pyspark.sql import SparkSession

KAFKA_PACKAGE = f"org.apache.spark:spark-sql-kafka-0-10_2.13:{pyspark.__version__}"


def get_spark(app_name="imdb-project", with_kafka=False, driver_memory="4g"):
    """Return a local SparkSession, with the Kafka connector if requested."""
    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", driver_memory)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "16")
    )
    if with_kafka:
        builder = builder.config("spark.jars.packages", KAFKA_PACKAGE)
    return builder.getOrCreate()
