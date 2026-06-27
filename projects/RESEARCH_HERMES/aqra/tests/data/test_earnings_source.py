from aqra.data.earnings_source import EarningsSource


def test_fetch_calendar_missing_key(monkeypatch):
    monkeypatch.delenv("EARNINGS_API_KEY", raising=False)
    src = EarningsSource()
    df = src.fetch_calendar("AAPL", "2024-01-01", "2024-01-31")
    assert df.empty
