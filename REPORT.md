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
