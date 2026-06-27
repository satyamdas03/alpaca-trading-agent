import pandas as pd
from aqra.data.yf_source import YFSource

def test_fetch_single_ticker():
    src = YFSource()
    df = src.fetch_ohlcv("AAPL", start="2024-01-01", end="2024-01-31")
    assert not df.empty
    assert set(df.columns) >= {"open", "high", "low", "close", "volume", "adjusted_close"}
