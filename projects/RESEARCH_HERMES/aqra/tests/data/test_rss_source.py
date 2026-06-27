from aqra.data.rss_source import RSSSource


def test_fetch_feed_invalid_url():
    src = RSSSource()
    df = src.fetch_feed("http://localhost:0/invalid")
    assert df.empty
