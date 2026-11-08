"""Collect film synopses, film languages and biographies from English Wikipedia.

Reads the scope written by imdb_project.enrichment.scope and writes raw records (one
JSON object per line) with their source URL and fetch time. When something cannot be
found, the record keeps a note written by the program instead of the text.

Steps, each in batches of titles:
1. film pages: candidate titles, kept only if the page links to the film's IMDb id;
2. their wikitext: plot section and infobox languages;
3. people: the first BIOS_PER_FILM principals of each film, then the next ones for the
   films that still have fewer than BIOS_PER_FILM biographies;
4. their introductions, used as biographies.

Collection runs outside Spark; cleaning and joins are done in Spark by
imdb_project.enrichment.build. Every answer is cached, so the command can be stopped and
started again without sending the same request twice.

Usage: python -m imdb_project.enrichment.collect [--limit N]
"""
import argparse
import json
from collections import defaultdict

from imdb_project.config import ENRICHED_DIR
from imdb_project.enrichment.wikipedia import (
    WikipediaClient,
    film_candidates,
    infobox_languages,
    page_url,
    person_candidates,
    plot_section,
)

# This module does not import Spark, so it can run on any machine with requests
SCOPE_DIR = ENRICHED_DIR / "scope"
RAW_DIR = ENRICHED_DIR / "raw"
CACHE_PATH = ENRICHED_DIR / "cache" / "wikipedia_api.sqlite"
BIOS_PER_FILM = 3
MAX_ORDERING = 5


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def match(candidates_by_key, ids_by_key, found):
    """First candidate whose page links to the key's IMDb id.

    Returns {key: (page title, None)} or {key: (None, note)}.
    """
    out = {}
    for key, candidates in candidates_by_key.items():
        out[key] = (None, f"no English Wikipedia page found for: {', '.join(candidates)}")
        seen = False
        for c in candidates:
            hit = found.get(c)
            if hit is None:
                continue
            seen = True
            title, ids = hit
            if ids_by_key[key] in ids:
                out[key] = (title, None)
                break
        if out[key][0] is None and seen:
            out[key] = (None, f"no English Wikipedia page linking to {ids_by_key[key]} "
                              f"among: {', '.join(candidates)}")
    return out


def collect_films(client, films):
    candidates = {f["tconst"]: film_candidates(f["primaryTitle"], f["originalTitle"],
                                               f["startYear"]) for f in films}
    found = client.imdb_pages([c for cs in candidates.values() for c in cs], "title")
    matched = match(candidates, {t: t for t in candidates}, found)
    print(f"films: {sum(1 for t, _ in matched.values() if t)}/{len(films)} pages found, "
          f"{client.requests} requests", flush=True)
    texts = client.wikitexts([t for t, _ in matched.values() if t])
    records = []
    for f in films:
        title, note = matched[f["tconst"]]
        record = {"tconst": f["tconst"], "page_title": title,
                  "source_url": page_url(title) if title else None, "retrieved_at": None,
                  "synopsis": None, "synopsis_section": None, "languages": [], "note": note}
        if title and title in texts:
            wikitext, fetched_at = texts[title]
            plot, heading = plot_section(wikitext)
            record.update(retrieved_at=fetched_at, languages=infobox_languages(wikitext))
            if plot:
                record.update(synopsis=plot, synopsis_section=heading)
            else:
                record["note"] = "page found but it has no plot or synopsis section"
        elif title:
            record["note"] = "page found but its content could not be read"
        records.append(record)
    return records


def collect_people(client, credits):
    candidates = {c["nconst"]: person_candidates(c["primaryName"], c["category"])
                  for c in credits}
    found = client.imdb_pages([c for cs in candidates.values() for c in cs], "name")
    matched = match(candidates, {n: n for n in candidates}, found)
    intros = client.intros([t for t, _ in matched.values() if t])
    records = {}
    for nconst, (title, note) in matched.items():
        record = {"nconst": nconst, "page_title": title,
                  "source_url": page_url(title) if title else None, "retrieved_at": None,
                  "biography": None, "note": note}
        if title and title in intros:
            record.update(biography=intros[title][0], retrieved_at=intros[title][1])
        elif title:
            record["note"] = "page found but its introduction is empty"
        records[nconst] = record
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="only the first N films")
    parser.add_argument("--people-only", action="store_true",
                        help="only fetch people (film pages are read in a later run)")
    args = parser.parse_args()

    films = read_jsonl(SCOPE_DIR / "films.jsonl")
    if args.limit:
        films = films[: args.limit]
    credits = defaultdict(list)
    for c in read_jsonl(SCOPE_DIR / "people.jsonl"):
        credits[c["tconst"]].append(c)

    client = WikipediaClient(CACHE_PATH)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    films_path = RAW_DIR / "films.jsonl"
    done = read_jsonl(films_path) if films_path.exists() else []
    if args.people_only:
        film_records = None
    elif [r["tconst"] for r in done] == [f["tconst"] for f in films]:
        film_records = done  # films already collected by a previous run
    else:
        film_records = collect_films(client, films)
        with open(films_path, "w", encoding="utf-8") as out:
            for record in film_records:
                out.write(json.dumps(record, ensure_ascii=False) + "\n")

    need = [f["tconst"] for f in films if f["need_people"]]
    people = {}
    for rank in range(1, MAX_ORDERING + 1):
        # ordering 1..3 first, then 4 and 5 only for films still missing biographies
        wanted = []
        for t in need:
            ordered = sorted(credits[t], key=lambda c: c["ordering"])
            found = sum(1 for c in ordered if c["nconst"] in people
                        and people[c["nconst"]]["biography"])
            if rank > BIOS_PER_FILM and found >= BIOS_PER_FILM:
                continue
            wanted += [c for c in ordered if c["ordering"] == rank
                       and c["nconst"] not in people]
        if wanted:
            people.update(collect_people(client, wanted))
        print(f"people rank {rank}: {len(people)} looked up, {client.requests} requests",
              flush=True)

    if film_records is None:
        print(f"{len(people)} people looked up, {client.requests} requests sent")
        return
    with open(RAW_DIR / "people.jsonl", "w", encoding="utf-8") as out:
        for record in people.values():
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"{len(film_records)} films and {len(people)} people written to {RAW_DIR}, "
          f"{client.requests} requests sent")


if __name__ == "__main__":
    main()
