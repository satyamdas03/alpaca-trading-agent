"""Market overview tool — indices, sectors, movers."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)

MAJOR_INDICES = {
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "RUSSELL2000": "^RUT",
    "VIX": "^VIX",
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "FTSE100": "^FTSE",
    "DAX": "^GDAXI",
    "NIKKEI": "^N225",
}

SECTOR_ETF = {
    "Technology": "XLK",
    "Healthcare": "XLV",
    "Financials": "XLF",
    "Energy": "XLE",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Communication Services": "XLC",
}


def fetch_market_overview(limit: int = 20) -> dict[str, Any]:
    """Fetch market indices and sector performance."""
    now = datetime.now(timezone.utc).isoformat()

    indices_data = _fetch_indices()
    sectors_data = _fetch_sectors()

    return {
        "tool": "market_overview",
        "ticker": "MARKET",
        "data": {
            "indices": indices_data,
            "sectors": sectors_data,
            "market_status": _market_status(),
        },
        "source": "yfinance",
        "fetched_at": now,
        "cache_ttl": 120,
    }


def _fetch_indices() -> list[dict[str, Any]]:
    """Fetch current values for major indices."""
    results = []
    tickers = list(MAJOR_INDICES.values())
    names = list(MAJOR_INDICES.keys())

    try:
        data = yf.download(tickers, period="2d", progress=False, threads=True)
    except Exception as e:
        logger.warning(f"Index batch download failed: {e}")
        return _fetch_indices_individual()

    if data.empty:
        return _fetch_indices_individual()

    for name, ticker in zip(names, tickers):
        try:
            if len(tickers) == 1:
                close = data.get("Close")
            else:
                close = data.get(("Close", ticker)) if ("Close", ticker) in data.columns else None

            if close is None or (hasattr(close, "empty") and close.empty):
                continue

            current = float(close.iloc[-1])
            prev = float(close.iloc[0]) if len(close) > 1 else current
            change_pct = ((current - prev) / prev * 100) if prev != 0 else 0

            results.append({
                "name": name,
                "ticker": ticker,
                "value": round(current, 2),
                "change_pct": round(change_pct, 2),
            })
        except Exception:
            continue

    return results or _fetch_indices_individual()


def _fetch_indices_individual() -> list[dict[str, Any]]:
    """Fallback: fetch indices one by one."""
    results = []
    for name, ticker in list(MAJOR_INDICES.items())[:8]:  # limit fallback
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if hist.empty:
                continue
            current = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[0]) if len(hist) > 1 else current
            change_pct = ((current - prev) / prev * 100) if prev != 0 else 0
            results.append({
                "name": name,
                "ticker": ticker,
                "value": round(current, 2),
                "change_pct": round(change_pct, 2),
            })
        except Exception:
            continue
    return results


def _fetch_sectors() -> list[dict[str, Any]]:
    """Fetch sector ETF performance."""
    results = []
    tickers = list(SECTOR_ETF.values())
    names = list(SECTOR_ETF.keys())

    try:
        data = yf.download(tickers, period="2d", progress=False, threads=True)
        if data.empty:
            return results

        for name, ticker in zip(names, tickers):
            try:
                close = data.get(("Close", ticker)) if ("Close", ticker) in data.columns else None
                if close is None or (hasattr(close, "empty") and close.empty):
                    continue
                current = float(close.iloc[-1])
                prev = float(close.iloc[0]) if len(close) > 1 else current
                change_pct = ((current - prev) / prev * 100) if prev != 0 else 0
                results.append({
                    "sector": name,
                    "ticker": ticker,
                    "value": round(current, 2),
                    "change_pct": round(change_pct, 2),
                })
            except Exception:
                continue
    except Exception:
        pass

    return results


def _market_status() -> dict[str, str]:
    """Return simple market status indicators."""
    now = datetime.now(timezone.utc)
    hour = now.hour
    # US market hours: 9:30-16:00 ET = 13:30-20:00 UTC
    us_status = "open" if 13 <= hour < 20 else "closed"
    # India market hours: 9:15-15:30 IST = 3:45-10:00 UTC
    india_status = "open" if 3 <= hour < 10 else "closed"
    return {
        "us_market": us_status,
        "india_market": india_status,
    }