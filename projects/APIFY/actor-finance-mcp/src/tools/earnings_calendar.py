"""Earnings calendar tool — upcoming earnings dates via yfinance."""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_earnings_calendar(tickers: list[str], limit: int = 20) -> list[dict[str, Any]]:
    """Fetch earnings dates and estimates for given tickers."""
    tickers = tickers[:limit]
    now = datetime.now(timezone.utc).isoformat()
    results = []

    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}

            # Get earnings dates
            earnings_dates = _get_earnings_dates(t)

            # Get earnings estimates
            estimates = _get_earnings_estimates(t, info)

            results.append({
                "tool": "earnings_calendar",
                "ticker": ticker,
                "data": {
                    "company_name": info.get("longName") or info.get("shortName"),
                    "next_earnings_date": estimates.get("next_earnings_date"),
                    "eps_estimate": estimates.get("eps_estimate"),
                    "eps_actual": estimates.get("eps_actual"),
                    "revenue_estimate": estimates.get("revenue_estimate"),
                    "earnings_history": estimates.get("earnings_history", []),
                    "earnings_dates": earnings_dates,
                },
                "source": "yfinance",
                "fetched_at": now,
                "cache_ttl": 3600,
            })
        except Exception as e:
            logger.warning(f"Earnings calendar failed for {ticker}: {e}")
            results.append({
                "tool": "earnings_calendar",
                "ticker": ticker,
                "data": {"error": f"Earnings data unavailable for {ticker}: {str(e)}"},
                "source": "error",
                "fetched_at": now,
                "cache_ttl": 300,
            })

    return results


def _get_earnings_dates(t: yf.Ticker) -> list[dict[str, Any]]:
    """Get upcoming earnings dates."""
    try:
        cal = t.calendar
        if cal is None or (hasattr(cal, "empty") and cal.empty):
            return []

        dates = []
        if isinstance(cal, dict):
            # yfinance returns calendar as dict
            earnings_date = cal.get("Earnings Date")
            if earnings_date is not None:
                if hasattr(earnings_date, "tolist"):
                    for d in earnings_date.tolist()[:4]:
                        dates.append({"date": str(d)})
                else:
                    dates.append({"date": str(earnings_date)})
        return dates
    except Exception:
        return []


def _get_earnings_estimates(t: yf.Ticker, info: dict) -> dict[str, Any]:
    """Extract earnings estimates from ticker info."""
    result = {}

    # Next earnings date
    result["next_earnings_date"] = info.get("nextEarningsDate")

    # EPS estimates
    result["eps_estimate"] = info.get("targetMeanPrice")  # Not exact but closest proxy

    # Get actual earnings history if available
    try:
        earnings = t.earnings
        if earnings is not None and not earnings.empty:
            history = []
            for idx, row in earnings.tail(4).iterrows():
                entry = {"fiscal_year": str(idx)}
                for col in earnings.columns:
                    val = row[col]
                    if hasattr(val, "item"):
                        val = val.item()
                    entry[col.lower().replace(" ", "_")] = val
                history.append(entry)
            result["earnings_history"] = history
    except Exception:
        result["earnings_history"] = []

    return result