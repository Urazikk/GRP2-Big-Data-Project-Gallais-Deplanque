import json
from datetime import datetime

from imdb_project.streaming.consumer import match, parse, volume, windowed_changes
from imdb_project.streaming.lookup import person_pages, resolve, title_pages
from imdb_project.streaming.producer import keep, slim

CHANGE = {
    "meta": {"id": "e1", "dt": "2026-11-07T10:01:30Z"}, "timestamp": 1794045690,
    "server_name": "en.wikipedia.org", "type": "edit", "namespace": 0,
    "title": "Heat (1995 film)", "user": "Alice", "bot": False, "minor": True,
    "length": {"old": 100, "new": 160}, "revision": {"old": 1, "new": 2}, "comment": "typo",
}


def test_producer_filter_and_slim():
    assert keep(CHANGE, ["en.wikipedia.org"], ["edit"], [0])
    assert not keep({**CHANGE, "namespace": 1}, ["en.wikipedia.org"], ["edit"], [0])
    assert not keep({**CHANGE, "server_name": "fr.wikipedia.org"}, ["en.wikipedia.org"],
                    ["edit"], [0])
    record = slim(CHANGE)
    assert record["event_id"] == "e1" and record["length_new"] == 160
    assert json.loads(json.dumps(record)) == record


def test_lookup_page_titles(spark):
    basics = spark.createDataFrame(
        [("tt1", "movie", "Heat", 1995), ("tt2", "movie", "Heat", 1972),
         ("tt3", "tvSeries", "Friends", 1994), ("tt4", "short", "Heat", 2000)],
        "tconst string, titleType string, primaryTitle string, startYear int",
    )
    ratings = spark.createDataFrame([("tt1", 8.3, 900000), ("tt2", 6.1, 2000),
                                     ("tt3", 8.9, 1100000), ("tt4", 7.0, 5000)],
                                    "tconst string, averageRating double, numVotes int")
    titles = title_pages(basics, ratings, min_votes=1000, plain_min_votes=20000)
    lookup = {r.page_title: r for r in resolve(titles).collect()}
    assert lookup["Heat (1995 film)"].imdb_id == "tt1"
    assert lookup["Heat (1972 film)"].imdb_id == "tt2"
    # "Heat (film)" is claimed by both films: the most voted one wins
    assert lookup["Heat (film)"].imdb_id == "tt1" and lookup["Heat (film)"].competitors == 2
    assert lookup["Friends (TV series)"].kind == "series"
    assert lookup["Heat"].imdb_id == "tt1"           # plain title only for popular entries
    assert "Heat (2000 film)" not in lookup          # shorts are not films

    principals = spark.createDataFrame([("tt1", "nm1", "actor"), ("tt1", "nm2", "editor")],
                                       "tconst string, nconst string, category string")
    names = spark.createDataFrame([("nm1", "Al Pacino"), ("nm2", "Someone")],
                                  "nconst string, primaryName string")
    people = {r.page_title for r in person_pages(titles, principals, names, 20000).collect()}
    assert people == {"Al Pacino (actor)", "Al Pacino"}


def test_consumer_transformations_on_a_static_frame(spark):
    rows = [(json.dumps(slim({**CHANGE, "meta": {"id": f"e{i}", "dt": dt}, "title": title})),
             datetime(2026, 11, 7, 10, 10))
            for i, (dt, title) in enumerate([("2026-11-07T10:01:30Z", "Heat (1995 film)"),
                                             ("2026-11-07T10:03:00Z", "Heat (1995 film)"),
                                             ("2026-11-07T10:06:00Z", "Unrelated page")])]
    raw = spark.createDataFrame(rows, "value string, timestamp timestamp")
    events = parse(raw)
    assert events.count() == 3 and events.first().size_delta == 60
    lookup = spark.createDataFrame([("Heat (1995 film)", "tt1", "film", "Heat", 900000)],
                                   "page_title string, imdb_id string, kind string, "
                                   "label string, votes int")
    matched = match(events, lookup)
    assert matched.count() == 2
    w = windowed_changes(matched, "5 minutes").collect()
    assert len(w) == 1 and w[0].changes == 2 and w[0].bytes_changed == 120
    assert sorted(r.changes for r in volume(events, "5 minutes").collect()) == [1, 2]
