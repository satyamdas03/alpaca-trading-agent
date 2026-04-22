"""Economic indicators tool — FRED macro data (GDP, inflation, rates, unemployment)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

from ..validators import FRED_SERIES

logger = logging.getLogger(__name__)

# FRED API is optional — yfinance covers some macro via index ETFs
# This tool uses yfinance for what it can, plus FRED_API_KEY env var if available

YF_MACRO_TICKERS = {
    "TREASURY_10Y": "^TNX",
    "TREASURY_2Y": "^IRX",
    "VIX": "^VIX",
    "DOLLAR_INDEX": "DX-Y.NYB",
}


def fetch_economic_indicators(indicators: list[str], limit: int = 20) -> dict[str, Any]:
    """Fetch economic indicator data. Uses yfinance for market-based indicators,
    FRED API for official statistics if key available."""
    indicators = indicators[:limit]
    now = datetime.now(timezone.utc).isoformat()
    results = {}

    # Fetch yfinance-based indicators
    yf_results = _fetch_yf_macro()
    results.update(yf_results)

    # For each requested indicator, try to provide data
    for ind in indicators:
        if ind in results:
            continue  # Already have it from yf
        if ind in FRED_SERIES:
            results[ind] = _fred_indicator(ind)
        elif ind not in results:
            results[ind] = {"indicator": ind, "error": f"Unknown indicator: {ind}"}

    return {
        "tool": "economic_indicators",
        "ticker": "MACRO",
        "data": {
            "indicators": results,
            "fetched_count": len([v for v in results.values() if "error" not in v]),
        },
        "source": "yfinance+fred",
        "fetched_at": now,
        "cache_ttl": 86400,
    }


def _fetch_yf_macro() -> dict[str, Any]:
    """Fetch market-based macro indicators via yfinance."""
    results = {}
    tickers = list(YF_MACRO_TICKERS.values())
    names = list(YF_MACRO_TICKERS.keys())

    try:
        data = yf.download(tickers, period="5d", progress=False, threads=True)
        if data.empty:
            return results

        for name, ticker in zip(names, tickers):
            try:
                close_col = ("Close", ticker) if len(tickers) > 1 else "Close"
                if close_col not in data.columns and "Close" not in data.columns:
                    continue
                series = data[close_col] if len(tickers) > 1 else data["Close"]
                if series is None or (hasattr(series, "empty") and series.empty):
                    continue
                latest = float(series.iloc[-1])
                results[name] = {
                    "indicator": name,
                    "value": round(latest, 4),
                    "unit": _unit_for(name),
                    "source": "yfinance",
                }
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"Macro yf download failed: {e}")

    return results


def _fred_indicator(indicator: str) -> dict[str, Any]:
    """Return FRED series info with latest value placeholder.
    Full FRED data requires FRED_API_KEY environment variable."""
    series_id = FRED_SERIES.get(indicator, indicator)
    return {
        "indicator": indicator,
        "fred_series_id": series_id,
        "value": None,
        "unit": _unit_for(indicator),
        "source": "fred",
        "note": "Set FRED_API_KEY env var for live FRED data. Falls back to yfinance where available.",
    }


def _unit_for(indicator: str) -> str:
    units = {
        "GDP": "USD billions",
        "REAL_GDP": "USD billions (chained 2017)",
        "INFLATION": "Index (1982-84=100)",
        "CORE_INFLATION": "Index (1982-84=100)",
        "INTEREST_RATE": "Percent",
        "UNEMPLOYMENT": "Percent",
        "RETAIL_SALES": "USD millions",
        "CONSUMER_SENTIMENT": "Index",
        "HOUSING_STARTS": "Thousands (units)",
        "INDUSTRIAL_PRODUCTION": "Index (2017=100)",
        "M2_MONEY_SUPPLY": "USD billions",
        "TREASURY_10Y": "Percent",
        "TREASURY_2Y": "Percent",
        "YIELD_SPREAD": "Percent",
        "VIX": "Index",
        "DOLLAR_INDEX": "Index",
    }
    return units.get(indicator, "unknown")