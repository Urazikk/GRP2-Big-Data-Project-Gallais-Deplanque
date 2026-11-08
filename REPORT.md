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

#### Runtime notably different from the genre average

Outliers found: 37 570 (film, genre) pairs, 27 706 distinct films. Full list: `data/exploration/runtime_outliers.csv`.

Statistics, fences and outliers per genre:

| genre | films | mean | std | median | low_fence | high_fence | shorter | longer | outlier_pct |
|---|---|---|---|---|---|---|---|---|---|
| Drama | 196514 | 96.1 | 37.1 | 93 | 53.4 | 162.5 | 8078 | 3040 | 5.66 |
| Documentary | 115951 | 78.1 | 223.6 | 74 | 28.7 | 178.6 | 0 | 942 | 0.81 |
| Comedy | 96535 | 93.1 | 28.7 | 91 | 59.1 | 141.5 | 4536 | 2858 | 7.66 |
| Romance | 42411 | 99.1 | 25.1 | 95 | 57.7 | 161.9 | 1169 | 723 | 4.46 |
| Action | 40323 | 101.2 | 33.7 | 94 | 55.5 | 173.2 | 1224 | 661 | 4.67 |
| Crime | 34587 | 95.5 | 25.6 | 92 | 58.3 | 149.4 | 1306 | 1039 | 6.78 |
| Thriller | 34044 | 96.1 | 21.8 | 93 | 61.9 | 144.2 | 1425 | 1040 | 7.24 |
| Horror | 30693 | 88.6 | 22.3 | 88 | 59.0 | 128.6 | 1605 | 904 | 8.17 |
| Adventure | 24039 | 93.0 | 30.6 | 90 | 54.6 | 146.0 | 1040 | 821 | 7.74 |
| Mystery | 16461 | 94.3 | 50.4 | 92 | 54.9 | 155.0 | 588 | 217 | 4.89 |
| Biography | 16092 | 89.2 | 29.4 | 88 | 37.3 | 192.4 | 0 | 103 | 0.64 |
| Family | 15932 | 92.3 | 32.7 | 90 | 50.5 | 155.5 | 522 | 330 | 5.35 |
| Music | 13948 | 88.4 | 57.7 | 87 | 38.1 | 178.3 | 0 | 173 | 1.24 |
| History | 13618 | 94.3 | 52.9 | 90 | 39.2 | 198.4 | 0 | 154 | 1.13 |
| Fantasy | 12710 | 94.0 | 31.9 | 91 | 54.0 | 154.2 | 495 | 285 | 6.14 |
| Sci-Fi | 9803 | 91.2 | 30.5 | 90 | 55.5 | 142.4 | 498 | 233 | 7.46 |
| Musical | 8494 | 100.0 | 33.3 | 94 | 52.1 | 174.8 | 191 | 148 | 3.99 |
| Animation | 8326 | 82.7 | 26.8 | 81 | 42.5 | 148.7 | 4 | 125 | 1.55 |
| War | 8043 | 94.8 | 31.3 | 92 | 53.2 | 157.9 | 433 | 218 | 8.09 |
| Sport | 6805 | 89.0 | 37.4 | 90 | 42.5 | 167.2 | 5 | 84 | 1.31 |
| Western | 6374 | 76.5 | 28.7 | 70 | 28.7 | 178.6 | 0 | 81 | 1.27 |
| Adult | 6118 | 79.5 | 30.1 | 77 | 45.2 | 124.2 | 15 | 224 | 3.91 |
| News | 1408 | 77.6 | 32.2 | 75 | 33.8 | 156.3 | 0 | 22 | 1.56 |
| Film-Noir | 876 | 81.9 | 13.8 | 82 | 48.9 | 132.0 | 0 | 2 | 0.23 |
| Reality-TV | 298 | 92.2 | 85.1 | 90 | 34.8 | 176.4 | 0 | 9 | 3.02 |
| Talk-Show | 104 | 87.6 | 33.6 | 79 | 23.5 | 285.6 | 0 | 0 | 0.0 |

20 largest gaps to the genre mean:

| genre | tconst | primaryTitle | startYear | runtimeMinutes | mean | gap_to_mean | direction |
|---|---|---|---|---|---|---|---|
| Documentary | tt8273150 | Logistics | 2012 | 51420 | 78.1 | 51341.9 | longer |
| Documentary | tt3854496 | Ambiancé | 2020 | 43200 | 78.1 | 43121.9 | longer |
| Documentary | tt12277054 | Carnets Filmés (Liste Complète) | 2019 | 28643 | 78.1 | 28564.9 | longer |
| Documentary | tt2659636 | Modern Times Forever | 2011 | 14400 | 78.1 | 14321.9 | longer |
| Documentary | tt2355497 | Beijing 2003 | 2004 | 9000 | 78.1 | 8921.9 | longer |
| Documentary | tt5068890 | Hunger! | 2015 | 6000 | 78.1 | 5921.9 | longer |
| Drama | tt5068890 | Hunger! | 2015 | 6000 | 96.1 | 5903.9 | longer |
| Drama | tt1806963 | Matrjoschka | 2006 | 5700 | 96.1 | 5603.9 | longer |
| Comedy | tt5136218 | London EC1 | 2015 | 5460 | 93.1 | 5366.9 | longer |
| Mystery | tt5136218 | London EC1 | 2015 | 5460 | 94.3 | 5365.7 | longer |
| Drama | tt5136218 | London EC1 | 2015 | 5460 | 96.1 | 5363.9 | longer |
| Documentary | tt0284020 | The Cure for Insomnia | 1987 | 5220 | 78.1 | 5141.9 | longer |
| Music | tt0284020 | The Cure for Insomnia | 1987 | 5220 | 88.4 | 5131.6 | longer |
| Drama | tt3837350 | A 2nd generation film | 2013 | 3077 | 96.1 | 2980.9 | longer |
| Documentary | tt5135246 | Saynatakuna: Masks | 2013 | 2905 | 78.1 | 2826.9 | longer |
| History | tt5135246 | Saynatakuna: Masks | 2013 | 2905 | 94.3 | 2810.7 | longer |
| Documentary | tt0342707 | The Longest Most Meaningless Movie in the World | 1970 | 2880 | 78.1 | 2801.9 | longer |
| History | tt0342707 | The Longest Most Meaningless Movie in the World | 1970 | 2880 | 94.3 | 2785.7 | longer |
| Drama | tt0342707 | The Longest Most Meaningless Movie in the World | 1970 | 2880 | 96.1 | 2783.9 | longer |
| Documentary | tt1866307 | World Peace & Prayer Day | 2011 | 2400 | 78.1 | 2321.9 | longer |

#### Top three genres per year (1980-2025)

Top three genres per year:

| year | rank | genre | films | votes | weighted_rating |
|---|---|---|---|---|---|
| 1980 | 1 | Drama | 1328 | 3162096 | 7.74 |
| 1980 | 2 | Adventure | 163 | 2481109 | 7.93 |
| 1980 | 3 | Horror | 151 | 2071543 | 7.47 |
| 1981 | 1 | Adventure | 177 | 2250020 | 7.71 |
| 1981 | 2 | Drama | 1279 | 1709927 | 7.2 |
| 1981 | 3 | Horror | 169 | 1275011 | 6.47 |
| 1982 | 1 | Drama | 1362 | 3072360 | 7.49 |
| 1982 | 2 | Sci-Fi | 55 | 2456566 | 7.7 |
| 1982 | 3 | Action | 334 | 1872417 | 7.5 |
| 1983 | 1 | Drama | 1406 | 2919435 | 7.37 |
| 1983 | 2 | Action | 340 | 2023789 | 7.44 |
| 1983 | 3 | Adventure | 170 | 1983746 | 7.5 |
| 1984 | 1 | Action | 322 | 3666321 | 7.32 |
| 1984 | 2 | Drama | 1377 | 3022542 | 7.39 |
| 1984 | 3 | Adventure | 161 | 2930924 | 7.36 |
| 1985 | 1 | Comedy | 687 | 4562449 | 7.46 |
| 1985 | 2 | Adventure | 167 | 3409725 | 7.43 |
| 1985 | 3 | Drama | 1332 | 3076037 | 7.23 |
| 1986 | 1 | Drama | 1433 | 3997189 | 7.29 |
| 1986 | 2 | Adventure | 178 | 2964710 | 7.54 |
| 1986 | 3 | Comedy | 700 | 2785094 | 6.7 |
| 1987 | 1 | Drama | 1541 | 4132692 | 7.37 |
| 1987 | 2 | Comedy | 700 | 3685699 | 6.9 |
| 1987 | 3 | Action | 475 | 2359975 | 6.91 |
| 1988 | 1 | Drama | 1431 | 4462790 | 7.39 |
| 1988 | 2 | Comedy | 687 | 4428769 | 6.9 |
| 1988 | 3 | Action | 513 | 2713230 | 7.24 |
| 1989 | 1 | Comedy | 771 | 5010428 | 7.09 |
| 1989 | 2 | Drama | 1456 | 3959624 | 7.24 |
| 1989 | 3 | Adventure | 181 | 2942520 | 7.41 |
| 1990 | 1 | Drama | 1450 | 6319827 | 7.47 |
| 1990 | 2 | Comedy | 721 | 4014816 | 6.85 |
| 1990 | 3 | Crime | 402 | 3587480 | 7.51 |
| 1991 | 1 | Drama | 1428 | 5583702 | 7.49 |
| 1991 | 2 | Crime | 314 | 3672804 | 7.78 |
| 1991 | 3 | Comedy | 704 | 3193538 | 6.64 |
| 1992 | 1 | Drama | 1327 | 6094919 | 7.39 |
| 1992 | 2 | Comedy | 701 | 4072681 | 6.91 |
| 1992 | 3 | Crime | 321 | 3608692 | 7.34 |
| 1993 | 1 | Drama | 1276 | 8992035 | 7.6 |
| 1993 | 2 | Comedy | 626 | 4497822 | 6.83 |
| 1993 | 3 | Crime | 333 | 3044022 | 7.18 |
| 1994 | 1 | Drama | 1337 | 15736393 | 8.3 |
| 1994 | 2 | Crime | 307 | 6503132 | 7.9 |
| 1994 | 3 | Comedy | 682 | 5670203 | 6.66 |
| 1995 | 1 | Drama | 1361 | 12519208 | 7.69 |
| 1995 | 2 | Crime | 291 | 7761469 | 7.84 |
| 1995 | 3 | Comedy | 655 | 6079070 | 7.07 |
| 1996 | 1 | Drama | 1346 | 7858482 | 7.12 |
| 1996 | 2 | Comedy | 725 | 4708226 | 6.45 |
| 1996 | 3 | Crime | 275 | 4442806 | 7.3 |
| 1997 | 1 | Drama | 1477 | 12624106 | 7.5 |
| 1997 | 2 | Action | 398 | 6764510 | 6.5 |
| 1997 | 3 | Comedy | 789 | 5603784 | 6.88 |
| 1998 | 1 | Drama | 1460 | 11779284 | 7.51 |
| 1998 | 2 | Comedy | 825 | 9859359 | 7.21 |
| 1998 | 3 | Crime | 327 | 6216964 | 7.51 |
| 1999 | 1 | Drama | 1574 | 15516565 | 7.7 |
| 1999 | 2 | Comedy | 879 | 8220087 | 6.84 |
| 1999 | 3 | Crime | 324 | 7179618 | 7.96 |
| 2000 | 1 | Drama | 1683 | 13019976 | 7.43 |
| 2000 | 2 | Comedy | 891 | 8332534 | 6.8 |
| 2000 | 3 | Adventure | 153 | 6989496 | 7.32 |
| 2001 | 1 | Drama | 1825 | 14732568 | 7.45 |
| 2001 | 2 | Comedy | 965 | 9508270 | 6.89 |
| 2001 | 3 | Adventure | 166 | 9249984 | 7.68 |
| 2002 | 1 | Drama | 1916 | 17055791 | 7.44 |
| 2002 | 2 | Adventure | 171 | 8689925 | 7.26 |
| 2002 | 3 | Action | 477 | 8392137 | 6.73 |
| 2003 | 1 | Drama | 2018 | 13250949 | 7.5 |
| 2003 | 2 | Action | 471 | 11706196 | 7.01 |
| 2003 | 3 | Comedy | 1142 | 10758236 | 6.74 |
| 2004 | 1 | Drama | 2100 | 16470418 | 7.28 |
| 2004 | 2 | Action | 497 | 11515167 | 7.0 |
| 2004 | 3 | Comedy | 1160 | 10944579 | 6.65 |
| 2005 | 1 | Drama | 2365 | 13686084 | 7.06 |
| 2005 | 2 | Comedy | 1289 | 10189642 | 6.46 |
| 2005 | 3 | Action | 453 | 9056978 | 6.75 |
| 2006 | 1 | Drama | 2602 | 20879930 | 7.42 |
| 2006 | 2 | Comedy | 1433 | 11771538 | 6.53 |
| 2006 | 3 | Thriller | 464 | 8662615 | 7.21 |
| 2007 | 1 | Drama | 2800 | 18531545 | 7.24 |
| 2007 | 2 | Comedy | 1450 | 11713305 | 6.7 |
| 2007 | 3 | Action | 513 | 8992542 | 6.72 |
| 2008 | 1 | Drama | 3132 | 17571788 | 6.98 |
| 2008 | 2 | Action | 575 | 13404992 | 6.75 |
| 2008 | 3 | Comedy | 1656 | 11325031 | 6.39 |
| 2009 | 1 | Drama | 3695 | 17585793 | 7.15 |
| 2009 | 2 | Comedy | 1948 | 13458216 | 6.87 |
| 2009 | 3 | Action | 699 | 12114159 | 6.85 |
| 2010 | 1 | Drama | 4156 | 17550116 | 6.93 |
| 2010 | 2 | Action | 853 | 13331320 | 6.67 |
| 2010 | 3 | Adventure | 504 | 13175423 | 7.34 |
| 2011 | 1 | Drama | 4337 | 20740529 | 7.04 |
| 2011 | 2 | Action | 856 | 17142025 | 6.77 |
| 2011 | 3 | Comedy | 2201 | 13977132 | 6.64 |
| 2012 | 1 | Drama | 4644 | 20110724 | 7.1 |
| 2012 | 2 | Action | 859 | 14889760 | 6.84 |
| 2012 | 3 | Comedy | 2344 | 12505113 | 6.65 |
| 2013 | 1 | Drama | 5151 | 21976633 | 7.04 |
| 2013 | 2 | Action | 966 | 17156769 | 6.67 |
| 2013 | 3 | Comedy | 2547 | 14798111 | 6.79 |
| 2014 | 1 | Drama | 5365 | 24509209 | 7.1 |
| 2014 | 2 | Action | 1017 | 20929010 | 6.92 |
| 2014 | 3 | Adventure | 789 | 17732053 | 7.29 |
| 2015 | 1 | Drama | 5439 | 20482176 | 7.01 |
| 2015 | 2 | Action | 1046 | 15554234 | 6.91 |
| 2015 | 3 | Adventure | 696 | 14157413 | 7.02 |
| 2016 | 1 | Drama | 5458 | 20877518 | 7.07 |
| 2016 | 2 | Action | 1123 | 17198675 | 6.81 |
| 2016 | 3 | Adventure | 698 | 12359102 | 6.72 |
| 2017 | 1 | Drama | 5572 | 20794270 | 7.0 |
| 2017 | 2 | Action | 1151 | 16701145 | 6.98 |
| 2017 | 3 | Comedy | 2700 | 11298413 | 6.73 |
| 2018 | 1 | Drama | 5638 | 17400940 | 6.89 |
| 2018 | 2 | Action | 1105 | 15070353 | 6.9 |
| 2018 | 3 | Adventure | 665 | 13340404 | 7.04 |
| 2019 | 1 | Drama | 5588 | 22008361 | 7.2 |
| 2019 | 2 | Action | 1129 | 12350202 | 6.82 |
| 2019 | 3 | Comedy | 2632 | 12255295 | 6.8 |
| 2020 | 1 | Drama | 4267 | 10471475 | 6.56 |
| 2020 | 2 | Comedy | 1973 | 6510734 | 6.44 |
| 2020 | 3 | Action | 826 | 6125829 | 6.16 |
| 2021 | 1 | Drama | 4954 | 14390968 | 6.77 |
| 2021 | 2 | Action | 1090 | 12862971 | 6.62 |
| 2021 | 3 | Adventure | 558 | 10181453 | 7.01 |
| 2022 | 1 | Drama | 5537 | 15956494 | 6.86 |
| 2022 | 2 | Action | 1165 | 13342657 | 6.75 |
| 2022 | 3 | Comedy | 2793 | 10196482 | 6.58 |
| 2023 | 1 | Drama | 5739 | 14746054 | 6.85 |
| 2023 | 2 | Action | 1286 | 10567801 | 6.52 |
| 2023 | 3 | Comedy | 2872 | 9489286 | 6.55 |
| 2024 | 1 | Drama | 5547 | 11660418 | 6.68 |
| 2024 | 2 | Action | 1288 | 8648694 | 6.54 |
| 2024 | 3 | Comedy | 2762 | 7094428 | 6.43 |
| 2025 | 1 | Drama | 5091 | 8577811 | 6.66 |
| 2025 | 2 | Action | 1282 | 7662518 | 6.43 |
| 2025 | 3 | Comedy | 2556 | 5876106 | 6.42 |

Years in the top three per genre:

| genre | years_in_top | years_at_rank_1 |
|---|---|---|
| Drama | 46 | 42 |
| Comedy | 34 | 2 |
| Action | 29 | 1 |
| Adventure | 16 | 1 |
| Crime | 9 | 0 |
| Horror | 2 | 0 |
| Sci-Fi | 1 | 0 |
| Thriller | 1 | 0 |

#### Top three genres compared with the other genres

Top three genres against the other genres, per year:

| year | other_genres | top_vote_share_pct | top_film_share_pct | top_votes_per_film | rest_votes_per_film | top_weighted_rating | rest_weighted_rating |
|---|---|---|---|---|---|---|---|
| 1980 | 21 | 44.3 | 36.5 | 4698.0 | 3399.0 | 7.73 | 7.5 |
| 1981 | 20 | 46.5 | 35.6 | 3222.0 | 2051.0 | 7.24 | 6.85 |
| 1982 | 19 | 43.7 | 38.1 | 4227.0 | 3353.0 | 7.56 | 7.15 |
| 1983 | 19 | 45.9 | 40.6 | 3615.0 | 2915.0 | 7.43 | 7.11 |
| 1984 | 20 | 44.7 | 39.0 | 5172.0 | 4093.0 | 7.35 | 7.18 |
| 1985 | 19 | 51.5 | 45.0 | 5054.0 | 3882.0 | 7.39 | 7.02 |
| 1986 | 19 | 46.2 | 46.1 | 4218.0 | 4191.0 | 7.2 | 7.05 |
| 1987 | 19 | 42.6 | 51.2 | 3748.0 | 5300.0 | 7.09 | 7.06 |
| 1988 | 19 | 46.8 | 49.3 | 4411.0 | 4865.0 | 7.17 | 7.07 |
| 1989 | 20 | 49.5 | 43.9 | 4947.0 | 3960.0 | 7.22 | 6.78 |
| 1990 | 19 | 45.6 | 47.4 | 5411.0 | 5821.0 | 7.3 | 7.07 |
| 1991 | 19 | 44.2 | 47.9 | 5090.0 | 5926.0 | 7.36 | 7.49 |
| 1992 | 19 | 46.3 | 47.7 | 5865.0 | 6198.0 | 7.23 | 7.0 |
| 1993 | 19 | 44.8 | 47.4 | 7398.0 | 8214.0 | 7.31 | 7.39 |
| 1994 | 20 | 58.2 | 47.8 | 11999.0 | 7865.0 | 7.87 | 7.32 |
| 1995 | 19 | 49.0 | 44.8 | 11426.0 | 9654.0 | 7.59 | 7.28 |
| 1996 | 21 | 44.7 | 46.4 | 7250.0 | 7765.0 | 6.98 | 6.78 |
| 1997 | 19 | 44.1 | 48.5 | 9382.0 | 11213.0 | 7.09 | 7.13 |
| 1998 | 20 | 51.5 | 46.8 | 10664.0 | 8850.0 | 7.4 | 6.8 |
| 1999 | 20 | 43.6 | 47.1 | 11133.0 | 12819.0 | 7.53 | 7.32 |
| 2000 | 20 | 45.0 | 42.2 | 10393.0 | 9270.0 | 7.21 | 6.98 |
| 2001 | 19 | 42.4 | 42.5 | 11330.0 | 11403.0 | 7.36 | 7.16 |
| 2002 | 22 | 42.4 | 35.5 | 13314.0 | 9949.0 | 7.22 | 7.04 |
| 2003 | 21 | 45.5 | 46.5 | 9836.0 | 10244.0 | 7.11 | 7.22 |
| 2004 | 21 | 41.3 | 44.0 | 10362.0 | 11557.0 | 7.02 | 7.11 |
| 2005 | 21 | 40.4 | 42.8 | 8019.0 | 8848.0 | 6.79 | 6.87 |
| 2006 | 22 | 42.7 | 42.0 | 9183.0 | 8911.0 | 7.12 | 6.95 |
| 2007 | 22 | 38.3 | 41.1 | 8238.0 | 9248.0 | 6.96 | 6.91 |
| 2008 | 21 | 40.4 | 40.4 | 7888.0 | 7899.0 | 6.75 | 7.1 |
| 2009 | 21 | 41.3 | 40.1 | 6805.0 | 6466.0 | 6.98 | 6.88 |
| 2010 | 22 | 40.0 | 30.1 | 7991.0 | 5170.0 | 6.97 | 7.02 |
| 2011 | 21 | 46.1 | 37.9 | 7014.0 | 5008.0 | 6.84 | 6.75 |
| 2012 | 22 | 42.7 | 37.1 | 6054.0 | 4779.0 | 6.9 | 6.96 |
| 2013 | 22 | 41.4 | 36.8 | 6225.0 | 5133.0 | 6.85 | 6.95 |
| 2014 | 23 | 47.0 | 28.7 | 8809.0 | 3986.0 | 7.09 | 6.96 |
| 2015 | 22 | 46.6 | 29.7 | 6990.0 | 3385.0 | 6.98 | 6.77 |
| 2016 | 22 | 44.1 | 30.0 | 6929.0 | 3773.0 | 6.89 | 6.9 |
| 2017 | 22 | 45.1 | 39.0 | 5178.0 | 4032.0 | 6.93 | 6.8 |
| 2018 | 22 | 44.3 | 30.7 | 6184.0 | 3446.0 | 6.94 | 6.74 |
| 2019 | 23 | 43.6 | 39.5 | 4986.0 | 4207.0 | 7.0 | 6.86 |
| 2020 | 22 | 44.8 | 36.9 | 3270.0 | 2354.0 | 6.42 | 6.42 |
| 2021 | 22 | 46.4 | 30.9 | 5670.0 | 2921.0 | 6.78 | 6.54 |
| 2022 | 23 | 46.4 | 39.8 | 4160.0 | 3178.0 | 6.75 | 6.56 |
| 2023 | 22 | 44.7 | 40.7 | 3517.0 | 2978.0 | 6.67 | 6.66 |
| 2024 | 23 | 42.9 | 39.3 | 2855.0 | 2462.0 | 6.57 | 6.52 |
| 2025 | 22 | 39.3 | 38.6 | 2477.0 | 2403.0 | 6.52 | 6.45 |

#### Directors with one film rated 8.0 or more and other films averaging 6.0 or less

Directors found: 171. The 25 with the most voted hit are below, full list in
`results/exploration/one_hit_directors.md`.

| nconst | primaryName | other_films | others_avg | hit_title | hit_year | hit_rating | hit_votes |
|---|---|---|---|---|---|---|---|
| nm0574625 | James McTeigue | 4 | 5.98 | V for Vendetta | 2005 | 8.1 | 1260308 |
| nm0549658 | Richard Marquand | 6 | 5.98 | Star Wars: Episode VI - Return of the Jedi | 1983 | 8.3 | 1228582 |
| nm0796117 | M. Night Shyamalan | 15 | 5.87 | The Sixth Sense | 1999 | 8.2 | 1175286 |
| nm0446819 | Richard Kelly | 3 | 5.43 | Donnie Darko | 2001 | 8.0 | 924596 |
| nm0001675 | Robert Rodriguez | 23 | 5.9 | Sin City | 2005 | 8.0 | 825453 |
| nm0588340 | Frank Miller | 2 | 5.65 | Sin City | 2005 | 8.0 | 825453 |
| nm0132709 | Martin Campbell | 20 | 5.62 | Casino Royale | 2006 | 8.0 | 757974 |
| nm0000814 | John G. Avildsen | 21 | 5.78 | Rocky | 1976 | 8.1 | 706136 |
| nm0853238 | Tate Taylor | 6 | 5.88 | The Help | 2011 | 8.1 | 534754 |
| nm0936374 | Kirk Wise | 3 | 5.43 | Beauty and the Beast | 1991 | 8.0 | 511190 |
| nm0204628 | Garth Davis | 2 | 5.65 | Lion | 2016 | 8.0 | 270125 |
| nm0490487 | Wai Keung Lau | 43 | 5.72 | Infernal Affairs | 2002 | 8.0 | 139825 |
| nm1749112 | Vincent Paronnaud | 4 | 5.83 | Persepolis | 2007 | 8.0 | 107428 |
| nm0000671 | Billy Bob Thornton | 3 | 5.93 | Sling Blade | 1996 | 8.0 | 105152 |
| nm1084488 | Umesh Shukla | 6 | 5.57 | OMG: Oh My God! | 2012 | 8.1 | 72394 |
| nm2134474 | Vikas Bahl | 6 | 5.83 | Queen | 2013 | 8.1 | 71987 |
| nm1025280 | Anubhav Sinha | 12 | 5.77 | Article 15 | 2019 | 8.1 | 42123 |
| nm1164861 | Seth Gordon | 7 | 5.7 | The King of Kong: A Fistful of Quarters | 2007 | 8.0 | 38782 |
| nm6134590 | Apoorv Singh Karki | 2 | 4.2 | Sirf Ek Bandaa Kaafi Hai | 2023 | 8.0 | 31497 |
| nm0559877 | John Mathew Matthan | 2 | 5.75 | Sarfarosh | 1999 | 8.1 | 29122 |
| nm1326535 | Sundar C. | 25 | 5.68 | Anbe Sivam | 2003 | 8.6 | 28783 |
| nm0178880 | Eleanor Coppola | 2 | 5.2 | Hearts of Darkness: A Filmmaker's Apocalypse | 1991 | 8.1 | 26239 |
| nm1729063 | Mert Baykal | 3 | 5.9 | Pardon | 2005 | 8.1 | 24920 |
| nm0846092 | Kamal Tabrizi | 14 | 5.76 | The Lizard | 2004 | 8.4 | 24810 |
| nm5120912 | Ajay Bahl | 3 | 4.63 | Section 375 | 2019 | 8.0 | 21914 |

#### Series with the worst episode in the last season and the best in the first two

Series found: 504 out of 13 594 series with at least three seasons of 10 episodes or more.
The 25 most voted are below, full list in `results/exploration/series_worst_last_best_first.md`.

| tconst | primaryTitle | startYear | long_seasons | last_season | rated_episodes | best_first | worst_last | series_votes |
|---|---|---|---|---|---|---|---|---|
| tt1856010 | House of Cards | 2013 | 5 | 6 | 73 | 9.5 | 2.5 | 565114 |
| tt2707408 | Narcos | 2015 | 3 | 3 | 30 | 9.4 | 7.8 | 539285 |
| tt3107288 | The Flash | 2014 | 9 | 9 | 184 | 9.6 | 3.8 | 389893 |
| tt7335184 | You | 2018 | 5 | 5 | 50 | 9.1 | 5.3 | 378437 |
| tt1837492 | 13 Reasons Why | 2017 | 4 | 4 | 49 | 9.1 | 5.1 | 344672 |
| tt1312171 | The Umbrella Academy | 2019 | 3 | 4 | 36 | 8.9 | 4.8 | 319491 |
| tt0844441 | True Blood | 2008 | 7 | 7 | 81 | 8.8 | 5.4 | 274090 |
| tt0813715 | Heroes | 2006 | 4 | 4 | 78 | 8.9 | 6.8 | 267532 |
| tt2357547 | Jessica Jones | 2015 | 3 | 3 | 39 | 9.0 | 7.1 | 243094 |
| tt9335498 | Demon Slayer: Kimetsu no Yaiba | 2019 | 3 | 4 | 63 | 9.8 | 7.1 | 240684 |
| tt4508902 | One Punch Man | 2015 | 3 | 3 | 36 | 9.5 | 1.6 | 232365 |
| tt0285331 | 24 | 2001 | 8 | 8 | 192 | 9.3 | 7.6 | 208785 |
| tt2575988 | Silicon Valley | 2014 | 3 | 6 | 53 | 9.3 | 7.3 | 185192 |
| tt0934814 | Chuck | 2007 | 5 | 5 | 91 | 9.5 | 7.4 | 155059 |
| tt1235099 | Lie to Me | 2009 | 3 | 3 | 48 | 8.8 | 7.0 | 136744 |
| tt1740299 | The Man in the High Castle | 2015 | 4 | 4 | 40 | 9.2 | 6.0 | 127274 |
| tt0439100 | Weeds | 2005 | 8 | 8 | 102 | 8.9 | 6.9 | 124046 |
| tt1553656 | Under the Dome | 2013 | 3 | 3 | 39 | 7.6 | 6.1 | 120007 |
| tt11041332 | Yellowjackets | 2021 | 3 | 3 | 29 | 8.2 | 6.6 | 118486 |
| tt5296406 | Designated Survivor | 2016 | 3 | 3 | 53 | 8.5 | 6.5 | 117302 |
| tt6315640 | Atypical | 2017 | 3 | 4 | 38 | 9.1 | 7.4 | 115695 |
| tt8064302 | Dead to Me | 2019 | 3 | 3 | 30 | 8.6 | 7.4 | 112257 |
| tt8714904 | Narcos: Mexico | 2018 | 3 | 3 | 30 | 9.0 | 7.4 | 103497 |
| tt0060028 | Star Trek | 1966 | 3 | 3 | 80 | 9.2 | 5.2 | 102653 |
| tt1462059 | Falling Skies | 2011 | 5 | 5 | 52 | 8.1 | 5.9 | 100080 |
#### Actors and actresses whose popularity peaked early

Actors found: 4 163 out of 10 592 with at least 15 rated feature films over 20 years or more.
The 50 with the largest decline are below, full list in `data/exploration/early_peak_actors.csv`.

| nconst | primaryName | films | first_year | last_year | best_film | best_year | best_rating | early_avg | late_avg | decline |
|---|---|---|---|---|---|---|---|---|---|---|
| nm0822268 | Jacques Stany | 19 | 1964 | 2000 | A Quiet Place to Kill | 1970 | 6.3 | 5.91 | 1.5 | 4.41 |
| nm0006370 | Manoj Kumar | 20 | 1962 | 1995 | My Name Is Joker | 1970 | 7.9 | 7.11 | 3.05 | 4.06 |
| nm0299014 | Yvonne Furneaux | 18 | 1953 | 1984 | La Dolce Vita | 1960 | 8.0 | 6.43 | 2.4 | 4.03 |
| nm0000043 | Veronica Lake | 20 | 1941 | 1970 | Sullivan's Travels | 1941 | 7.9 | 6.46 | 2.5 | 3.96 |
| nm0044600 | Saroja Devi B. | 16 | 1958 | 2023 | Babruvahana | 1977 | 8.9 | 7.96 | 4.15 | 3.81 |
| nm0015145 | Halit Akçatepe | 35 | 1972 | 2005 | The Chaos Class | 1975 | 9.1 | 7.23 | 3.45 | 3.78 |
| nm0752323 | Helena Růžičková | 17 | 1967 | 2004 | Happy End | 1967 | 7.8 | 6.94 | 3.23 | 3.7 |
| nm0879872 | Larisa Udovichenko | 26 | 1975 | 2014 | Uspekh | 1985 | 7.5 | 6.74 | 3.05 | 3.69 |
| nm0001167 | Shelley Duvall | 20 | 1970 | 2023 | The Shining | 1980 | 8.4 | 7.18 | 3.5 | 3.68 |
| nm0015629 | Tuncay Akça | 19 | 1975 | 2018 | The Chaos Class Failed the Class | 1975 | 8.3 | 6.65 | 3.0 | 3.65 |
| nm0025618 | Mahesh Anand | 32 | 1988 | 2019 | Abhimanyu | 1991 | 7.4 | 5.53 | 1.9 | 3.63 |
| nm0007147 | Dev Anand | 41 | 1951 | 2003 | Guide | 1965 | 8.4 | 7.28 | 3.7 | 3.58 |
| nm0738553 | Artur Rolén | 20 | 1918 | 1967 | The Outlaw and His Wife | 1918 | 7.2 | 7.2 | 3.67 | 3.53 |
| nm0939961 | Robert Woods | 22 | 1966 | 2016 | My Name Is Pecos | 1966 | 6.1 | 5.12 | 1.7 | 3.42 |
| nm0447652 | Tony Kendall | 28 | 1963 | 2000 | The Whip and the Body | 1963 | 6.6 | 5.31 | 1.9 | 3.41 |
| nm0267946 | Hamid Farrokhnezhad | 28 | 2000 | 2023 | Fireworks Wednesday | 2006 | 7.6 | 7.3 | 3.99 | 3.31 |
| nm0000470 | Jeffrey Jones | 27 | 1983 | 2014 | Amadeus | 1984 | 8.4 | 6.18 | 2.9 | 3.28 |
| nm0619870 | Reza Naji | 18 | 1997 | 2025 | Children of Heaven | 1997 | 8.2 | 7.75 | 4.47 | 3.28 |
| nm0060692 | Aleksey Batalov | 16 | 1954 | 2007 | The Cranes Are Flying | 1957 | 8.3 | 7.32 | 4.05 | 3.27 |
| nm0042820 | Suzan Avcı | 40 | 1962 | 2003 | Before the Ice Thaws | 1965 | 7.6 | 5.86 | 2.7 | 3.16 |
| nm0936295 | Norman Wisdom | 18 | 1953 | 2002 | A Stitch in Time | 1963 | 6.9 | 6.31 | 3.2 | 3.11 |
| nm0449431 | András Kern | 22 | 1973 | 2016 | Cat City | 1986 | 8.2 | 7.2 | 4.14 | 3.06 |
| nm0015000 | Ajit Khan | 24 | 1952 | 1994 | Mughal-E-Azam | 1960 | 8.1 | 7.97 | 5.04 | 2.93 |
| nm0052410 | Reggie Bannister | 25 | 1976 | 2017 | Kenny & Company | 1976 | 7.2 | 6.73 | 3.81 | 2.92 |
| nm2298288 | Arzhang Amirfazli | 16 | 1995 | 2025 | Hello! Hello! This Is Juju | 1995 | 6.0 | 6.0 | 3.08 | 2.92 |
| nm0838517 | Sumalatha | 25 | 1980 | 2023 | Thoovanathumbikal | 1987 | 8.6 | 7.48 | 4.58 | 2.9 |
| nm0693027 | Achyut Potdar | 22 | 1983 | 2018 | Ardh Satya | 1983 | 8.1 | 6.77 | 3.9 | 2.87 |
| nm1498467 | Kalasala Babu | 29 | 1988 | 2017 | Paadha Mudhra | 1988 | 7.4 | 7.4 | 4.53 | 2.87 |
| nm0613098 | Caroline Munro | 19 | 1972 | 2020 | The Spy Who Loved Me | 1977 | 7.0 | 5.67 | 2.82 | 2.85 |
| nm0164967 | Robert Clarke | 28 | 1945 | 1990 | The Enchanted Cottage | 1945 | 7.5 | 5.67 | 2.83 | 2.84 |
| nm0557625 | Raju Shrestha | 16 | 1972 | 2012 | Bawarchi | 1972 | 8.1 | 7.43 | 4.6 | 2.83 |
| nm0315942 | Salim Ghouse | 24 | 1976 | 2026 | Thazhvaram | 1990 | 8.2 | 6.87 | 4.05 | 2.82 |
| nm0639684 | Margaret O'Brien | 22 | 1942 | 2018 | Our Vines Have Tender Grapes | 1945 | 7.6 | 6.73 | 3.93 | 2.8 |
| nm0675413 | Maria Perschy | 21 | 1958 | 1984 | Man's Favorite Sport? | 1964 | 7.0 | 6.19 | 3.4 | 2.79 |
| nm0280541 | Jim Fitzpatrick | 16 | 1979 | 2022 | Shelter in the Storm | 1987 | 8.4 | 7.75 | 4.97 | 2.78 |
| nm0008206 | Akbar Abdi | 40 | 1987 | 2023 | Mother | 1990 | 8.4 | 6.54 | 3.78 | 2.76 |
| nm0351352 | Coşkun Göğen | 23 | 1975 | 2022 | Arkadasim | 1982 | 7.2 | 5.47 | 2.7 | 2.76 |
| nm0073426 | Laxmikant Berde | 48 | 1985 | 2013 | Ashi Hi Banwa Banwi | 1988 | 9.0 | 6.29 | 3.55 | 2.74 |
| nm0000998 | Jake Busey | 43 | 1978 | 2025 | Straight Time | 1978 | 7.4 | 7.4 | 4.67 | 2.73 |
| nm0144133 | Gabriel Casseus | 15 | 1995 | 2017 | Black Hawk Down | 2001 | 7.7 | 6.13 | 3.4 | 2.73 |
| nm0666358 | Paula Raymond | 19 | 1948 | 1969 | The Tall Target | 1951 | 7.2 | 6.32 | 3.6 | 2.72 |
| nm0535597 | Ernest Maftei | 17 | 1966 | 2006 | The Punishment | 1976 | 8.0 | 7.3 | 4.6 | 2.7 |
| nm0945085 | Yuriy Yakovlev | 21 | 1958 | 2007 | Ivan Vasilyevich Changes His Profession | 1973 | 8.2 | 7.17 | 4.47 | 2.7 |
| nm0499614 | Ari Lehman | 17 | 1978 | 2026 | Manny's Orphans | 1978 | 6.4 | 6.4 | 3.71 | 2.69 |
| nm0518579 | Ulli Lommel | 25 | 1964 | 2020 | Chinese Roulette | 1976 | 7.2 | 6.14 | 3.45 | 2.69 |
| nm0577867 | Marisa Mell | 36 | 1961 | 1990 | Dr | 1962 | 7.7 | 5.59 | 2.9 | 2.69 |
| nm0004949 | Troy Garity | 19 | 1981 | 2025 | On Golden Pond | 1981 | 7.6 | 7.6 | 4.92 | 2.68 |
| nm0004435 | Rajesh Khanna | 64 | 1966 | 2002 | Anand | 1971 | 8.1 | 6.82 | 4.15 | 2.67 |
| nm1591496 | Mike Colter | 15 | 2004 | 2025 | Million Dollar Baby | 2004 | 8.1 | 8.1 | 5.43 | 2.67 |
| nm0597188 | Piroska Molnár | 15 | 1976 | 2023 | Nobody's Daughter | 1976 | 7.7 | 7.7 | 5.04 | 2.66 |

#### Multi-talented film professionals

People per combination of roles:

| talent_combo | count |
|---|---|
| direct+write | 7902 |
| act+direct+write | 1463 |
| act+write | 1207 |
| act+direct | 439 |

Multi-role films against single-role films, per combination (people with both kinds of films):

| talent_combo | people | multi_films | single_films | avg_multi_rating | avg_single_rating | avg_rating_gap | median_rating_gap | pct_better_multi | avg_multi_median_votes | avg_single_median_votes |
|---|---|---|---|---|---|---|---|---|---|---|
| direct+write | 5655 | 31082 | 29826 | 5.95 | 5.9 | 0.05 | 0.03 | 52.1 | 8157.0 | 8641.0 |
| act+direct+write | 1372 | 10556 | 20615 | 5.83 | 5.74 | 0.09 | 0.12 | 57.5 | 7181.0 | 4839.0 |
| act+write | 1014 | 3300 | 15790 | 5.66 | 5.64 | 0.02 | 0.07 | 54.0 | 7271.0 | 5239.0 |
| act+direct | 340 | 844 | 7765 | 5.74 | 5.84 | -0.1 | -0.04 | 47.9 | 4109.0 | 3684.0 |

30 people with the most multi-role films:

| primaryName | talent_combo | multi_films | single_films | multi_rating | single_rating | rating_gap |
|---|---|---|---|---|---|---|
| Jesús Franco | act+direct+write | 127 | 24 | 4.65 | 4.45 | 0.21 |
| Jing Wong | act+direct+write | 91 | 71 | 5.65 | 5.72 | -0.07 |
| Yōji Yamada | direct+write | 63 | 7 | 6.89 | 6.89 | 0.0 |
| Giannis Dalianidis | direct+write | 61 | 12 | 5.98 | 5.94 | 0.04 |
| Jean-Luc Godard | act+direct+write | 60 | 12 | 6.43 | 6.15 | 0.28 |
| Carlo Vanzina | direct+write | 55 | 13 | 4.85 | 4.83 | 0.02 |
| Woody Allen | act+direct+write | 54 | 8 | 6.89 | 5.69 | 1.2 |
| Cheh Chang | direct+write | 53 | 22 | 6.47 | 6.32 | 0.15 |
| Claude Chabrol | act+direct+write | 47 | 24 | 6.54 | 6.09 | 0.46 |
| Godfrey Ho | act+direct+write | 45 | 23 | 4.12 | 4.51 | -0.39 |
| Kader Khan | act+write | 45 | 126 | 5.73 | 5.35 | 0.38 |
| Claude Lelouch | direct+write | 44 | 7 | 6.3 | 6.56 | -0.26 |
| Mario Monicelli | direct+write | 44 | 34 | 6.67 | 6.61 | 0.06 |
| Neri Parenti | direct+write | 44 | 3 | 4.87 | 5.1 | -0.23 |
| Werner Herzog | act+direct+write | 44 | 10 | 7.09 | 6.48 | 0.61 |
| Dino Risi | direct+write | 42 | 15 | 6.35 | 6.57 | -0.21 |
| Julien Duvivier | direct+write | 42 | 7 | 6.84 | 6.77 | 0.07 |
| Alberto Sordi | act+direct+write | 41 | 63 | 6.14 | 6.64 | -0.5 |
| Alekos Sakellarios | direct+write | 41 | 16 | 6.96 | 5.93 | 1.03 |
| Priyadarshan | direct+write | 40 | 34 | 6.82 | 6.56 | 0.26 |
| Steno | direct+write | 40 | 37 | 6.2 | 6.02 | 0.18 |
| Carlos Saura | direct+write | 39 | 3 | 6.75 | 6.17 | 0.58 |
| Mariano Ozores | direct+write | 39 | 10 | 4.88 | 5.09 | -0.21 |
| Tyler Perry | act+direct+write | 39 | 7 | 5.27 | 6.43 | -1.16 |
| Ingmar Bergman | act+direct+write | 38 | 16 | 7.28 | 6.49 | 0.79 |
| Pupi Avati | direct+write | 38 | 6 | 6.23 | 5.63 | 0.6 |
| Sreenivasan | act+write | 37 | 70 | 7.23 | 6.46 | 0.77 |
| Joseph W. Sarno | direct+write | 36 | 1 | 5.32 | 6.3 | -0.98 |
| Umberto Lenzi | direct+write | 36 | 24 | 5.47 | 5.44 | 0.04 |
| Lucio Fulci | act+direct+write | 35 | 29 | 5.85 | 5.98 | -0.13 |

#### Actors and actresses successful in films of several languages

The original language of a film is the first language of its English Wikipedia infobox
(collected by the enrichment step). Success: rating >= 7.0 and votes >= 10000.

| successful_films | with_language |
|---|---|
| 4963 | 4789 |

Actors per number of original languages among their successful films:

| language_count | count |
|---|---|
| 1 | 26433 |
| 2 | 888 |
| 3 | 112 |
| 4 | 11 |
| 5 | 2 |

Most frequent original languages of successful films:

| language | count |
|---|---|
| English | 3008 |
| Hindi | 300 |
| French | 255 |
| Japanese | 170 |
| Spanish | 97 |
| German | 90 |
| Italian | 87 |
| Tamil | 87 |
| Turkish | 74 |
| Korean | 64 |
| Telugu | 45 |
| Russian | 42 |
| Malayalam | 42 |
| Cantonese | 41 |
| Swedish | 41 |

Actors with successful films in three languages or more:

| primaryName | language_count | successful_films | languages |
|---|---|---|---|
| Bruno Ganz | 5 | 10 | English, German, Greek, Italian, Norwegian |
| Christian Berkel | 5 | 7 | Danish, Dutch, English, French, German |
| Prakash Raj | 4 | 26 | Hindi, Kannada, Tamil, Telugu |
| Max von Sydow | 4 | 17 | English, French, Scanian, Swedish |
| Om Puri | 4 | 12 | English, Hindi, Tamil, Telugu |
| Donnie Yen | 4 | 10 | Cantonese, Chinese (dialect: Cantonese, English, Mandarin |
| Ashish Vidyarthi | 4 | 8 | Hindi, Malayalam, Tamil, Telugu |
| Dulquer Salmaan | 4 | 8 | Hindi, Malayalam, Tamil, Telugu |
| Julie Delpy | 4 | 8 | English, French, German, Polish |
| Monica Bellucci | 4 | 7 | Aramaic, English, French, Italian |
| Ziyi Zhang | 4 | 7 | Cantonese, English, Korean, Mandarin |
| Irene Papas | 4 | 6 | Arabic, English, French, Italian |
| Tadanobu Asano | 4 | 6 | English, Japanese, Mongolian, Thai |
| Amitabh Bachchan | 3 | 28 | English, Hindi, Telugu |
| Nassar | 3 | 25 | Hindi, Tamil, Telugu |
| Anupam Kher | 3 | 21 | English, Hindi, Telugu |
| Jackie Chan | 3 | 17 | Cantonese, English, Mandarin |
| Nawazuddin Siddiqui | 3 | 15 | English, Hindi, Tamil |
| Saurabh Shukla | 3 | 13 | English, Hindi, Tamil |
| Tony Leung Chiu-wai | 3 | 13 | Cantonese, English, Mandarin |
| Catherine Deneuve | 3 | 12 | English, French, Spanish |
| Tabu | 3 | 12 | English, Hindi, Telugu |
| Fahadh Faasil | 3 | 11 | Malayalam, Tamil, Telugu |
| Maggie Cheung | 3 | 11 | Cantonese, English, Mandarin |
| Michelle Yeoh | 3 | 11 | Cantonese, English, Mandarin |
| Ron Perlman | 3 | 11 | English, French, Invented language |
| Anthony Quinn | 3 | 10 | Arabic, English, Italian |
| Daniel Brühl | 3 | 10 | English, French, German |
| Ingrid Bergman | 3 | 10 | English, English (production), Swedish |
| Jeanne Moreau | 3 | 10 | English, French, Italian |
| Michel Piccoli | 3 | 10 | English, French, Italian |
| Amrish Puri | 3 | 9 | English, Hindi, Tamil |
| Charles Chaplin | 3 | 9 | English, Sound (part-talkie), Synchronized Sound |
| Kamal Haasan | 3 | 9 | Hindi, Tamil, Telugu |
| Diane Kruger | 3 | 8 | English, French, German |
| Erland Josephson | 3 | 8 | English, Russian, Swedish |
| Jean Reno | 3 | 8 | English, French, Italian |
| Jet Li | 3 | 8 | Cantonese, English, Mandarin |
| Jim Caviezel | 3 | 8 | Aramaic, English, Persian |
| Mohanlal | 3 | 8 | Hindi, Malayalam, Tamil |
| Mélanie Laurent | 3 | 8 | English, French, Maghrebi Arabic |
| Richard Harris | 3 | 8 | English, Italian, Russian |
| Thomas Kretschmann | 3 | 8 | English, German, Korean |
| Yun-Fat Chow | 3 | 8 | Cantonese, English, Mandarin |
| Ali Suliman | 3 | 7 | Arabic, English, Palestinian Arabic |
| Alia Bhatt | 3 | 7 | Hindi, Punjabi, Telugu |
| Golshifteh Farahani | 3 | 7 | English, French, Persian |
| Isabelle Adjani | 3 | 7 | English, French, German |
| Kishore Kumar G. | 3 | 7 | Kannada, Malayalam, Tamil |
| Lee Byung-hun | 3 | 7 | English, Filipino, Korean |
| Mathieu Amalric | 3 | 7 | American Sign Language, English, French |
| Rutger Hauer | 3 | 7 | Dutch, English, German |
| Taapsee Pannu | 3 | 7 | Hindi, Tamil, Telugu |
| Trisha Krishnan | 3 | 7 | Malayalam, Tamil, Telugu |
| Atul Kulkarni | 3 | 6 | Hindi, Tamil, Telugu |
| Chhaya Kadam | 3 | 6 | Hindi, Malayalam, Marathi |
| Kenneth Branagh | 3 | 6 | Early Modern English, English, Walmajarri |
| Matthias Schoenaerts | 3 | 6 | Dutch, English, French |
| Pierfrancesco Favino | 3 | 6 | English, French, Italian |
| Rao Ramesh | 3 | 6 | Kannada, Tamil, Telugu |
| Sandra Hüller | 3 | 6 | English, French, German |
| Shriya Saran | 3 | 6 | Hindi, Tamil, Telugu |
| Valeria Golino | 3 | 6 | English, French, Italian |
| Fernando Rey | 3 | 5 | English, French, Spanish |
| Féodor Atkine | 3 | 5 | English, French, Spanish |
| Ileana D'Cruz | 3 | 5 | Hindi, Tamil, Telugu |
| Kajal Aggarwal | 3 | 5 | Hindi, Tamil, Telugu |
| Klaus Kinski | 3 | 5 | English, German, Italian |
| Pradeep Singh Rawat | 3 | 5 | Hindi, Tamil, Telugu |
| Rodrigo Santoro | 3 | 5 | English, Portuguese, Spanish |
| Roman Polanski | 3 | 5 | English, French, Polish |
| Sai Kumar | 3 | 5 | Kannada, Tamil, Telugu |
| Sofie Gråbøl | 3 | 5 | Danish, French, Scanian |
| Tinnu Anand | 3 | 5 | Hindi, Tamil, Telugu |
| Aksel Hennie | 3 | 4 | Danish, English, Norwegian |
| Alida Valli | 3 | 4 | English, French, Italian |
| Benno Fürmann | 3 | 4 | French, German, Polish |
| Branka Katic | 3 | 4 | German, Romani, Serbian |
| Doug Jones | 3 | 4 | American Sign Language, English, Spanish |
| Eiji Okada | 3 | 4 | English, French, Japanese |
| Florian Lukas | 3 | 4 | English, German, Hindi |
| Francisco Rabal | 3 | 4 | English, Italian, Spanish |
| Gian Maria Volontè | 3 | 4 | English, French, Italian |
| Hanns Zischler | 3 | 4 | Danish, English, German |
| Jayaram | 3 | 4 | Kannada, Tamil, Telugu |
| Joanna Kulig | 3 | 4 | English, French, Polish |
| Johan Heldenbergh | 3 | 4 | Bosnian, Dutch, English |
| Julia Ormond | 3 | 4 | English, Russian, Spanish |
| Margarita Lozano | 3 | 4 | English, French, Spanish |
| Michel Blanc | 3 | 4 | English, French, Italian |
| Michel Simon | 3 | 4 | English, French, French (intertitles) |
| Nathan Jones | 3 | 4 | English, Mandarin, Thai |
| Nikolaj Coster-Waldau | 3 | 4 | Danish, English, Norwegian |
| Predrag Lakovic | 3 | 4 | Romani, Serbian, Serbo-Croatian |
| Riccardo Scamarcio | 3 | 4 | English, French, Italian |
| Sergi López | 3 | 4 | French, Italian, Spanish |
| Sobhita Dhulipala | 3 | 4 | Hindi, Malayalam, Telugu |
| Stéphane Audran | 3 | 4 | Danish, English, French |
| Ángela Molina | 3 | 4 | French, Italian, Spanish |
| Aitana Sánchez-Gijón | 3 | 3 | English, Italian, Spanish |
| Al Ernest Garcia | 3 | 3 | English, Sound (part-talkie), Synchronized Sound |
| Andréa Ferréol | 3 | 3 | French, German, Italian |
| Anupama Parameswaran | 3 | 3 | Malayalam, Tamil, Telugu |
| Claudia Gerini | 3 | 3 | Aramaic, English, Italian |
| Daniel Olbrychski | 3 | 3 | English, German, Russian |
| Danny Denzongpa | 3 | 3 | English, Hindi, Tamil |
| Franco Nero | 3 | 3 | English, German, Spanish |
| Gustaf Skarsgård | 3 | 3 | English, Norwegian, Swedish |
| Hichem Yacoubi | 3 | 3 | French, Hassaniya Arabic, Wolof |
| Homayoun Ershadi | 3 | 3 | Dari, English, Persian |
| Hristo Shopov | 3 | 3 | Aramaic, English, Serbian |
| Jean Martin | 3 | 3 | Arabic, French, Italian |
| José Luis de Vilallonga | 3 | 3 | English, French, Italian |
| Karl Markovics | 3 | 3 | English, German, Norwegian |
| Leonor Watling | 3 | 3 | English, French, Spanish |
| Miguel Bosé | 3 | 3 | English, French, Spanish |
| R. Sarathkumar | 3 | 3 | Kannada, Tamil, Telugu |
| Rakul Preet Singh | 3 | 3 | Hindi, Tamil, Telugu |
| Sai Pallavi | 3 | 3 | Malayalam, Tamil, Telugu |
| Sebastian Koch | 3 | 3 | Dutch, English, German |
| Sergej Trifunovic | 3 | 3 | English, Norwegian, Serbian |
| Siddharth | 3 | 3 | Hindi, Tamil, Telugu |
| Susanne Lothar | 3 | 3 | English, French, German |
| Valentina Cortese | 3 | 3 | English, French, Italian |
| Vinay Rai | 3 | 3 | Malayalam, Tamil, Telugu |

50 actors with the most successful films in two languages:

| primaryName | language_count | successful_films | languages |
|---|---|---|---|
| Robert De Niro | 2 | 34 | English, Italian |
| Paresh Rawal | 2 | 23 | Hindi, Tamil |
| Clint Eastwood | 2 | 22 | English, Italian |
| Burt Lancaster | 2 | 21 | English, Italian |
| Aamir Khan | 2 | 20 | English, Hindi |
| Jeff Bridges | 2 | 19 | English, English/French |
| Shah Rukh Khan | 2 | 19 | Hindi, Tamil |
| Christian Bale | 2 | 18 | English, Mandarin |
| Henry Fonda | 2 | 18 | English, Italian |
| Irrfan Khan | 2 | 18 | English, Hindi |
| Kate Winslet | 2 | 18 | Early Modern English, English |
| Steve Buscemi | 2 | 18 | English, French |
| Ajay Devgn | 2 | 17 | Hindi, Telugu |
| Mads Mikkelsen | 2 | 17 | Danish, English |
| Stellan Skarsgård | 2 | 17 | English, Norwegian |
| Naseeruddin Shah | 2 | 16 | Hindi, Tamil |
| Rani Mukerji | 2 | 16 | Hindi, Tamil |
| Colin Farrell | 2 | 15 | English, Thai |
| Sally Hawkins | 2 | 15 | American Sign Language, English |
| Tilda Swinton | 2 | 15 | English, Italian |
| Dennis Hopper | 2 | 14 | English, German |
| Kristin Scott Thomas | 2 | 14 | English, French |
| Toshirō Mifune | 2 | 14 | English, Japanese |
| Benicio Del Toro | 2 | 13 | English, Spanish |
| Javier Bardem | 2 | 13 | English, Spanish |
| Madhavan | 2 | 13 | Hindi, Tamil |
| Michael Fassbender | 2 | 13 | English, Irish |
| Michael Stuhlbarg | 2 | 13 | American Sign Language, English |
| Nikolaj Lie Kaas | 2 | 13 | Danish, English |
| Antonio Banderas | 2 | 12 | English, Spanish |
| Boman Irani | 2 | 12 | Hindi, Telugu |
| Marion Cotillard | 2 | 12 | English, French |
| Michael Shannon | 2 | 12 | American Sign Language, English |
| Penélope Cruz | 2 | 12 | English, Spanish |
| Rajkummar Rao | 2 | 12 | English, Hindi |
| Song Kang-ho | 2 | 12 | English, Korean |
| Djimon Hounsou | 2 | 11 | American Sign Language, English |
| Gary Cooper | 2 | 11 | English, Sound (synchronized) |
| Gérard Depardieu | 2 | 11 | French, Italian |
| Hrithik Roshan | 2 | 11 | Hindi, Tamil |
| Juliette Binoche | 2 | 11 | English, French |
| Kareena Kapoor | 2 | 11 | Hindi, Punjabi |
| Samantha Ruth Prabhu | 2 | 11 | Tamil, Telugu |
| Sanjay Dutt | 2 | 11 | Hindi, Kannada |
| Alain Delon | 2 | 10 | French, Italian |
| Cem Yılmaz | 2 | 10 | English, Turkish |
| Charlotte Rampling | 2 | 10 | English, French |
| Cillian Murphy | 2 | 10 | American Sign Language, English |
| James Coburn | 2 | 10 | English, Italian |
| Jason Clarke | 2 | 10 | English, Walmajarri |


### Methodological explanation

## Data enrichment

### Results

Scope: top 10 feature films per genre and year (1980-2025) by IMDb votes, 7 184 films.

Coverage:

| films | with_synopsis | with_languages | with_3_biographies | avg_biographies |
|---|---|---|---|---|
| 7184 | 5824 | 6065 | 5684 | 3.24 |

Films without a synopsis, by note written by the collector:

| synopsis_note | count |
|---|---|
| no English Wikipedia page found | 762 |
| page found but it has no plot or synopsis section | 363 |
| no English Wikipedia page linking | 235 |

Schema of `data/enriched/films`:

```
root
 |-- tconst: string (nullable = true)
 |-- title: string (nullable = true)
 |-- year: integer (nullable = true)
 |-- runtime_minutes: integer (nullable = true)
 |-- genres: array (nullable = true)
 |    |-- element: string (containsNull = true)
 |-- top_genres: array (nullable = true)
 |    |-- element: string (containsNull = true)
 |-- average_rating: double (nullable = true)
 |-- num_votes: integer (nullable = true)
 |-- synopsis: string (nullable = true)
 |-- synopsis_source_url: string (nullable = true)
 |-- synopsis_retrieved_at: timestamp (nullable = true)
 |-- synopsis_note: string (nullable = true)
 |-- original_languages: array (nullable = false)
 |    |-- element: string (containsNull = true)
 |-- principals: array (nullable = false)
 |    |-- element: struct (containsNull = true)
 |    |    |-- ordering: integer (nullable = true)
 |    |    |-- nconst: string (nullable = true)
 |    |    |-- name: string (nullable = true)
 |    |    |-- category: string (nullable = true)
 |    |    |-- biography: string (nullable = true)
 |    |    |-- source_url: string (nullable = true)
 |    |    |-- retrieved_at: timestamp (nullable = true)
 |    |    |-- note: string (nullable = true)
 |-- biographies_found: integer (nullable = false)
```

Sample (the five most voted films with a synopsis and three biographies):

| tconst | title | year | top_genres | synopsis | synopsis_source_url | original_languages | principals |
|---|---|---|---|---|---|---|---|
| tt0111161 | The Shawshank Redemption | 1994 | Drama | In 1947, Portland, Maine, banker Andy Dufresne arrives at Shawshank State Prison to serve two consecutive life sentences for murdering his wife and her lover. H... | https://en.wikipedia.org/wiki/The_Shawshank_Redemption | English | Tim Robbins (bio); Morgan Freeman (bio); Bob Gunton (bio); William Sadler (bio); Clancy Brown (bio) |
| tt0468569 | The Dark Knight | 2008 | Crime, Thriller | A gang of masked criminals rob a mafia-owned bank in Gotham City, betraying and killing each other until the sole survivor, the Joker, reveals himself as the ma... | https://en.wikipedia.org/wiki/The_Dark_Knight | English | Christian Bale (bio); Heath Ledger (bio); Aaron Eckhart (bio); Michael Caine (bio); Maggie Gyllenhaal (bio) |
| tt1375666 | Inception | 2010 | Adventure, Sci-Fi, Thriller | Dom Cobb and Arthur are professional thieves who perform corporate espionage using experimental dream-sharing technology to infiltrate their targets' subconscio... | https://en.wikipedia.org/wiki/Inception | English | Leonardo DiCaprio (bio); Joseph Gordon-Levitt (bio); Elliot Page (bio); Ken Watanabe (bio); Tom Hardy (bio) |
| tt0137523 | Fight Club | 1999 | Crime, Drama, Thriller | The unnamed Narrator works an office job as an insurance claims adjuster. He sees a doctor for his disordered sleep, complaining that he falls asleep unexpected... | https://en.wikipedia.org/wiki/Fight_Club | English | Brad Pitt (bio); Edward Norton (bio); Meat Loaf (bio) |
| tt0816692 | Interstellar | 2014 | Adventure, Sci-Fi | In the near future, humanity faces extinction due to dust storms and widespread crop blights. Joseph Cooper, a widowed former NASA test pilot, works as a farmer... | https://en.wikipedia.org/wiki/Interstellar_(film) | English | Matthew McConaughey (bio); Anne Hathaway (bio); Jessica Chastain (bio); Mackenzie Foy (bio); Ellen Burstyn (bio) |


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

Pairs come from feature films (more than 40 minutes) with the same normalised original title,
released at least 10 years apart, both with at least 1,000 IMDb votes. Each candidate was
checked on English Wikipedia on 7 November 2026; the confirmed pairs, with the source URL and
the sentence used as evidence, are in `data/open_question/remakes`.

Candidates kept at each step:

| step | count |
|---|---|
| candidate pairs (same title, gap >= 10 years) | 2408 |
| distinct remake candidates | 2042 |
| remake candidates with a Wikipedia page linking to their IMDb id | 1713 |
| remakes confirmed by their Wikipedia introduction | 172 |
| confirmed (original, remake) pairs | 180 |

Remake rating minus original rating, all confirmed pairs:

| pairs | avg_original_rating | avg_remake_rating | avg_diff | median_diff | pct_remake_better | pct_remake_worse | median_votes_ratio | pct_remake_more_votes |
|---|---|---|---|---|---|---|---|---|
| 180 | 6.94 | 5.82 | -1.12 | -1.1 | 13.3 | 86.1 | 0.93 | 49.4 |

By gap between the two releases:

| gap | pairs | avg_original_rating | avg_remake_rating | avg_diff | median_diff | pct_remake_better | pct_remake_worse | median_votes_ratio | pct_remake_more_votes |
|---|---|---|---|---|---|---|---|---|---|
| 10-19 years | 16 | 6.86 | 5.75 | -1.11 | -1.1 | 18.8 | 81.3 | 0.54 | 31.3 |
| 20-29 years | 52 | 6.98 | 5.87 | -1.11 | -1.1 | 9.6 | 90.4 | 0.84 | 48.1 |
| 30-49 years | 89 | 6.87 | 5.75 | -1.12 | -1.1 | 12.4 | 86.5 | 0.96 | 49.4 |
| 50+ years | 23 | 7.2 | 6.03 | -1.16 | -1.2 | 21.7 | 78.3 | 1.53 | 65.2 |

By decade of the remake:

| remake_decade | pairs | avg_original_rating | avg_remake_rating | avg_diff | median_diff | pct_remake_better | pct_remake_worse | median_votes_ratio | pct_remake_more_votes |
|---|---|---|---|---|---|---|---|---|---|
| 1940 | 2 | 7.65 | 7.1 | -0.55 | -0.8 | 0.0 | 100.0 | 0.6 | 50.0 |
| 1950 | 8 | 7.18 | 6.98 | -0.2 | -0.5 | 50.0 | 50.0 | 0.79 | 50.0 |
| 1960 | 6 | 7.23 | 6.18 | -1.05 | -1.1 | 0.0 | 100.0 | 0.3 | 16.7 |
| 1970 | 6 | 7.53 | 6.05 | -1.48 | -1.7 | 0.0 | 100.0 | 0.4 | 33.3 |
| 1980 | 10 | 7.03 | 6.16 | -0.87 | -1.1 | 20.0 | 80.0 | 1.1 | 60.0 |
| 1990 | 21 | 7.3 | 6.09 | -1.2 | -1.2 | 4.8 | 90.5 | 1.88 | 57.1 |
| 2000 | 47 | 6.96 | 5.6 | -1.36 | -1.3 | 8.5 | 91.5 | 1.45 | 59.6 |
| 2010 | 57 | 6.82 | 5.75 | -1.08 | -1.1 | 15.8 | 84.2 | 0.96 | 49.1 |
| 2020 | 23 | 6.48 | 5.41 | -1.07 | -0.9 | 17.4 | 82.6 | 0.54 | 30.4 |

By genre of the remake (genres with at least 10 pairs):

| genre | pairs | avg_original_rating | avg_remake_rating | avg_diff | median_diff | pct_remake_better | pct_remake_worse | median_votes_ratio | pct_remake_more_votes |
|---|---|---|---|---|---|---|---|---|---|
| Drama | 75 | 7.14 | 6.09 | -1.04 | -1.0 | 16.0 | 84.0 | 0.86 | 46.7 |
| Comedy | 54 | 6.94 | 5.9 | -1.04 | -1.1 | 7.4 | 92.6 | 1.11 | 53.7 |
| Horror | 52 | 6.61 | 5.09 | -1.51 | -1.4 | 11.5 | 88.5 | 0.6 | 32.7 |
| Action | 46 | 7.06 | 5.9 | -1.16 | -1.1 | 15.2 | 84.8 | 1.15 | 54.3 |
| Thriller | 38 | 6.83 | 5.64 | -1.19 | -1.3 | 13.2 | 84.2 | 1.53 | 57.9 |
| Crime | 37 | 7.08 | 6.19 | -0.89 | -0.9 | 16.2 | 81.1 | 1.89 | 67.6 |
| Adventure | 33 | 7.17 | 6.35 | -0.81 | -0.7 | 24.2 | 75.8 | 1.43 | 57.6 |
| Romance | 32 | 7.04 | 6.3 | -0.73 | -0.9 | 15.6 | 81.3 | 1.21 | 56.3 |
| Mystery | 23 | 6.75 | 5.2 | -1.55 | -1.4 | 8.7 | 91.3 | 0.55 | 30.4 |
| Sci-Fi | 16 | 6.77 | 5.29 | -1.48 | -1.5 | 6.3 | 93.8 | 0.8 | 43.8 |
| Family | 15 | 7.02 | 6.15 | -0.87 | -1.0 | 6.7 | 93.3 | 1.22 | 60.0 |
| Fantasy | 15 | 6.81 | 5.82 | -0.99 | -1.1 | 13.3 | 86.7 | 0.86 | 40.0 |

Depending on whether the remake shares at least one principal (cast or crew) with the original:

| shares_people | pairs | avg_original_rating | avg_remake_rating | avg_diff | median_diff | pct_remake_better | pct_remake_worse | median_votes_ratio | pct_remake_more_votes |
|---|---|---|---|---|---|---|---|---|---|
| False | 22 | 6.84 | 6.26 | -0.58 | -0.7 | 22.7 | 77.3 | 2.06 | 63.6 |
| True | 158 | 6.96 | 5.76 | -1.2 | -1.2 | 12.0 | 87.3 | 0.86 | 47.5 |

Largest drops:

| original_title | original_year | original_rating | remake_title | remake_year | remake_rating | rating_diff | source_url |
|---|---|---|---|---|---|---|---|
| Night of the Living Dead | 1968 | 7.8 | Night of the Living Dead 3D | 2006 | 3.2 | -4.6 | https://en.wikipedia.org/wiki/Night_of_the_Living_Dead_3D |
| Zanjeer | 1973 | 7.5 | Zanjeer | 2013 | 3.4 | -4.1 | https://en.wikipedia.org/wiki/Zanjeer_(2013_film) |
| Psycho | 1960 | 8.5 | Psycho | 1998 | 4.6 | -3.9 | https://en.wikipedia.org/wiki/Psycho_(1998_film) |
| Jacob's Ladder | 1990 | 7.4 | Jacob's Ladder | 2019 | 3.6 | -3.8 | https://en.wikipedia.org/wiki/Jacob's_Ladder_(2019_film) |
| The Wicker Man | 1973 | 7.5 | The Wicker Man | 2006 | 3.8 | -3.7 | https://en.wikipedia.org/wiki/The_Wicker_Man_(2006_film) |
| Black Christmas | 1974 | 7.1 | Black Christmas | 2019 | 3.5 | -3.6 | https://en.wikipedia.org/wiki/Black_Christmas_(2019_film) |
| Night of the Living Dead | 1990 | 6.8 | Night of the Living Dead 3D | 2006 | 3.2 | -3.6 | https://en.wikipedia.org/wiki/Night_of_the_Living_Dead_3D |
| Chatrapathi | 2005 | 7.6 | Chatrapathi | 2023 | 4.0 | -3.6 | https://en.wikipedia.org/wiki/Chatrapathi_(2023_film) |
| The Wages of Fear | 1953 | 8.1 | The Wages of Fear | 2024 | 4.6 | -3.5 | https://en.wikipedia.org/wiki/The_Wages_of_Fear_(2024_film) |
| Rollerball | 1975 | 6.5 | Rollerball | 2002 | 3.2 | -3.3 | https://en.wikipedia.org/wiki/Rollerball_(2002_film) |

Largest gains:

| original_title | original_year | original_rating | remake_title | remake_year | remake_rating | rating_diff | source_url |
|---|---|---|---|---|---|---|---|
| Amber Alert | 2012 | 4.4 | Amber Alert | 2024 | 6.1 | 1.7 | https://en.wikipedia.org/wiki/Amber_Alert_(film) |
| A Star Is Born | 1976 | 6.1 | A Star Is Born | 2018 | 7.6 | 1.5 | https://en.wikipedia.org/wiki/A_Star_Is_Born_(2018_film) |
| Ocean's Eleven | 1960 | 6.5 | Ocean's Eleven | 2001 | 7.7 | 1.2 | https://en.wikipedia.org/wiki/Ocean's_Eleven |
| King Kong | 1976 | 6.0 | King Kong | 2005 | 7.2 | 1.2 | https://en.wikipedia.org/wiki/King_Kong_(2005_film) |
| Deathstalker | 1983 | 4.6 | Deathstalker | 2025 | 5.8 | 1.2 | https://en.wikipedia.org/wiki/Deathstalker_(2025_film) |
| The Ten Commandments | 1923 | 6.8 | The Ten Commandments | 1956 | 7.9 | 1.1 | https://en.wikipedia.org/wiki/The_Ten_Commandments_(1956_film) |
| Satan's Slave | 1980 | 5.6 | Satan's Slaves | 2017 | 6.5 | 0.9 | https://en.wikipedia.org/wiki/Satan's_Slaves |
| The Last House on the Left | 1972 | 5.8 | The Last House on the Left | 2009 | 6.5 | 0.7 | https://en.wikipedia.org/wiki/The_Last_House_on_the_Left_(2009_film) |
| The Man Who Knew Too Much | 1934 | 6.7 | The Man Who Knew Too Much | 1956 | 7.4 | 0.7 | https://en.wikipedia.org/wiki/The_Man_Who_Knew_Too_Much_(1956_film) |
| Scarface | 1932 | 7.7 | Scarface | 1983 | 8.3 | 0.6 | https://en.wikipedia.org/wiki/Scarface_(1983_film) |

### Methodological explanation
