from aqra.data.fmp_source import FMPSource


def test_fetch_fundamentals_missing_key(monkeypatch):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    src = FMPSource()
    df = src.fetch_fundamentals("AAPL")
    assert df.empty
