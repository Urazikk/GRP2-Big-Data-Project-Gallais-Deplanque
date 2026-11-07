"""Download the IMDb non-commercial datasets into data/raw.

Usage: python scripts/download_imdb.py [--force] [--tables title.basics title.ratings]
"""
import argparse
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from imdb_project.config import IMDB_BASE_URL, IMDB_TABLES, RAW_DIR, USER_AGENT  # noqa: E402


def download(table, force=False):
    target = RAW_DIR / f"{table}.tsv.gz"
    if target.exists() and not force:
        print(f"{target.name} already there, skipped")
        return
    url = f"{IMDB_BASE_URL}/{table}.tsv.gz"
    tmp = target.with_suffix(".part")
    with requests.get(url, stream=True, timeout=60, headers={"User-Agent": USER_AGENT}) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    tmp.rename(target)
    print(f"{target.name} downloaded ({target.stat().st_size / 1e6:.0f} MB)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", nargs="+", default=IMDB_TABLES, choices=IMDB_TABLES)
    parser.add_argument("--force", action="store_true", help="download again if present")
    args = parser.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for table in args.tables:
        download(table, args.force)


if __name__ == "__main__":
    main()
