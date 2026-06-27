from aqra.data.polygon_source import PolygonSource


def test_fetch_aggregates_missing_key(monkeypatch):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    src = PolygonSource()
    df = src.fetch_aggregates("AAPL", "2024-01-01", "2024-01-31")
    assert df.empty
