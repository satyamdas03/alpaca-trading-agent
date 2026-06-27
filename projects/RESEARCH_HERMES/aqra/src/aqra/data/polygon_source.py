import os
import logging

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class PolygonSource:
    BASE = "https://api.polygon.io/v2/aggs/ticker"

    def fetch_aggregates(
        self,
        ticker: str,
        start: str,
        end: str,
        multiplier: int = 1,
        timespan: str = "day",
    ) -> pd.DataFrame:
        api_key = os.getenv("POLYGON_API_KEY")
        if not api_key:
            logger.warning("POLYGON_API_KEY not set; returning empty aggregates")
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume", "vw", "transactions"]
            )

        url = f"{self.BASE}/{ticker.upper()}/range/{multiplier}/{timespan}/{start}/{end}"
        params = {"apiKey": api_key, "sort": "asc", "limit": 50000}
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()
        results = payload.get("results", [])
        if not results:
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume", "vw", "transactions"]
            )

        df = pd.DataFrame(results)
        df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
        return df.rename(
            columns={
                "o": "open",
                "h": "high",
                "l": "low",
                "c": "close",
                "v": "volume",
                "vw": "vw",
                "n": "transactions",
            }
        )[["timestamp", "open", "high", "low", "close", "volume", "vw", "transactions"]]
