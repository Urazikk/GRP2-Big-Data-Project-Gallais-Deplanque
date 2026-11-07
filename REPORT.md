# Report

## Data preparation

### Results

### Methodological explanation

## Data exploration

### Results

### Methodological explanation

## Data enrichment

### Results

### Methodological explanation

## Streaming data processing

### Results

Test run of 7 November 2026, 11:24 to 11:50 UTC: consumer running 25 minutes, live producer
22 minutes (English Wikipedia, articles, edits and new pages), watermark 10 minutes,
tumbling windows of 5 minutes, trigger every 30 seconds. Lookup table: 580,796 Wikipedia
page titles for 49,349 films, 12,968 series and 258,997 people (titles with at least 1,000
IMDb votes).

Run summary:

| metric | value |
|---|---|
| changes matched to the IMDb dataset (whole run) | 36 |
| first / last matched event time | 2026-11-07 11:24:45.738000 / 2026-11-07 11:47:47.177000 |
| closed windows (written after the watermark passed them) | 2026-11-07 11:20:00 / 2026-11-07 11:35:00 |
| changes in closed windows (all English Wikipedia articles) | 874 |
| matched changes in closed windows | 13 |
| matched share in closed windows (%) | 1.49 |
| distinct film entries matched | 12 |
| distinct person entries matched | 13 |
| distinct series entries matched | 2 |

IMDb entries whose Wikipedia page changed during the run:

| kind | imdb_id | label | changes | editors | bytes_changed |
|---|---|---|---|---|---|
| person | nm0446504 | John Kelly | 5 | 1 | 44 |
| film | tt0118617 | Anastasia | 3 | 2 | 1166 |
| series | tt6170874 | Salvation | 2 | 1 | 2250 |
| person | nm0072758 | Tim Bentinck | 2 | 1 | 52 |
| person | nm10635159 | Tyriq Withers | 2 | 2 | 304 |
| film | tt0118636 | Apt Pupil | 1 | 1 | 18 |
| person | nm0213642 | Dan DeCarlo | 1 | 1 | 2 |
| person | nm0000358 | Daniel Day-Lewis | 1 | 1 | 2 |
| series | tt33043892 | Dexter: Resurrection | 1 | 1 | 8 |
| film | tt14564000 | Guntur Kaaram | 1 | 1 | 398 |
| film | tt7125860 | If Beale Street Could Talk | 1 | 1 | 8 |
| film | tt0160399 | Impostor | 1 | 1 | 782 |
| person | nm5313125 | Jane Schoenbrun | 1 | 1 | 3 |
| person | nm5481013 | Kaito Ishikawa | 1 | 1 | 2 |
| person | nm3393343 | Kim Sae-ron | 1 | 1 | 7 |
| person | nm2271872 | Park Si-yeon | 1 | 1 | 6558 |
| film | tt8850222 | Peninsula | 1 | 1 | 73 |
| person | nm0191520 | Peter Cullen | 1 | 1 | 9 |
| person | nm0001636 | Priscilla Presley | 1 | 1 | 3 |
| person | nm0712262 | Rick Ravanello | 1 | 1 | 19 |

Closed windows, all English Wikipedia article changes against the matched ones:

| window_start | window_end | changes | bot_changes | matched_changes | entries |
|---|---|---|---|---|---|
| 2026-11-07 11:20:00 | 2026-11-07 11:25:00 | 41 | 19 | 1 | 1 |
| 2026-11-07 11:25:00 | 2026-11-07 11:30:00 | 416 | 171 | 6 | 5 |
| 2026-11-07 11:30:00 | 2026-11-07 11:35:00 | 417 | 151 | 6 | 5 |

Streaming metrics per query (from the progress of every micro-batch):

| query | batches | input_rows | rows_dropped_by_watermark | max_state_rows | last_watermark | avg_input_rows_per_s | avg_processed_rows_per_s | avg_batch_ms | max_batch_ms |
|---|---|---|---|---|---|---|---|---|---|
| matched_events | 48 | 5235 | 2298 | 1705 | 2026-11-07T11:38:05.583Z | 4.0 | 40.5 | 2715.0 | 3245 |
| volume | 48 | 5235 | 2298 | 1708 | 2026-11-07T11:38:05.583Z | 4.0 | 63.9 | 1750.0 | 2299 |
| windows | 48 | 5235 | 2298 | 1723 | 2026-11-07T11:38:05.583Z | 4.0 | 35.3 | 3046.0 | 3763 |
| windows_console | 48 | 5235 | 2298 | 1723 | 2026-11-07T11:38:05.583Z | 4.0 | 33.3 | 3179.0 | 3909 |

### Late arriving data

Late data test: during the run, a second producer replayed for 3 minutes the changes made
from 40 minutes before (3,447 events sent to the same topic). Rows dropped by the watermark
are counted in the metrics table above.

Delay between the change on Wikipedia (event time) and its arrival in Kafka, for the matched
events that were kept:

| median_s | p95_s | max_s | events_over_1_min |
|---|---|---|---|
| 0.3 | 557.8 | 636.6 | 2 |

### Methodological explanation

## Open question

### Question and motivation

### Results

### Methodological explanation
