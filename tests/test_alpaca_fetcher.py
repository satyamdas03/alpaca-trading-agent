from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data.alpaca_fetcher import AlpacaFetcher


def _v3_bars():
    """Simulate v3 API response format (full column names)."""
    return pd.DataFrame({
        "timestamp": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
        "open": [100.0, 101.0, 102.0],
        "high": [101.0, 102.0, 103.0],
        "low": [99.0, 100.0, 101.0],
        "close": [100.5, 101.5, 102.5],
        "volume": [1000, 1100, 1200],
        "trade_count": [50, 55, 60],
        "vwap": [100.3, 101.2, 102.1],
    })


def _v2_bars():
    """Simulate v2 API response format (single-letter column names)."""
    return pd.DataFrame({
        "t": pd.to_datetime(["2024-01-02", "2024-01-03"]),
        "o": [100.0, 101.0],
        "h": [101.0, 102.0],
        "l": [99.0, 100.0],
        "c": [100.5, 101.5],
        "v": [1000, 1100],
    })


def test_normalize_v3_columns(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    df = fetcher._normalize_columns(_v3_bars())
    assert "date" in df.columns
    assert "close" in df.columns
    assert "volume" in df.columns
    assert "trade_count" not in df.columns
    assert "vwap" not in df.columns


def test_normalize_v2_columns(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    df = fetcher._normalize_columns(_v2_bars())
    assert "date" in df.columns
    assert "close" in df.columns
    assert "volume" in df.columns


def test_fetch_bars_returns_dataframe(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    mock_df = _v3_bars()
    with patch.object(fetcher, "_fetch_from_api", return_value=mock_df):
        df = fetcher.fetch_bars("SPY", days=5)
    assert isinstance(df, pd.DataFrame)
    assert "close" in df.columns
    assert len(df) == 3


def test_fetch_bars_uses_cache(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    mock_df = _v3_bars()
    with patch.object(fetcher, "_fetch_from_api", return_value=mock_df) as mock_api:
        df1 = fetcher.fetch_bars("SPY", days=5)
    # Second call should hit cache
    with patch.object(fetcher, "_fetch_from_api", return_value=mock_df) as mock_api2:
        df2 = fetcher.fetch_bars("SPY", days=5)
        assert mock_api2.call_count == 0


def test_fetch_bars_empty(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    empty_df = pd.DataFrame()
    with patch.object(fetcher, "_fetch_from_api", return_value=empty_df):
        df = fetcher.fetch_bars("INVALID", days=5)
    assert df.empty


def test_fetch_bars_batch(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    mock_df = _v3_bars()
    with patch.object(fetcher, "_fetch_from_api", return_value=mock_df):
        df = fetcher.fetch_bars_batch("SPY", "2024-01-01", "2024-01-10")
    assert isinstance(df, pd.DataFrame)
    assert "close" in df.columns