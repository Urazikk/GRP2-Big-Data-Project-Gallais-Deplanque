# Project guide

## Contributors

| Name | Git username | Email |
|------|--------------|-------|
| Simon Gallais | `Urazikk` | simon.gallais@edu.ece.fr |
| Gautier Deplanque | `gautierdpl` | gautier.deplanque@edu.ece.fr |

## Repository layout

| Path | Content |
|------|---------|
| `compose.yaml` | Kafka broker and Jupyter/PySpark container |
| `requirements.txt` | Python dependencies (PySpark is already in the Docker image) |
| `scripts/download_imdb.py` | Downloads the seven IMDb TSV files into `data/raw` |
| `src/imdb_project/` | Shared code: configuration, Spark session, IMDb readers |
| `src/imdb_project/<section>/` | One package per part of the project |
| `notebooks/` | Notebooks that run each part and show the outputs |
| `tests/` | Unit tests (pytest) |
| `data/` | Downloaded and generated data, not committed |

## Environment setup

Two ways to run the project. Both need about 10 GB of free disk space for the IMDb files
and the intermediate outputs.

### Option 1: Docker Compose (recommended)

Requirements: Docker with Docker Compose.

```bash
git clone https://github.com/Urazikk/GRP2-Big-Data-Project-Gallais-Deplanque.git
cd GRP2-Big-Data-Project-Gallais-Deplanque
docker compose up -d
docker compose exec pyspark-notebook pip install -r requirements.txt
docker logs pyspark_notebook 2>&1 | grep "127.0.0.1:8888"   # Jupyter URL with its token
```

Inside the container, Kafka is reachable at `kafka:19092` (already set through
`KAFKA_BOOTSTRAP_SERVERS`). From the host machine, it is reachable at `localhost:9092`.

### Option 2: local Python environment

Requirements: Python 3.10 or later, Java 17 or 21, and a Kafka broker for the streaming part
(`docker compose up -d kafka` starts only Kafka).

```bash
python -m venv .venv
source .venv/bin/activate
pip install pyspark==4.0.1 -r requirements.txt
export PYTHONPATH=$PWD/src
```

## Running the project

With Docker, run the commands below inside the container, for example
`docker compose exec pyspark-notebook python scripts/download_imdb.py`.

1. Download the IMDb dataset (about 2 GB compressed):

   ```bash
   python scripts/download_imdb.py
   ```

2. Run the tests:

   ```bash
   python -m pytest tests
   ```

3. Each part of the project (data preparation, exploration, enrichment, streaming, open
   question) is described in its own section below, with the command or notebook to run.

### Data exploration

Each question is one module, and its tables are written to `results/exploration/`.
Feature films are movies longer than 40 minutes; a film counts in each of its genres.

```bash
# Feature films whose runtime is notably different from their genre (about 2 minutes);
# the full list is written to data/exploration/runtime_outliers.csv
python -m imdb_project.exploration.runtime_outliers
# Top 3 genres per year (1980-2025) by IMDb votes, and comparison with the other genres
python -m imdb_project.exploration.popular_genres
# Directors with exactly one film rated >= 8.0 and other films averaging <= 6.0
python -m imdb_project.exploration.directors
# Series whose worst episode is in the last season and best in the first two
python -m imdb_project.exploration.series
# Actors with 20+ year careers whose popularity peaked early (about 5 minutes);
# the full list is written to data/exploration/early_peak_actors.csv
python -m imdb_project.exploration.careers
# Multi-talented professionals and their films with combined roles (about 5 minutes)
python -m imdb_project.exploration.multi_talented
```

### Data enrichment

Synopses and biographies come from English Wikipedia only. The collection step runs
outside Spark and only needs `requests` and `beautifulsoup4`; every answer is cached in
`data/enriched/cache/`, so it can be stopped and restarted. A page is kept only if it
links to the IMDb id of the film or person.

```bash
# 1. Films to enrich: top 10 feature films per genre and year, 1980-2025 (Spark)
python -m imdb_project.enrichment.scope --first-year 1980 --last-year 2025 --top-n 10
# 2. Fetch Wikipedia pages (several hours, at most 4 requests per second)
python -m imdb_project.enrichment.collect
# 3. Clean, join and write data/enriched/films with its schema (Spark)
python -m imdb_project.enrichment.build
# Exploration question on languages, which needs the film languages from step 3
python -m imdb_project.exploration.languages
```

Wikimedia rate-limits shared cloud addresses heavily, so step 2 should run from a
personal connection.

### Open question: are remakes rated lower than the films they remake?

Candidate pairs are feature films with the same original title released at least 10 years
apart; each candidate is confirmed on English Wikipedia (the introduction of the remake's
page must call it a remake of a film of the original's year). The Wikipedia step runs
outside Spark, sends batches of 20 titles per request and caches every answer in
`data/open_question/cache/`. Tables are written to `results/open_question/`.

```bash
# 1. Candidate (original, remake) pairs, both films with >= 1000 votes (Spark, about 2 minutes)
python -m imdb_project.open_question.remakes_scope --min-votes 1000 --min-gap 10
# 2. Check every candidate on Wikipedia (about 300 requests, 5 to 15 minutes)
python -m imdb_project.open_question.remakes_collect
# 3. Comparisons and the confirmed pairs with their lineage (Spark, about 3 minutes)
python -m imdb_project.open_question.remakes_analysis
```

## AI tools declaration

| Tool | Used for |
|------|----------|
| Claude Code (Anthropic) | Repository setup: Docker Compose file, Spark session helper, IMDb readers with explicit schemas, download script, unit tests, this guide |
| Claude Code (Anthropic) | Data exploration code and its unit tests |
| Claude Code (Anthropic) | Data enrichment code (scope, Wikipedia collector, Spark build) and its unit tests |
| Claude Code (Anthropic) | Open question code (candidate pairs, batched Wikipedia check, Spark analysis) and its unit tests |

AI tools were not used to write the explanations and reasoning in `REPORT.md`.
