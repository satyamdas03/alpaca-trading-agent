import os
import logging

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class FMPSource:
    BASE = "https://financialmodelingprep.com/api/v3"

    def fetch_fundamentals(
        self, ticker: str, period: str = "annual", limit: int = 120
    ) -> pd.DataFrame:
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            logger.warning("FMP_API_KEY not set; returning empty fundamentals")
            return pd.DataFrame()

        url = f"{self.BASE}/income-statement/{ticker.upper()}"
        params = {"period": period, "limit": limit, "apikey": api_key}
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
