# Report

## Data preparation

### Results

Percentage of null (`\N` in the IMDb files), missing or empty values per column, computed on
the raw files with every column read as a string:

| table | column | total_rows | null_marker | spark_null | empty | missing | missing_pct |
|---|---|---|---|---|---|---|---|
| name.basics | birthYear | 15783070 | 15097973 | 0 | 0 | 15097973 | 95.66 |
| name.basics | deathYear | 15783070 | 15517984 | 0 | 0 | 15517984 | 98.32 |
| name.basics | knownForTitles | 15783070 | 1912328 | 0 | 0 | 1912328 | 12.12 |
| name.basics | nconst | 15783070 | 0 | 0 | 0 | 0 | 0.0 |
| name.basics | primaryName | 15783070 | 91 | 0 | 0 | 91 | 0.0 |
| name.basics | primaryProfession | 15783070 | 3209410 | 0 | 0 | 3209410 | 20.33 |
| title.akas | attributes | 60074283 | 59757615 | 0 | 0 | 59757615 | 99.47 |
| title.akas | isOriginalTitle | 60074283 | 0 | 0 | 0 | 0 | 0.0 |
| title.akas | language | 60074283 | 19576970 | 0 | 0 | 19576970 | 32.59 |
| title.akas | ordering | 60074283 | 0 | 0 | 0 | 0 | 0.0 |
| title.akas | region | 60074283 | 12958051 | 0 | 0 | 12958051 | 21.57 |
| title.akas | title | 60074283 | 0 | 0 | 0 | 0 | 0.0 |
| title.akas | titleId | 60074283 | 0 | 0 | 0 | 0 | 0.0 |
| title.akas | types | 60074283 | 40204114 | 0 | 0 | 40204114 | 66.92 |
| title.basics | endYear | 12918857 | 12754952 | 0 | 0 | 12754952 | 98.73 |
| title.basics | genres | 12918857 | 546498 | 0 | 0 | 546498 | 4.23 |
| title.basics | isAdult | 12918857 | 0 | 0 | 0 | 0 | 0.0 |
| title.basics | originalTitle | 12918857 | 0 | 0 | 0 | 0 | 0.0 |
| title.basics | primaryTitle | 12918857 | 0 | 0 | 0 | 0 | 0.0 |
| title.basics | runtimeMinutes | 12918857 | 8042071 | 0 | 0 | 8042071 | 62.25 |
| title.basics | startYear | 12918857 | 1485401 | 0 | 0 | 1485401 | 11.5 |
| title.basics | tconst | 12918857 | 0 | 0 | 0 | 0 | 0.0 |
| title.basics | titleType | 12918857 | 0 | 0 | 0 | 0 | 0.0 |
| title.crew | directors | 12919986 | 5761968 | 0 | 0 | 5761968 | 44.6 |
| title.crew | tconst | 12919986 | 0 | 0 | 0 | 0 | 0.0 |
| title.crew | writers | 12919986 | 6402347 | 0 | 0 | 6402347 | 49.55 |
| title.episode | episodeNumber | 9997191 | 2104913 | 0 | 0 | 2104913 | 21.06 |
| title.episode | parentTconst | 9997191 | 0 | 0 | 0 | 0 | 0.0 |
| title.episode | seasonNumber | 9997191 | 2104913 | 0 | 0 | 2104913 | 21.06 |
| title.episode | tconst | 9997191 | 0 | 0 | 0 | 0 | 0.0 |
| title.principals | category | 102659089 | 0 | 0 | 0 | 0 | 0.0 |
| title.principals | characters | 102659089 | 52567377 | 0 | 0 | 52567377 | 51.21 |
| title.principals | job | 102659089 | 82835998 | 0 | 0 | 82835998 | 80.69 |
| title.principals | nconst | 102659089 | 0 | 0 | 0 | 0 | 0.0 |
| title.principals | ordering | 102659089 | 0 | 0 | 0 | 0 | 0.0 |
| title.principals | tconst | 102659089 | 0 | 0 | 0 | 0 | 0.0 |
| title.ratings | averageRating | 1728074 | 0 | 0 | 0 | 0 | 0.0 |
| title.ratings | numVotes | 1728074 | 0 | 0 | 0 | 0 | 0.0 |
| title.ratings | tconst | 1728074 | 0 | 0 | 0 | 0 | 0.0 |

Five columns with the highest percentage of missing values:

| table | column | total_rows | null_marker | spark_null | empty | missing | missing_pct |
|---|---|---|---|---|---|---|---|
| title.akas | attributes | 60074283 | 59757615 | 0 | 0 | 59757615 | 99.47 |
| title.basics | endYear | 12918857 | 12754952 | 0 | 0 | 12754952 | 98.73 |
| name.basics | deathYear | 15783070 | 15517984 | 0 | 0 | 15517984 | 98.32 |
| name.basics | birthYear | 15783070 | 15097973 | 0 | 0 | 15097973 | 95.66 |
| title.principals | job | 102659089 | 82835998 | 0 | 0 | 82835998 | 80.69 |

Cleaning (`python -m imdb_project.preparation.cleaning --max-runtime 600`), rows per table:

| table | rows_in | rows_out | quarantined |
|---|---|---|---|
| title_basics | 12918857 | 12918857 | 0 |
| name_basics | 15783070 | 15783070 | 0 |
| title_ratings | 1728074 | 1728074 | 0 |
| title_principals | 102659089 | 102651910 | 7179 |
| title_directors | 9576802 | 9576105 | 697 |
| title_writers | 15214506 | 15213051 | 1455 |
| title_episode | 9997191 | 9997186 | 5 |
| title_akas | 60074283 | 60074173 | 110 |

Rows moved to the quarantine table, per reason:

| table | reason | count |
|---|---|---|
| title_akas | titleId missing in title.basics | 110 |
| title_directors | nconst missing in name.basics | 443 |
| title_directors | tconst missing in title.basics | 254 |
| title_episode | parentTconst missing in title.basics | 5 |
| title_principals | nconst missing in name.basics | 7179 |
| title_writers | nconst missing in name.basics | 1186 |
| title_writers | tconst missing in title.basics | 269 |

Quality flags kept in the `dq_flags` column, per table:

| table | flag | count |
|---|---|---|
| name_basics | alive_born_before_1900 | 2067 |
| name_basics | lifespan_over_110 | 39 |
| name_basics | birth_before_1000 | 34 |
| name_basics | death_before_birth | 28 |
| name_basics | unknown_known_for_title | 11 |
| title_basics | start_after_current_year | 5530 |
| title_basics | runtime_over_max | 1133 |
| title_basics | runtime_not_positive | 4 |
| title_episode | no_season_or_episode_number | 2104908 |
| title_principals | died_before_release | 350839 |
| title_principals | aged_over_100_at_release | 134812 |
| title_principals | born_after_release | 3108 |

### Methodological explanation

## Data exploration

### Results

### Methodological explanation

## Data enrichment

### Results

### Methodological explanation

## Streaming data processing

### Results

### Late arriving data

### Methodological explanation

## Open question

### Question and motivation

### Results

### Methodological explanation
