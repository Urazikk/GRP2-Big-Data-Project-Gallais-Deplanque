"""Open question, step 2: check each candidate pair on English Wikipedia (outside Spark).

For every remake candidate, the possible page titles ("Title (year film)", "Title (film)",
"Title") are looked up with the MediaWiki action API, 20 titles per request: one request
returns the plain text introduction and the IMDb links of each page. Batching keeps the
number of requests about 20 times lower than one request per page.

Politeness rules (same as the enrichment step): a User-Agent with a contact address, one
request at a time and at least MIN_INTERVAL seconds apart, Retry-After honoured on 429 and
5xx, maxlag to back off when the servers are busy, and a local SQLite cache so that a title
is never requested twice.

A page is accepted for a film only if it links to the film's IMDb id. A pair is confirmed
when one sentence of the introduction of the remake's page calls the film a remake (not
negated) and names the release year of the original. Every record keeps the source URL
and fetch time (lineage), the sentence used as evidence, or a note written by the program
when the page or the sentence is missing.

Usage: python -m imdb_project.open_question.remakes_collect [--limit N]
"""
import argparse
import json
import re
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timezone

import requests

from imdb_project.config import USER_AGENT
from imdb_project.enrichment.collect import read_jsonl
from imdb_project.enrichment.wikipedia import IMDB_ID, film_candidates, page_url
from imdb_project.open_question.remakes_scope import CANDIDATES_PATH, REMAKES_DIR

API = "https://en.wikipedia.org/w/api.php"
CHECKS_PATH = REMAKES_DIR / "checks.jsonl"
CACHE_PATH = REMAKES_DIR / "cache" / "wikipedia_intro.sqlite"
BATCH = 20          # max titles per request for prop=extracts with exintro
MIN_INTERVAL = 1.0
MAX_RETRIES = 8

# "remake" / "re-make" only: "was remade in 1962" talks about a later film, not this one
REMAKE_WORD = re.compile(r"\bre-?make\b", re.IGNORECASE)
NEGATION = re.compile(r"\bnot\b[^.]*\bre-?make\b", re.IGNORECASE)
SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")


def sentences(text: str) -> list:
    return [s.strip() for s in SENTENCE_END.split(text or "") if s.strip()]


def is_remake_of(lead: str, original_year: int):
    """(confirmed, evidence or note) from the introduction of the remake's page.

    Confirmed when one sentence calls the film a remake (not negated) and names the
    release year of the original in the same sentence.
    """
    if not lead:
        return False, "page found but its introduction is empty"
    remake_sentences = [s for s in sentences(lead)
                        if REMAKE_WORD.search(s) and not NEGATION.search(s)]
    if not remake_sentences:
        return False, "introduction does not describe the film as a remake"
    year = re.compile(rf"\b{original_year}\b")
    for s in remake_sentences:
        if year.search(s):
            return True, s
    return False, f"introduction mentions a remake but not of a {original_year} film"


class IntroClient:
    """Batched lookups of page introductions and IMDb links, with a persistent cache.

    The cache maps every requested title to the page it resolves to (after normalisation
    and redirects), or to null when the page does not exist.
    """

    def __init__(self, cache_path=CACHE_PATH, min_interval: float = MIN_INTERVAL,
                 session=None):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(cache_path))
        self.db.execute("CREATE TABLE IF NOT EXISTS titles (asked TEXT PRIMARY KEY, page TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS pages (title TEXT PRIMARY KEY, "
                        "intro TEXT, imdb_ids TEXT, fetched_at TEXT)")
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.min_interval = min_interval
        self._last = 0.0
        self.requests = 0

    def _get(self, params: dict) -> dict:
        for attempt in range(MAX_RETRIES):
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            self.requests += 1
            try:
                resp = self.session.get(API, params=params, timeout=60)
            except requests.RequestException:
                time.sleep(2 ** attempt)
                continue
            retry = resp.headers.get("Retry-After", "")
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(int(retry) if retry.isdigit() else 2 ** (attempt + 1))
                continue
            data = resp.json()
            if data.get("error", {}).get("code") == "maxlag":
                time.sleep(int(retry) if retry.isdigit() else 5)
                continue
            return data
        raise RuntimeError(f"giving up after {MAX_RETRIES} attempts")

    def _fetch(self, titles: list) -> None:
        """Fetch up to BATCH titles and store them in the cache."""
        params = {"action": "query", "format": "json", "formatversion": "2",
                  "redirects": "1", "maxlag": "5",
                  "prop": "extracts|extlinks", "exintro": "1", "explaintext": "1",
                  "exlimit": "max", "ellimit": "max",
                  "elprotocol": "https", "elquery": "www.imdb.com/title/",
                  "titles": "|".join(titles)}
        pages, extract, links = {}, {}, defaultdict(set)
        while True:  # extlinks may need several continuations
            data = self._get(params)
            query = data.get("query", {})
            for p in query.get("pages", []):
                pages[p["title"]] = p
                if p.get("extract"):
                    extract[p["title"]] = p["extract"]
                for link in p.get("extlinks", []):
                    links[p["title"]].update(IMDB_ID.findall(link.get("url", "")))
            if "continue" not in data:
                break
            params = {**params, **data["continue"]}
        # requested title -> final page title, through normalisation and redirects
        mapping = {t: t for t in titles}
        for step in ("normalized", "redirects"):
            for item in query.get(step, []):
                for asked, target in mapping.items():
                    if target == item["from"]:
                        mapping[asked] = item["to"]
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for asked, target in mapping.items():
            page = pages.get(target)
            exists = page is not None and not page.get("missing") and not page.get("invalid")
            self.db.execute("INSERT OR REPLACE INTO titles VALUES (?, ?)",
                            (asked, target if exists else None))
            if exists:
                self.db.execute("INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?)",
                                (target, extract.get(target, ""),
                                 json.dumps(sorted(links[target])), now))
        self.db.commit()

    def prefetch(self, titles) -> None:
        """Fetch every title that is not cached yet, BATCH at a time."""
        known = {r[0] for r in self.db.execute("SELECT asked FROM titles")}
        todo = sorted({t for t in titles if t and t not in known})
        for i in range(0, len(todo), BATCH):
            self._fetch(todo[i:i + BATCH])
            if (i // BATCH) % 20 == 0:
                print(f"{min(i + BATCH, len(todo))}/{len(todo)} titles fetched, "
                      f"{self.requests} requests sent")

    def find(self, candidates: list, imdb_id: str):
        """First candidate whose page links to imdb_id: (title, intro, fetched_at, note)."""
        tried = []
        for asked in candidates:
            if not asked:
                continue
            tried.append(asked)
            row = self.db.execute("SELECT page FROM titles WHERE asked = ?", (asked,)).fetchone()
            if not row or not row[0]:
                continue
            title, intro, ids, fetched_at = self.db.execute(
                "SELECT title, intro, imdb_ids, fetched_at FROM pages WHERE title = ?",
                (row[0],)).fetchone()
            if imdb_id in json.loads(ids):
                return title, intro, fetched_at, None
        return None, None, None, (f"no English Wikipedia page linking to {imdb_id} among: "
                                  + ", ".join(tried))


def candidate_titles(remake: dict) -> list:
    return film_candidates(remake["remake_title"], remake["remake_original_title"],
                           remake["remake_year"])


def check_remake(client, remake: dict, originals: list) -> list:
    """One record per (original, remake) pair of this remake."""
    title, intro, fetched_at, note = client.find(candidate_titles(remake),
                                                 remake["remake_tconst"])
    records = []
    for o in originals:
        record = {"original_tconst": o["original_tconst"],
                  "remake_tconst": remake["remake_tconst"],
                  "page_title": title, "source_url": page_url(title) if title else None,
                  "retrieved_at": fetched_at, "confirmed": False, "evidence": None,
                  "note": note}
        if title:
            ok, text = is_remake_of(intro, o["original_year"])
            record["confirmed"] = ok
            record["evidence"], record["note"] = (text, None) if ok else (None, text)
        records.append(record)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="only the first N remakes")
    args = parser.parse_args()

    by_remake = defaultdict(list)
    for pair in read_jsonl(CANDIDATES_PATH):
        by_remake[pair["remake_tconst"]].append(pair)
    remakes = list(by_remake.values())
    if args.limit:
        remakes = remakes[:args.limit]

    client = IntroClient()
    client.prefetch(t for pairs in remakes for t in candidate_titles(pairs[0]))
    confirmed = 0
    with open(CHECKS_PATH, "w", encoding="utf-8") as out:
        for pairs in remakes:
            for record in check_remake(client, pairs[0], pairs):
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                confirmed += record["confirmed"]
    print(f"{len(remakes)} remakes checked, {confirmed} pairs confirmed, "
          f"{client.requests} requests sent; written to {CHECKS_PATH}")


if __name__ == "__main__":
    main()
