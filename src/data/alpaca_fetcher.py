from pathlib import Path
import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt
from src.data.cache import Cache


class AlpacaFetcher:
    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        self._cache = Cache(cache_dir, ttl_hours=ttl_hours)

    def fetch_bars(self, symbol: str, days: int = 5, timeframe: str = "1Day") -> pd.DataFrame:
        cached = self._cache.read_parquet(symbol)
        if cached is not None:
            return cached
        raw = self._fetch_from_api(symbol, days, timeframe)
        df = self._parse_bars(raw)
        self._cache.write_parquet(symbol, df)
        return df

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def _fetch_from_api(self, symbol: str, days: int, timeframe: str) -> list[dict]:
        from alpaca_trade_api import REST
        api = REST()
        bars = api.get_bars(symbol, timeframe, limit=days).df
        return bars.reset_index().to_dict("records")

    def _parse_bars(self, raw: list[dict]) -> pd.DataFrame:
        if not raw:
            return pd.DataFrame()
        df = pd.DataFrame(raw)
        col_map = {"t": "date", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df