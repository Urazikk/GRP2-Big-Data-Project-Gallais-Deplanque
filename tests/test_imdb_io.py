import gzip

from imdb_project.imdb_io import read_imdb

SAMPLE = (
    "tconst\ttitleType\tprimaryTitle\toriginalTitle\tisAdult\tstartYear\tendYear"
    "\truntimeMinutes\tgenres\n"
    'tt0000001\tmovie\tSay "Hi\tSay "Hi\t0\t1999\t\\N\t120\tDrama,Comedy\n'
    "tt0000002\tshort\tB\tB\t0\t\\N\t\\N\tabc\t\\N\n"
)


def write_sample(tmp_path):
    with gzip.open(tmp_path / "title.basics.tsv.gz", "wt", encoding="utf-8") as f:
        f.write(SAMPLE)


def test_typed_read(spark, tmp_path):
    write_sample(tmp_path)
    rows = read_imdb(spark, "title.basics", raw_dir=tmp_path).orderBy("tconst").collect()
    assert rows[0].primaryTitle == 'Say "Hi'
    assert rows[0].runtimeMinutes == 120
    assert rows[0].endYear is None
    assert rows[1].startYear is None
    assert rows[1].runtimeMinutes is None


def test_raw_read_keeps_markers(spark, tmp_path):
    write_sample(tmp_path)
    rows = read_imdb(spark, "title.basics", raw_dir=tmp_path, typed=False).orderBy("tconst").collect()
    assert rows[1].startYear == "\\N"
    assert rows[1].runtimeMinutes == "abc"
