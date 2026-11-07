"""Polite English Wikipedia client (MediaWiki Action API) and wikitext parsing.

Pages are asked for in batches (up to 50 titles per request) to keep the number of
requests low:
- a User-Agent with a contact address (config.USER_AGENT) and maxlag=5;
- one request at a time, at most one every MIN_INTERVAL seconds;
- retries with backoff on 429 and 5xx (and maxlag errors), honouring Retry-After;
- a local SQLite cache keyed by request URL, so a request is never sent twice.

A page is accepted for a film or a person only if it links to its IMDb id.
"""
import json
import re
import sqlite3
import time
from datetime import datetime, timezone
from urllib.parse import quote, urlencode

import mwparserfromhell
import requests

from imdb_project.config import USER_AGENT

API = "https://en.wikipedia.org/w/api.php"
WIKI = "https://en.wikipedia.org/wiki/"
MIN_INTERVAL = 0.2
MAX_RETRIES = 8
TITLES_PER_REQUEST = 50
CONTENT_PER_REQUEST = 20
EXTRACTS_PER_REQUEST = 20
PLOT_SECTIONS = r"^\s*(Plot|Synopsis|Plot summary|Premise|Story|Summary)\s*$"
IMDB_ID = re.compile(r"/(?:title|name)/((?:tt|nm)\d+)")

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


def chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


class WikipediaClient:
    """Action API client with rate limit, retries and a persistent cache."""

    def __init__(self, cache_path, min_interval: float = MIN_INTERVAL, session=None):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(cache_path))
        self.db.execute("CREATE TABLE IF NOT EXISTS cache (url TEXT PRIMARY KEY, "
                        "payload TEXT, fetched_at TEXT)")
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.min_interval = min_interval
        self._last = 0.0
        self.requests = 0

    def _get(self, url: str) -> dict:
        for attempt in range(MAX_RETRIES):
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            self.requests += 1
            try:
                resp = self.session.get(url, timeout=90)
            except requests.RequestException:
                time.sleep(2 ** attempt)
                continue
            if resp.status_code in (429, 500, 502, 503, 504):
                retry = resp.headers.get("Retry-After", "")
                time.sleep(int(retry) if retry.isdigit() else 2 ** (attempt + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            if data.get("error", {}).get("code") == "maxlag":
                time.sleep(int(resp.headers.get("Retry-After", "5") or 5))
                continue
            return data
        raise RuntimeError(f"giving up on {url} after {MAX_RETRIES} attempts")

    def call(self, **params):
        """One API request (cached). Returns (json, fetched_at)."""
        params = {"action": "query", "format": "json", "formatversion": "2",
                  "maxlag": "5", **params}
        url = API + "?" + urlencode(sorted(params.items()))
        row = self.db.execute("SELECT payload, fetched_at FROM cache WHERE url = ?",
                              (url,)).fetchone()
        if row:
            return json.loads(row[0]), row[1]
        data = self._get(url)
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.db.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, ?)",
                        (url, json.dumps(data), fetched_at))
        self.db.commit()
        return data, fetched_at

    def query(self, titles, **params):
        """Query a batch of titles, following continuations.

        Returns ({requested title: final page dict or None}, fetched_at).
        """
        pages, resolve, fetched_at, cont = {}, {}, None, {}
        while True:
            data, fetched_at = self.call(titles="|".join(titles), redirects="1",
                                         **params, **cont)
            q = data.get("query", {})
            for step in ("normalized", "redirects"):
                for r in q.get(step, []):
                    resolve[r["from"]] = r["to"]
            for p in q.get("pages", []):
                merged = pages.setdefault(p["title"], p)
                if merged is not p:
                    for key, value in p.items():
                        if isinstance(value, list):
                            merged.setdefault(key, []).extend(value)
                        else:
                            merged.setdefault(key, value)
            if "continue" not in data:
                break
            cont = {k: v for k, v in data["continue"].items()}
        out = {}
        for t in titles:
            final = t
            for _ in range(3):
                final = resolve.get(final, final)
            page = pages.get(final)
            out[t] = page if page and not page.get("missing") and not page.get("invalid") \
                else None
        return out, fetched_at

    def imdb_pages(self, titles, kind: str):
        """For each title: (final title, set of IMDb ids linked) or None.

        kind is "title" or "name". Disambiguation pages count as missing.
        """
        result = {}
        unique = list(dict.fromkeys(titles))
        for batch in chunks(unique, TITLES_PER_REQUEST):
            pages, _ = self.query(batch, prop="pageprops|extlinks", ppprop="disambiguation",
                                  elquery=f"www.imdb.com/{kind}/", ellimit="max")
            for t, page in pages.items():
                if page is None or "disambiguation" in page.get("pageprops", {}):
                    result[t] = None
                else:
                    ids = {m for link in page.get("extlinks", [])
                           for m in IMDB_ID.findall(link.get("url", ""))}
                    result[t] = (page["title"], ids)
        return result

    def wikitexts(self, titles):
        """{title: (wikitext, fetched_at)} for existing pages."""
        out = {}
        for batch in chunks(list(dict.fromkeys(titles)), CONTENT_PER_REQUEST):
            pages, fetched_at = self.query(batch, prop="revisions", rvprop="content",
                                           rvslots="main")
            for t, page in pages.items():
                if page and page.get("revisions"):
                    out[t] = (page["revisions"][0]["slots"]["main"]["content"], fetched_at)
        return out

    def intros(self, titles):
        """{title: (plain text introduction, fetched_at)} for existing pages."""
        out = {}
        for batch in chunks(list(dict.fromkeys(titles)), EXTRACTS_PER_REQUEST):
            pages, fetched_at = self.query(batch, prop="extracts", exintro="1",
                                           explaintext="1", exlimit="max")
            for t, page in pages.items():
                if page and page.get("extract"):
                    out[t] = (page["extract"], fetched_at)
        return out


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


def _plain(wikicode) -> str:
    """Wikitext to plain text: no references, files, templates or markup."""
    for tag in wikicode.filter_tags(recursive=True,
                                    matches=lambda t: str(t.tag).lower() == "ref"):
        try:
            wikicode.remove(tag)
        except ValueError:
            pass
    for link in wikicode.filter_wikilinks(recursive=False):
        if str(link.title).strip().lower().startswith(("file:", "image:", "category:")):
            wikicode.remove(link)
    text = wikicode.strip_code(normalize=True, collapse=True)
    return "\n".join(line.strip() for line in text.split("\n") if line.strip())


SECTION_START = re.compile(r"^==\s*(Plot|Synopsis|Plot summary|Premise|Story|Summary)\s*==\s*$",
                           re.M)
NEXT_SECTION = re.compile(r"^==[^=]", re.M)


def plot_section(wikitext: str):
    """(plot text, section heading) from a film page, or ("", None)."""
    start = SECTION_START.search(wikitext)
    if not start:
        return "", None
    end = NEXT_SECTION.search(wikitext, start.end())
    # parse only the plot section: parsing whole pages is slow
    code = mwparserfromhell.parse(wikitext[start.start(): end.start() if end else None])
    for section in code.get_sections(levels=[2], matches=PLOT_SECTIONS):
        heading = str(section.filter_headings()[0].title).strip()
        body = mwparserfromhell.parse(str(section))
        body.remove(body.filter_headings()[0])
        return _plain(body), heading
    return "", None


def infobox_languages(wikitext: str) -> list:
    """Languages listed in the film infobox, in order."""
    head = NEXT_SECTION.search(wikitext)
    code = mwparserfromhell.parse(wikitext[: head.start() if head else None])
    for template in code.filter_templates(recursive=False):
        if str(template.name).strip().lower().startswith("infobox film"):
            if not template.has("language"):
                return []
            value = mwparserfromhell.parse(str(template.get("language").value))
            for tag in value.filter_tags(recursive=True,
                                         matches=lambda t: str(t.tag).lower() == "ref"):
                value.remove(tag)
            text = value.strip_code(keep_template_params=True)
            text = re.sub(r"<br\s*/?>", "\n", str(text), flags=re.I)
            items = re.split(r"[\n*,;]+", text)
            return [i.strip() for i in items if i.strip() and i.strip().lower() not in
                    ("plainlist", "ubl", "unbulleted list", "hlist", "flatlist")]
    return []
