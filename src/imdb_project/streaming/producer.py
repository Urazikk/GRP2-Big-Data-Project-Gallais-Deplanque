"""Read the Wikimedia recent changes stream and send the kept events to Kafka.

The Server-Sent Events stream (stream.wikimedia.org) is read directly with requests-sse,
so no Wikimedia account or library configuration is needed. Filters on the producer side
only reduce the volume (wikis, change types, namespaces); deciding which events are about
the IMDb dataset is done by the Spark consumer, where the IMDb tables are available.

Records are sent as JSON with the page title as key, so every change of a given page goes
to the same partition and keeps its order. A delivery callback counts failures, and the
producer is configured as idempotent so that retries do not create duplicates in Kafka.

--since-minutes N replays the stream from N minutes ago (Wikimedia keeps a few days of
history): replayed events have an old event time and arrive late on purpose, which is used
to test how the consumer handles late data.

Usage: python -m imdb_project.streaming.producer [--minutes 20] [--since-minutes 0]
"""
import argparse
import json
import socket
import time
from datetime import datetime, timedelta, timezone

from confluent_kafka import Producer
from requests_sse import EventSource

from imdb_project.config import KAFKA_BOOTSTRAP_SERVERS, USER_AGENT
from imdb_project.streaming.admin import TOPIC

STREAM_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
DEFAULT_WIKIS = ["en.wikipedia.org"]
DEFAULT_TYPES = ["edit", "new"]
DEFAULT_NAMESPACES = [0]  # articles only (no talk, user or template pages)
COMMENT_MAX = 300


def keep(change: dict, wikis, types, namespaces) -> bool:
    """Producer-side filter: wiki, change type and namespace."""
    return (
        change.get("server_name") in wikis
        and change.get("type") in types
        and change.get("namespace") in namespaces
    )


def slim(change: dict) -> dict:
    """Fields used by the consumer (the raw event has many more)."""
    meta = change.get("meta") or {}
    length = change.get("length") or {}
    revision = change.get("revision") or {}
    return {
        "event_id": meta.get("id"),
        "event_dt": meta.get("dt"),
        "timestamp": change.get("timestamp"),
        "server_name": change.get("server_name"),
        "type": change.get("type"),
        "namespace": change.get("namespace"),
        "title": change.get("title"),
        "user": change.get("user"),
        "bot": change.get("bot"),
        "minor": change.get("minor"),
        "length_old": length.get("old"),
        "length_new": length.get("new"),
        "revision_old": revision.get("old"),
        "revision_new": revision.get("new"),
        "comment": (change.get("comment") or "")[:COMMENT_MAX],
    }


def stream_url(since_minutes: float) -> str:
    if since_minutes <= 0:
        return STREAM_URL
    since = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
    return f"{STREAM_URL}?since={since.strftime('%Y-%m-%dT%H:%M:%SZ')}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minutes", type=float, default=20, help="how long to stream")
    parser.add_argument("--since-minutes", type=float, default=0,
                        help="replay from N minutes ago (late data test)")
    parser.add_argument("--wikis", nargs="+", default=DEFAULT_WIKIS)
    parser.add_argument("--types", nargs="+", default=DEFAULT_TYPES)
    parser.add_argument("--namespaces", type=int, nargs="+", default=DEFAULT_NAMESPACES)
    parser.add_argument("--topic", default=TOPIC)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    producer = Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "client.id": socket.gethostname(),
        "enable.idempotence": True,
        "compression.type": "lz4",
    })
    stats = {"read": 0, "kept": 0, "delivered": 0, "failed": 0}

    def on_delivery(err, _msg):
        stats["failed" if err else "delivered"] += 1

    stop_at = time.monotonic() + args.minutes * 60
    url = stream_url(args.since_minutes)
    last_id = None
    print(f"reading {url} for {args.minutes} min, wikis={args.wikis}, types={args.types}, "
          f"namespaces={args.namespaces}")
    while time.monotonic() < stop_at:
        try:
            headers = {"User-Agent": USER_AGENT}
            if last_id:  # resume where the connection was cut
                headers["Last-Event-ID"] = last_id
            with EventSource(url, timeout=30, headers=headers) as source:
                for event in source:
                    if time.monotonic() >= stop_at:
                        break
                    if event.type != "message" or not event.data:
                        continue
                    last_id = event.last_event_id or last_id
                    change = json.loads(event.data)
                    stats["read"] += 1
                    if not keep(change, args.wikis, args.types, args.namespaces):
                        continue
                    record = slim(change)
                    producer.produce(args.topic, key=(record["title"] or "").encode("utf-8"),
                                     value=json.dumps(record).encode("utf-8"),
                                     callback=on_delivery)
                    producer.poll(0)
                    stats["kept"] += 1
                    if not args.quiet and stats["kept"] % 200 == 0:
                        print(f"{stats['kept']} kept out of {stats['read']} read, "
                              f"last event {record['event_dt']}")
        except Exception as exc:  # network cut: wait and reconnect with Last-Event-ID
            print(f"stream interrupted ({exc}), reconnecting")
            time.sleep(5)
    producer.flush(60)
    print(f"done: {stats}")


if __name__ == "__main__":
    main()
