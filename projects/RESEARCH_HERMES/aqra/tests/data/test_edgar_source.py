from aqra.data.edgar_source import EDGARSource


def test_fetch_form4_missing_key(monkeypatch):
    monkeypatch.delenv("EDGAR_API_KEY", raising=False)
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    src = EDGARSource()
    df = src.fetch_form4("AAPL", "2024-01-01", "2024-01-31")
    assert df.empty
