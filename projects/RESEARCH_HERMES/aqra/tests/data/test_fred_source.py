from aqra.data.fred_source import FREDSource


def test_fetch_vix_missing_key(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    src = FREDSource()
    df = src.fetch_vix("2024-01-01", "2024-01-31")
    assert df.empty
