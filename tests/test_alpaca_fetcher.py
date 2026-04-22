from unittest.mock import patch, MagicMock
import pandas as pd
from src.data.alpaca_fetcher import AlpacaFetcher

def test_fetch_bars_returns_dataframe(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    mock_bars = [{
        "t": "2024-01-02T00:00:00Z",
        "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": 1000,
        "n": 100, "vw": 100.3,
    }]
    with patch.object(fetcher, "_fetch_from_api", return_value=mock_bars):
        df = fetcher.fetch_bars("SPY", days=5)
    assert isinstance(df, pd.DataFrame)
    assert "close" in df.columns
    assert len(df) == 1

def test_fetch_bars_uses_cache(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    mock_bars = [{
        "t": "2024-01-02T00:00:00Z",
        "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": 1000,
        "n": 100, "vw": 100.3,
    }]
    with patch.object(fetcher, "_fetch_from_api", return_value=mock_bars) as mock_api:
        df1 = fetcher.fetch_bars("SPY", days=5)
        df2 = fetcher.fetch_bars("SPY", days=5)
    assert mock_api.call_count == 1