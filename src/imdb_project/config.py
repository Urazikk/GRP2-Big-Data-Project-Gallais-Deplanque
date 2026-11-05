"""Shared paths and settings, overridable with environment variables."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("IMDB_DATA_DIR", PROJECT_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
ENRICHED_DIR = DATA_DIR / "enriched"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"
# small result tables (markdown) copied into REPORT.md, committed
RESULTS_DIR = PROJECT_ROOT / "results"

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

IMDB_BASE_URL = "https://datasets.imdbws.com"
IMDB_TABLES = [
    "name.basics",
    "title.akas",
    "title.basics",
    "title.crew",
    "title.episode",
    "title.principals",
    "title.ratings",
]

# Wikimedia asks every client to identify itself with a contact address
USER_AGENT = os.environ.get(
    "IMDB_PROJECT_USER_AGENT",
    "ECE-BigData-GRP2-Project/0.1 (simon.gallais@edu.ece.fr)",
)
