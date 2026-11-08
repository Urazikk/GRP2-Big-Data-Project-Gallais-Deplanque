"""Create the Kafka topic of the streaming part.

Three partitions: the producer uses the page title as key, so all the changes of a page
stay in one partition and in order, while the consumer can read the topic in parallel.

Usage: python -m imdb_project.streaming.admin [--partitions 3] [--delete]
"""
import argparse

from confluent_kafka.admin import AdminClient, NewTopic

from imdb_project.config import KAFKA_BOOTSTRAP_SERVERS

TOPIC = "wikipedia-changes"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default=TOPIC)
    parser.add_argument("--partitions", type=int, default=3)
    parser.add_argument("--delete", action="store_true", help="delete the topic instead")
    args = parser.parse_args()

    admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
    if args.delete:
        futures = admin.delete_topics([args.topic])
    else:
        futures = admin.create_topics(
            [NewTopic(args.topic, num_partitions=args.partitions, replication_factor=1)])
    for name, future in futures.items():
        try:
            future.result()
            print(f"topic {name} {'deleted' if args.delete else 'created'}")
        except Exception as exc:  # e.g. TOPIC_ALREADY_EXISTS
            print(f"topic {name}: {exc}")
    print("topics:", sorted(admin.list_topics(timeout=10).topics))


if __name__ == "__main__":
    main()
