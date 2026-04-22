from datetime import date, timedelta
from pathlib import Path
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from src.data.cache import Cache

logger = logging.getLogger(__name__)


class FinraFetcher:
    def __init__(self, cache_dir: Path, ttl_hours: int = 672):
        self._cache = Cache(cache_dir, ttl_hours=ttl_hours)

    def fetch_dark_pool(self, ticker: str) -> dict:
        cached = self._cache.read_json(f"{ticker}_darkpool")
        if cached is not None:
            return cached
        try:
            data = self._fetch_from_finra(ticker)
        except Exception as e:
            logger.warning(f"Failed to fetch dark pool data for {ticker}: {e}")
            return {}
        if data:
            self._cache.write_json(f"{ticker}_darkpool", data)
        return data

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def _fetch_from_finra(self, ticker: str) -> dict:
        import requests
        url = f"https://api.finra.org/data/group/otcMarket/name/weeklySummary"
        params = {
            "symbol": ticker,
            "startDate": (date.today() - timedelta(weeks=4)).isoformat(),
            "endDate": date.today().isoformat(),
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        records = resp.json()
        if not records:
            return {}
        latest = records[-1]
        ats_vol = latest.get("atsVolume", 0)
        total_vol = latest.get("totalVolume", 1)
        return {
            "as_of_date": latest.get("weekStartDate", ""),
            "ats_volume": ats_vol,
            "total_volume": total_vol,
            "ats_ratio": ats_vol / total_vol if total_vol > 0 else 0,
        }

    @staticmethod
    def staleness_decay(weeks_stale: float) -> float:
        return max(0.0, 1.0 - weeks_stale / 4.0)