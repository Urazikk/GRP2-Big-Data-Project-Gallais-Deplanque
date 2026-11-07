"""Spark Structured Streaming consumer: Wikipedia changes relevant to the IMDb dataset.

Pipeline:
1. read the Kafka topic and parse the JSON value with an explicit schema;
2. event time = time of the change on Wikipedia (meta.dt), not the time Spark reads it;
3. late data: a watermark of WATERMARK on the event time; events older than the watermark
   are dropped and counted (numRowsDroppedByWatermark in the metrics), and the state of
   finished windows is freed. Duplicates (same Wikimedia event id, e.g. a producer retry)
   are removed within the watermark;
4. join with the static lookup (page title -> IMDb id), broadcast to every executor;
5. three outputs, each with its checkpoint so a restart neither loses nor repeats events:
   - matched_events: every relevant change (append, parquet);
   - windows: changes per IMDb entry per tumbling window of WINDOW (append, parquet;
     a window is written once the watermark has passed its end);
   - volume: all changes per window, matched or not, to measure the share of relevant
     events (append, parquet).
   Plus a live console view of the windows (update mode).
Every micro-batch progress (input rate, processing rate, rows dropped by the watermark...)
is appended to data/streaming/metrics.jsonl.

Usage: python -m imdb_project.streaming.consumer [--minutes 25] [--watermark "10 minutes"]
       [--window "5 minutes"] [--trigger "30 seconds"]
"""
import argparse
import json
import shutil
import threading
import time

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from imdb_project.config import CHECKPOINT_DIR, KAFKA_BOOTSTRAP_SERVERS
from imdb_project.spark_session import get_spark
from imdb_project.streaming.admin import TOPIC
from imdb_project.streaming.lookup import LOOKUP_PATH, STREAMING_DIR

WATERMARK = "10 minutes"
WINDOW = "5 minutes"
TRIGGER = "30 seconds"
METRICS_PATH = STREAMING_DIR / "metrics.jsonl"

EVENT_SCHEMA = T.StructType([
    T.StructField("event_id", T.StringType()),
    T.StructField("event_dt", T.StringType()),
    T.StructField("timestamp", T.LongType()),
    T.StructField("server_name", T.StringType()),
    T.StructField("type", T.StringType()),
    T.StructField("namespace", T.IntegerType()),
    T.StructField("title", T.StringType()),
    T.StructField("user", T.StringType()),
    T.StructField("bot", T.BooleanType()),
    T.StructField("minor", T.BooleanType()),
    T.StructField("length_old", T.IntegerType()),
    T.StructField("length_new", T.IntegerType()),
    T.StructField("revision_old", T.LongType()),
    T.StructField("revision_new", T.LongType()),
    T.StructField("comment", T.StringType()),
])


def parse(raw: DataFrame) -> DataFrame:
    """Kafka records -> typed change events with their event time and size change."""
    return (
        raw.select(F.from_json(F.col("value").cast("string"), EVENT_SCHEMA).alias("e"),
                   F.col("timestamp").alias("kafka_time"))
        .select("e.*", "kafka_time")
        .withColumn("event_time", F.to_timestamp("event_dt"))
        .withColumn("size_delta",
                    F.coalesce(F.col("length_new"), F.lit(0))
                    - F.coalesce(F.col("length_old"), F.lit(0)))
        .where(F.col("event_time").isNotNull() & F.col("title").isNotNull())
    )


def with_late_data_policy(events: DataFrame, watermark: str = WATERMARK) -> DataFrame:
    """Watermark on the event time and removal of duplicated events within it."""
    return events.withWatermark("event_time", watermark).dropDuplicatesWithinWatermark(
        ["event_id"])


def match(events: DataFrame, lookup: DataFrame) -> DataFrame:
    """Keep the changes whose page title is in the lookup, with their IMDb id."""
    return events.join(F.broadcast(lookup.select("page_title", "imdb_id", "kind", "label",
                                                 "votes")),
                       events["title"] == F.col("page_title"))


def windowed_changes(matched: DataFrame, window: str = WINDOW) -> DataFrame:
    """Changes per IMDb entry per tumbling window."""
    return (
        matched.groupBy(F.window("event_time", window).alias("w"), "kind", "imdb_id", "label")
        .agg(F.count("*").alias("changes"),
             F.approx_count_distinct("user").alias("editors"),
             F.sum(F.col("bot").cast("int")).alias("bot_changes"),
             F.sum(F.abs("size_delta")).alias("bytes_changed"))
        .select(F.col("w.start").alias("window_start"), F.col("w.end").alias("window_end"),
                "kind", "imdb_id", "label", "changes", "editors", "bot_changes",
                "bytes_changed")
    )


def volume(events: DataFrame, window: str = WINDOW) -> DataFrame:
    """All changes per tumbling window, to compare with the matched ones."""
    return (
        events.groupBy(F.window("event_time", window).alias("w"))
        .agg(F.count("*").alias("changes"), F.sum(F.col("bot").cast("int")).alias("bot_changes"))
        .select(F.col("w.start").alias("window_start"), F.col("w.end").alias("window_end"),
                "changes", "bot_changes")
    )


def record_metrics(queries, path, stop: threading.Event, every: float = 5.0):
    """Append the progress of every new micro-batch of every query to a JSON lines file."""
    seen = set()
    with open(path, "a", encoding="utf-8") as out:
        while not stop.is_set():
            for q in queries:
                for p in q.recentProgress:
                    key = (p["name"], p["batchId"])
                    if key not in seen:
                        seen.add(key)
                        out.write(json.dumps(p) + "\n")
            out.flush()
            stop.wait(every)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minutes", type=float, default=25, help="how long to run")
    parser.add_argument("--watermark", default=WATERMARK)
    parser.add_argument("--window", default=WINDOW)
    parser.add_argument("--trigger", default=TRIGGER)
    parser.add_argument("--starting-offsets", default="earliest")
    parser.add_argument("--reset", action="store_true",
                        help="delete previous outputs, checkpoints and metrics first")
    args = parser.parse_args()

    out_dir, ckpt_dir = STREAMING_DIR, CHECKPOINT_DIR / "streaming"
    if args.reset:
        for p in ("matched_events", "windows", "volume"):
            shutil.rmtree(out_dir / p, ignore_errors=True)
        shutil.rmtree(ckpt_dir, ignore_errors=True)
        METRICS_PATH.unlink(missing_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    spark = get_spark("imdb-streaming", with_kafka=True)
    spark.sparkContext.setLogLevel("WARN")
    spark.conf.set("spark.sql.shuffle.partitions", "4")
    lookup = spark.read.parquet(str(LOOKUP_PATH)).cache()
    print(f"lookup: {lookup.count()} page titles")

    raw = (spark.readStream.format("kafka")
           .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
           .option("subscribe", TOPIC)
           .option("startingOffsets", args.starting_offsets)
           .option("failOnDataLoss", "false")
           .load())
    events = with_late_data_policy(parse(raw), args.watermark)
    matched = match(events, lookup)
    windows = windowed_changes(matched, args.window)

    def to_parquet(df, name, mode="append"):
        return (df.writeStream.queryName(name).format("parquet").outputMode(mode)
                .option("path", str(out_dir / name))
                .option("checkpointLocation", str(ckpt_dir / name))
                .trigger(processingTime=args.trigger).start())

    queries = [
        to_parquet(matched.drop("page_title"), "matched_events"),
        to_parquet(windows, "windows"),
        to_parquet(volume(events, args.window), "volume"),
        windows.writeStream.queryName("windows_console").format("console")
        .outputMode("update").option("truncate", "false").option("numRows", 20)
        .trigger(processingTime=args.trigger).start(),
    ]
    stop = threading.Event()
    recorder = threading.Thread(target=record_metrics, args=(queries, METRICS_PATH, stop))
    recorder.start()
    try:
        time.sleep(args.minutes * 60)
    finally:
        for q in queries:
            q.stop()
        stop.set()
        recorder.join()
        spark.stop()
    print(f"outputs in {out_dir}, metrics in {METRICS_PATH}")


if __name__ == "__main__":
    main()
