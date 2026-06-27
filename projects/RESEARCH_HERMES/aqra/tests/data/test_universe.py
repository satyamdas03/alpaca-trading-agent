from aqra.data.universe import Universe


def test_universe_at_date():
    u = Universe()
    tickers = u.at_date("2024-01-02")
    assert "AAPL" in tickers
    assert len(tickers) >= 400
