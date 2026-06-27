from aqra.data.finnhub_source import FinnhubSource


def test_fetch_candles_missing_key(monkeypatch):
    monkeypatch.delenv("FINNHUB_API_KEY", raising=False)
    src = FinnhubSource()
    df = src.fetch_candles("AAPL", "2024-01-01", "2024-01-31")
    assert df.empty


def test_fetch_news_missing_key(monkeypatch):
    monkeypatch.delenv("FINNHUB_API_KEY", raising=False)
    src = FinnhubSource()
    df = src.fetch_news("AAPL", "2024-01-01", "2024-01-31")
    assert df.empty
