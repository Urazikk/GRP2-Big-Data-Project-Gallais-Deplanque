"""Result tables of a streaming run (batch Spark job on the outputs of the consumer).

Reads data/streaming/{matched_events, windows, volume} and metrics.jsonl and writes
markdown tables to results/streaming/:
- run_summary: events seen, events matched to IMDb, share, entries per kind;
- top_entries: the IMDb entries whose pages changed the most;
- windows: per tumbling window, all changes against matched changes;
- query_metrics: per streaming query, batches, rows, input and processing rates, batch
  duration, state size and rows dropped by the watermark (late data);
- event_delay: delay between the change on Wikipedia (event time) and its arrival in
  Kafka, which is what the watermark has to absorb.

Usage: python -m imdb_project.streaming.report
"""
import json

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from imdb_project.config import RESULTS_DIR
from imdb_project.spark_session import get_spark
from imdb_project.streaming.consumer import METRICS_PATH
from imdb_project.streaming.lookup import STREAMING_DIR


def to_markdown(df: DataFrame) -> str:
    rows = df.collect()
    lines = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    for r in rows:
        lines.append("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
    return "\n".join(lines) + "\n"


def query_metrics(spark, path) -> DataFrame:
    """One row per streaming query from the recorded micro-batch progresses."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            state = p.get("stateOperators") or []
            rows.append((
                p["name"], p["batchId"], p.get("numInputRows", 0),
                float(p.get("inputRowsPerSecond") or 0.0),
                float(p.get("processedRowsPerSecond") or 0.0),
                int((p.get("durationMs") or {}).get("triggerExecution", 0)),
                sum(int(s.get("numRowsTotal", 0)) for s in state),
                sum(int(s.get("numRowsDroppedByWatermark", 0)) for s in state),
                (p.get("eventTime") or {}).get("watermark"),
            ))
    df = spark.createDataFrame(rows, "query string, batch long, input_rows long, "
                                     "input_rows_per_s double, processed_rows_per_s double, "
                                     "batch_ms long, state_rows long, dropped_by_watermark long, "
                                     "watermark string")
    active = df.where("input_rows > 0")
    return (
        df.groupBy("query").agg(
            F.count("*").alias("batches"),
            F.sum("input_rows").alias("input_rows"),
            F.sum("dropped_by_watermark").alias("rows_dropped_by_watermark"),
            F.max("state_rows").alias("max_state_rows"),
            F.max("watermark").alias("last_watermark"))
        .join(active.groupBy("query").agg(
            F.round(F.avg("input_rows_per_s"), 1).alias("avg_input_rows_per_s"),
            F.round(F.avg("processed_rows_per_s"), 1).alias("avg_processed_rows_per_s"),
            F.round(F.avg("batch_ms"), 0).alias("avg_batch_ms"),
            F.max("batch_ms").alias("max_batch_ms")), "query", "left")
        .orderBy("query")
    )


def main():
    spark = get_spark("imdb-streaming-report")
    matched = spark.read.parquet(str(STREAMING_DIR / "matched_events")).cache()
    volume = spark.read.parquet(str(STREAMING_DIR / "volume")).cache()
    windows = spark.read.parquet(str(STREAMING_DIR / "windows"))

    # windows are written once the watermark has passed them, so the last minutes of a run
    # have no closed window: the share is computed over the closed windows only
    total, closed_start, closed_end = volume.agg(
        F.sum("changes"), F.min("window_start"), F.max("window_end")).first()
    total = total or 0
    n_matched = matched.count()
    n_matched_closed = matched.where(
        (F.col("event_time") >= F.lit(closed_start)) & (F.col("event_time") < F.lit(closed_end))
    ).count() if closed_end else 0
    first, last = matched.agg(F.min("event_time"), F.max("event_time")).first()
    summary_rows = [
        ("changes matched to the IMDb dataset (whole run)", str(n_matched)),
        ("first / last matched event time", f"{first} / {last}"),
        ("closed windows (written after the watermark passed them)",
         f"{closed_start} / {closed_end}"),
        ("changes in closed windows (all English Wikipedia articles)", str(total)),
        ("matched changes in closed windows", str(n_matched_closed)),
        ("matched share in closed windows (%)",
         f"{100 * n_matched_closed / total:.2f}" if total else ""),
    ] + [(f"distinct {r.kind} entries matched", str(r.n)) for r in
         matched.groupBy("kind").agg(F.countDistinct("imdb_id").alias("n")).orderBy("kind")
         .collect()]
    tables = {
        "run_summary": spark.createDataFrame(summary_rows, "metric string, value string"),
        "top_entries": (
            matched.groupBy("kind", "imdb_id", "label")
            .agg(F.count("*").alias("changes"), F.countDistinct("user").alias("editors"),
                 F.sum(F.abs("size_delta")).alias("bytes_changed"))
            .orderBy(F.desc("changes"), "label").limit(20)),
        "windows": (
            volume.join(windows.groupBy("window_start").agg(
                F.sum("changes").alias("matched_changes"),
                F.countDistinct("imdb_id").alias("entries")), "window_start", "left")
            .fillna(0, ["matched_changes", "entries"])
            .select("window_start", "window_end", "changes", "bot_changes",
                    "matched_changes", "entries")
            .orderBy("window_start")),
        "query_metrics": query_metrics(spark, METRICS_PATH),
        "event_delay": (
            matched.withColumn("delay_s", F.col("kafka_time").cast("double")
                               - F.col("event_time").cast("double"))
            .agg(F.round(F.percentile_approx("delay_s", 0.5, 10000), 1).alias("median_s"),
                 F.round(F.percentile_approx("delay_s", 0.95, 10000), 1).alias("p95_s"),
                 F.round(F.max("delay_s"), 1).alias("max_s"),
                 F.sum((F.col("delay_s") > 60).cast("int")).alias("events_over_1_min"))),
    }
    out = RESULTS_DIR / "streaming"
    out.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        (out / f"{name}.md").write_text(to_markdown(df))
        print(name)
        df.show(30, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
