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

### Streaming data processing

Live English Wikipedia changes go from Wikimedia to Kafka (producer, outside Spark) and are
read by a Spark Structured Streaming job that keeps the changes of pages about the IMDb
dataset (films, series and people). Kafka must be running: `docker compose up -d kafka`
(or the full Docker Compose stack). From inside the notebook container, set nothing: the
Kafka address is already `kafka:19092`.

```bash
# 1. Lookup table: Wikipedia page title -> IMDb id (Spark, about 5 minutes)
python -m imdb_project.streaming.lookup --min-votes 1000 --plain-min-votes 20000
# 2. Kafka topic (3 partitions)
python -m imdb_project.streaming.admin
# 3. In two terminals, for the test window (20 to 25 minutes):
python -m imdb_project.streaming.consumer --minutes 25 --watermark "10 minutes" --window "5 minutes" --reset
python -m imdb_project.streaming.producer --minutes 22
# 3b. Optional late data test, in a third terminal while the first two run:
#     replays changes from 40 minutes ago, older than the watermark
python -m imdb_project.streaming.producer --minutes 3 --since-minutes 40 --quiet
# 4. Result tables and streaming metrics (Spark batch)
python -m imdb_project.streaming.report
```

Outputs: `data/streaming/` (parquet and `metrics.jsonl`), `results/streaming/` (tables).

## AI tools declaration

| Tool | Used for |
|------|----------|
| Claude Code (Anthropic) | Repository setup: Docker Compose file, Spark session helper, IMDb readers with explicit schemas, download script, unit tests, this guide |
| Claude Code (Anthropic) | Streaming code (Wikimedia producer, lookup table, Structured Streaming consumer, report) and its unit tests |

AI tools were not used to write the explanations and reasoning in `REPORT.md`.
