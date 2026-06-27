import os
import logging

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class FREDSource:
    BASE = "https://api.stlouisfed.org/fred/series/observations"

    def fetch_vix(self, start: str, end: str) -> pd.DataFrame:
        return self.fetch_series("VIXCLS", start, end).rename(
            columns={"vixcls": "vix"}
        )

    def fetch_series(self, series_id: str, start: str, end: str) -> pd.DataFrame:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            logger.warning("FRED_API_KEY not set; returning empty %s series", series_id)
            return pd.DataFrame(columns=["date", series_id.lower()])

        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start,
            "observation_end": end,
        }
        r = requests.get(self.BASE, params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()
        observations = payload.get("observations", [])
        if not observations:
            return pd.DataFrame(columns=["date", series_id.lower()])

        df = pd.DataFrame(observations)
        df["date"] = pd.to_datetime(df["date"])
        df[series_id.lower()] = pd.to_numeric(df["value"], errors="coerce")
        return df[["date", series_id.lower()]]
