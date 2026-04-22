"""Alpaca data fetcher with v3 API support and offline data loading.

Supports three modes:
1. Live API via Alpaca Python SDK (needs APCA_API_KEY_ID / APCA_API_SECRET_KEY env vars)
2. Offline loading from pre-saved parquet files (for backtesting without live API)
3. Alpaca MCP tools via Claude session (for interactive data pulls)
"""

from datetime import datetime, timedelta
from pathlib import Path
import logging

import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt
from src.data.cache import Cache

logger = logging.getLogger(__name__)


class AlpacaFetcher:
    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        self._cache = Cache(cache_dir, ttl_hours=ttl_hours)

    def fetch_bars(self, symbol: str, days: int = 252, timeframe: str = "1Day") -> pd.DataFrame:
        cached = self._cache.read_parquet(symbol)
        if cached is not None:
            return cached
        raw = self._fetch_from_api(symbol, days, timeframe)
        df = self._normalize_columns(raw) if raw is not None and not raw.empty else pd.DataFrame()
        if not df.empty:
            self._cache.write_parquet(symbol, df)
        return df

    def fetch_bars_batch(self, symbol: str, start_date: str, end_date: str,
                         timeframe: str = "1Day") -> pd.DataFrame:
        """Fetch bars for a date range, handling pagination for multi-year requests."""
        all_bars = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        while current < end:
            chunk_end = min(current + timedelta(days=730), end)
            chunk_start = current.strftime("%Y-%m-%d")
            chunk_end_str = chunk_end.strftime("%Y-%m-%d")
            raw = self._fetch_from_api(symbol, None, timeframe,
                                       start=chunk_start, end=chunk_end_str)
            if raw is not None and not raw.empty:
                normalized = self._normalize_columns(raw)
                if not normalized.empty:
                    all_bars.append(normalized)
            current = chunk_end + timedelta(days=1)
        if not all_bars:
            return pd.DataFrame()
        df = pd.concat(all_bars, ignore_index=True)
        dedup_col = "date" if "date" in df.columns else None
        if dedup_col:
            df = df.drop_duplicates(subset=[dedup_col]).sort_values(dedup_col).reset_index(drop=True)
        else:
            df = df.drop_duplicates().reset_index(drop=True)
        return df

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def _fetch_from_api(self, symbol: str, days: int | None, timeframe: str,
                        start: str | None = None, end: str | None = None) -> pd.DataFrame:
        from alpaca_trade_api import REST
        api = REST()
        bars = api.get_bars(symbol, timeframe, start=start, end=end, limit=days)
        df = bars.df
        if df.empty:
            return pd.DataFrame()
        return df.reset_index()

    def load_from_directory(self, data_dir: Path, symbol: str) -> pd.DataFrame:
        """Load pre-saved parquet or CSV data from a directory.

        Expected file patterns:
        - {data_dir}/{symbol}.parquet
        - {data_dir}/{symbol}.csv
        """
        parquet_path = data_dir / f"{symbol}.parquet"
        csv_path = data_dir / f"{symbol}.csv"
        if parquet_path.exists():
            df = pd.read_parquet(parquet_path)
            return self._normalize_columns(df)
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            return self._normalize_columns(df)
        return pd.DataFrame()

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to our internal convention."""
        if df.empty:
            return df
        col_map = {}
        if "timestamp" in df.columns:
            col_map["timestamp"] = "date"
        elif "t" in df.columns:
            col_map["t"] = "date"
        v2_map = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        for k, v in v2_map.items():
            if k in df.columns:
                col_map[k] = v
        keep = {"date", "open", "high", "low", "close", "volume",
                "o", "h", "l", "c", "v", "timestamp"}
        drop_cols = [c for c in df.columns if c not in keep]
        df = df.rename(columns=col_map)
        df = df.drop(columns=drop_cols, errors="ignore")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df