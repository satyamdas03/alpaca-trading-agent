import os
import logging
from datetime import datetime

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class FinnhubSource:
    BASE = "https://finnhub.io/api/v1"

    def _api_key(self) -> str | None:
        return os.getenv("FINNHUB_API_KEY")

    def _ts(self, date_str: str) -> int:
        return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())

    def fetch_candles(
        self, symbol: str, start: str, end: str, resolution: str = "D"
    ) -> pd.DataFrame:
        api_key = self._api_key()
        if not api_key:
            logger.warning("FINNHUB_API_KEY not set; returning empty candles")
            return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

        url = f"{self.BASE}/stock/candle"
        params = {
            "symbol": symbol.upper(),
            "resolution": resolution,
            "from": self._ts(start),
            "to": self._ts(end),
            "token": api_key,
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()
        if payload.get("s") != "ok":
            return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(payload["t"], unit="s"),
                "open": payload["o"],
                "high": payload["h"],
                "low": payload["l"],
                "close": payload["c"],
                "volume": payload["v"],
            }
        )
        return df

    def fetch_news(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        api_key = self._api_key()
        if not api_key:
            logger.warning("FINNHUB_API_KEY not set; returning empty news")
            return pd.DataFrame(columns=["datetime", "headline", "source", "url", "summary"])

        url = f"{self.BASE}/company-news"
        params = {
            "symbol": symbol.upper(),
            "from": start,
            "to": end,
            "token": api_key,
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        if df.empty:
            return pd.DataFrame(columns=["datetime", "headline", "source", "url", "summary"])

        df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
        return df[["datetime", "headline", "source", "url", "summary"]]
