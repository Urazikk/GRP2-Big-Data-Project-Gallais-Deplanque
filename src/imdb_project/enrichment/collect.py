"""Collect film synopses, film languages and biographies from English Wikipedia.

Reads the scope written by imdb_project.enrichment.scope and writes raw records (one
JSON object per line) with their source URL and fetch time. When something cannot be
found, the record keeps a note written by the program instead of the text.

For each film that needs people, principals are tried in credit order until
BIOS_PER_FILM biographies are found.

Collection runs outside Spark; cleaning and joins are done in Spark by
imdb_project.enrichment.build. Every page answer is cached, so the command can be
stopped and started again without sending the same request twice.

Usage: python -m imdb_project.enrichment.collect [--limit N]
"""
import argparse
import json
from collections import defaultdict

from imdb_project.config import ENRICHED_DIR
from imdb_project.enrichment.wikipedia import (
    WikipediaClient,
    film_candidates,
    page_url,
    person_candidates,
)

# This module does not import Spark, so it can run on any machine with requests and bs4
SCOPE_DIR = ENRICHED_DIR / "scope"
RAW_DIR = ENRICHED_DIR / "raw"
CACHE_PATH = ENRICHED_DIR / "cache" / "wikipedia.sqlite"
BIOS_PER_FILM = 3


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def film_record(client, film):
    title, page, fetched_at, note = client.find(
        film_candidates(film["primaryTitle"], film["originalTitle"], film["startYear"]),
        film["tconst"],
    )
    record = {"tconst": film["tconst"], "page_title": title,
              "source_url": page_url(title) if title else None,
              "retrieved_at": fetched_at, "synopsis": None, "synopsis_section": None,
              "languages": [], "note": note}
    if page:
        record["languages"] = page["languages"]
        if page["plot"]:
            record["synopsis"] = page["plot"]
            record["synopsis_section"] = page["plot_section"]
        else:
            record["note"] = "page found but it has no plot or synopsis section"
    return record


def person_record(client, credit):
    title, page, fetched_at, note = client.find(
        person_candidates(credit["primaryName"], credit["category"]), credit["nconst"]
    )
    record = {"nconst": credit["nconst"], "page_title": title,
              "source_url": page_url(title) if title else None,
              "retrieved_at": fetched_at, "biography": None, "note": note}
    if page:
        if page["lead"]:
            record["biography"] = page["lead"]
        else:
            record["note"] = "page found but its introduction is empty"
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="only the first N films")
    args = parser.parse_args()

    films = read_jsonl(SCOPE_DIR / "films.jsonl")
    if args.limit:
        films = films[: args.limit]
    credits = defaultdict(list)
    for c in read_jsonl(SCOPE_DIR / "people.jsonl"):
        credits[c["tconst"]].append(c)

    client = WikipediaClient(CACHE_PATH)
    people = {}
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(RAW_DIR / "films.jsonl", "w", encoding="utf-8") as out:
        for i, film in enumerate(films, 1):
            out.write(json.dumps(film_record(client, film), ensure_ascii=False) + "\n")
            if film["need_people"]:
                found = 0
                for credit in sorted(credits[film["tconst"]], key=lambda c: c["ordering"]):
                    if found >= BIOS_PER_FILM:
                        break
                    if credit["nconst"] not in people:
                        people[credit["nconst"]] = person_record(client, credit)
                    found += people[credit["nconst"]]["biography"] is not None
            if i % 100 == 0:
                print(f"{i}/{len(films)} films, {len(people)} people, "
                      f"{client.requests} requests sent", flush=True)
    with open(RAW_DIR / "people.jsonl", "w", encoding="utf-8") as out:
        for record in people.values():
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"{len(films)} films and {len(people)} people written to {RAW_DIR}, "
          f"{client.requests} requests sent")


if __name__ == "__main__":
    main()
