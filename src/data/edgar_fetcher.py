import os
from pathlib import Path
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from src.data.cache import Cache

logger = logging.getLogger(__name__)


class EdgarFetcher:
    def __init__(self, cache_dir: Path, ttl_hours: int = 2160):
        self._cache = Cache(cache_dir, ttl_hours=ttl_hours)
        identity = os.environ.get("EDGAR_IDENTITY", "bull@trading-agent.dev")
        os.environ["EDGAR_IDENTITY"] = identity

    def fetch_fundamentals(self, ticker: str) -> dict:
        cached = self._cache.read_json(ticker)
        if cached is not None:
            return cached
        try:
            data = self._fetch_from_edgar(ticker)
        except Exception as e:
            logger.warning(f"Failed to fetch fundamentals for {ticker}: {e}")
            return {}
        if data:
            self._cache.write_json(ticker, data)
        return data

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def _fetch_from_edgar(self, ticker: str) -> dict:
        from edgar import Company
        company = Company(ticker)
        financials = company.get_financials()
        income = financials.income_statement()
        balance = financials.balance_sheet()
        return {
            "revenue": self._get_value(income, "Revenues"),
            "gross_profit": self._get_value(income, "GrossProfit"),
            "net_income": self._get_value(income, "NetIncomeLoss"),
            "total_assets": self._get_value(balance, "Assets"),
            "total_liabilities": self._get_value(balance, "Liabilities"),
            "current_assets": self._get_value(balance, "CurrentAssets"),
            "current_liabilities": self._get_value(balance, "CurrentLiabilities"),
        }

    def _get_value(self, statement, field_name: str) -> float | None:
        try:
            val = statement[field_name]
            if hasattr(val, "iloc"):
                return float(val.iloc[0])
            return float(val)
        except (KeyError, TypeError, ValueError):
            return None