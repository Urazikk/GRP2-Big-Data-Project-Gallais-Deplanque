"""Polite English Wikipedia client and page parsing.

Only the Wikimedia REST page endpoints are used (summary and Parsoid HTML):
- a User-Agent with a contact address (config.USER_AGENT);
- at most one request every MIN_INTERVAL seconds;
- retries with backoff on 429 and 5xx, honouring Retry-After;
- a local SQLite cache keyed by URL, so a page is never requested twice. Only the parts
  of a page we use are stored (text, languages, IMDb ids), not the full HTML.

A page is accepted for a film or a person only if it links to its IMDb id.
"""
import json
import re
import sqlite3
import time
from datetime import datetime, timezone
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from imdb_project.config import USER_AGENT

REST = "https://en.wikipedia.org/api/rest_v1/page"
WIKI = "https://en.wikipedia.org/wiki/"
MIN_INTERVAL = 0.25
MAX_RETRIES = 6
PLOT_SECTIONS = ("Plot", "Synopsis", "Plot_summary", "Premise", "Story", "Summary")
IMDB_ID = re.compile(r"imdb\.com/(?:title|name)/((?:tt|nm)\d+)")

PERSON_SUFFIXES = {
    "actor": ["", " (actor)"],
    "actress": ["", " (actress)", " (actor)"],
    "director": ["", " (director)", " (filmmaker)"],
    "writer": ["", " (writer)", " (screenwriter)"],
    "producer": ["", " (producer)", " (film producer)"],
    "composer": ["", " (composer)", " (musician)"],
    "cinematographer": ["", " (cinematographer)"],
    "editor": ["", " (film editor)", " (editor)"],
}


def page_url(title: str) -> str:
    """Human-readable URL of a page, used as lineage."""
    return WIKI + quote(title.replace(" ", "_"), safe="()_,'!-.")


def _path(title: str) -> str:
    return quote(title.replace(" ", "_"), safe="")


class WikipediaClient:
    """REST client with rate limit, retries and a persistent cache."""

    def __init__(self, cache_path, min_interval: float = MIN_INTERVAL, session=None):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(cache_path))
        self.db.execute("CREATE TABLE IF NOT EXISTS cache (url TEXT PRIMARY KEY, "
                        "status INTEGER, payload TEXT, fetched_at TEXT)")
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.min_interval = min_interval
        self._last = 0.0
        self.requests = 0

    def _get(self, url: str):
        """GET with rate limit and retries. Returns (status, response or None)."""
        for attempt in range(MAX_RETRIES):
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            self.requests += 1
            try:
                resp = self.session.get(url, timeout=60)
            except requests.RequestException:
                time.sleep(2 ** attempt)
                continue
            if resp.status_code in (429, 500, 502, 503, 504):
                retry = resp.headers.get("Retry-After", "")
                time.sleep(int(retry) if retry.isdigit() else 2 ** (attempt + 1))
                continue
            return resp.status_code, resp
        raise RuntimeError(f"giving up on {url} after {MAX_RETRIES} attempts")

    def cached(self, url: str, parse):
        """Return (status, payload, fetched_at) from the cache, or fetch, parse and store."""
        row = self.db.execute("SELECT status, payload, fetched_at FROM cache WHERE url = ?",
                              (url,)).fetchone()
        if row:
            return row[0], json.loads(row[1]) if row[1] else None, row[2]
        status, resp = self._get(url)
        payload = parse(resp) if status == 200 else None
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.db.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?)",
                        (url, status, json.dumps(payload) if payload else None, fetched_at))
        self.db.commit()
        return status, payload, fetched_at

    def summary(self, title: str):
        """Page summary (type, canonical title), or None if the page does not exist."""
        status, payload, _ = self.cached(
            f"{REST}/summary/{_path(title)}",
            lambda r: {k: r.json().get(k) for k in ("type", "title", "description")},
        )
        return payload if status == 200 else None

    def page(self, title: str):
        """Parsed content of a page (see parse_page) and when it was fetched."""
        status, payload, fetched_at = self.cached(
            f"{REST}/html/{_path(title)}", lambda r: parse_page(r.text)
        )
        return (payload, fetched_at) if status == 200 else (None, fetched_at)

    def find(self, candidates, imdb_id: str):
        """First candidate title whose page links to imdb_id.

        Returns (canonical title, parsed page, fetched_at, note).
        """
        seen = set()
        for candidate in candidates:
            if not candidate:
                continue
            summ = self.summary(candidate)
            if not summ or summ.get("type") == "disambiguation":
                continue
            title = summ["title"]
            if title in seen:
                continue
            seen.add(title)
            page, fetched_at = self.page(title)
            if page and imdb_id in page["imdb_ids"]:
                return title, page, fetched_at, None
        tried = ", ".join(c for c in candidates if c)
        note = (f"no English Wikipedia page linking to {imdb_id} among: {tried}"
                if seen else f"no English Wikipedia page found for: {tried}")
        return None, None, None, note


def film_candidates(primary: str, original: str, year) -> list:
    """Page titles to try for a film, most specific first."""
    titles = list(dict.fromkeys(t for t in (primary, original) if t))
    out = []
    for t in titles:
        if year:
            out.append(f"{t} ({year} film)")
        out.append(f"{t} (film)")
        out.append(t)
    return out


def person_candidates(name: str, category: str) -> list:
    """Page titles to try for a person, from their credit category."""
    if not name:
        return []
    return [name + s for s in PERSON_SUFFIXES.get(category, [""])]


def _paragraphs(section, recursive: bool = False) -> str:
    texts = [p.get_text() for p in section.find_all("p", recursive=recursive)]
    return "\n".join(t.strip() for t in texts if t.strip())


def parse_page(html: str) -> dict:
    """Extract what we keep from a Parsoid page: IMDb ids, lead, plot, infobox languages."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["style", "script"]):
        tag.decompose()
    ids = sorted(set(IMDB_ID.findall(html)))

    lead_section = soup.find("section", attrs={"data-mw-section-id": "0"})
    lead = _paragraphs(lead_section) if lead_section else ""

    plot, plot_section = "", None
    for heading in soup.find_all("h2"):
        if heading.get("id") in PLOT_SECTIONS and heading.parent.name == "section":
            # subsections (h3) of the plot are nested sections, so search recursively
            plot, plot_section = _paragraphs(heading.parent, recursive=True), heading.get("id")
            break

    languages = []
    infobox = soup.find("table", class_="infobox")
    if infobox:
        for row in infobox.find_all("tr"):
            th = row.find("th")
            if th and th.get_text(strip=True) in ("Language", "Languages"):
                td = row.find("td")
                if td:
                    for sup in td.find_all("sup"):
                        sup.decompose()
                    # one language per list item or per line break, links stay whole
                    for br in td.find_all("br"):
                        br.replace_with("\n")
                    items = td.find_all("li") or [td]
                    languages = [x.strip() for item in items
                                 for x in item.get_text().split("\n") if x.strip()]
                break
    return {"imdb_ids": ids, "lead": lead, "plot": plot, "plot_section": plot_section,
            "languages": languages}
