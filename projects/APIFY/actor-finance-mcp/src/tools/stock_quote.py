"""Stock quote tool — real-time/delayed prices, volume, change."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_stock_quotes(tickers: list[str], limit: int = 20) -> list[dict[str, Any]]:
    """Fetch quotes for multiple tickers using yfinance batch download."""
    tickers = tickers[:limit]
    results: list[dict[str, Any]] = []

    try:
        data = yf.download(tickers, period="1d", group_by="ticker", progress=False, threads=True)
    except Exception as e:
        logger.warning(f"Batch download failed: {e}, falling back to individual fetch")
        return _fetch_individual(tickers)

    if len(tickers) == 1:
        ticker = tickers[0]
        try:
            results.append(_parse_single(ticker, data))
        except Exception as e:
            logger.warning(f"Failed to parse {ticker}: {e}")
            results.append(_fallback_quote(ticker))
        return results

    for ticker in tickers:
        try:
            ticker_data = data[ticker] if ticker in data else None
            if ticker_data is None or ticker_data.empty:
                results.append(_fallback_quote(ticker))
                continue
            results.append(_parse_single(ticker, ticker_data))
        except Exception as e:
            logger.warning(f"Failed to parse {ticker}: {e}")
            results.append(_fallback_quote(ticker))

    return results


def _parse_single(ticker: str, data: Any) -> dict[str, Any]:
    """Parse yfinance data for a single ticker."""
    if data.empty:
        return _fallback_quote(ticker)

    row = data.iloc[-1] if hasattr(data, "iloc") else data

    def safe_get(key: str, default=None):
        try:
            val = row.get(key, default) if hasattr(row, "get") else getattr(row, key, default)
            if val is not None and hasattr(val, "item"):
                return val.item()
            return val
        except Exception:
            return default

    return {
        "tool": "stock_quote",
        "ticker": ticker,
        "data": {
            "price": safe_get("Close"),
            "open": safe_get("Open"),
            "high": safe_get("High"),
            "low": safe_get("Low"),
            "volume": safe_get("Volume"),
            "previous_close": safe_get("Close"),
        },
        "source": "yfinance",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cache_ttl": 60,
    }


def _fallback_quote(ticker: str) -> dict[str, Any]:
    """Generate fallback quote using yf.Ticker individual fetch."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        return {
            "tool": "stock_quote",
            "ticker": ticker,
            "data": {
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "open": info.get("regularMarketOpen") or info.get("open"),
                "high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "low": info.get("dayLow") or info.get("regularMarketDayLow"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "previous_close": info.get("previousClose"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume"),
            },
            "source": "yfinance_info",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "cache_ttl": 60,
        }
    except Exception as e:
        logger.warning(f"Fallback quote failed for {ticker}: {e}")
        return {
            "tool": "stock_quote",
            "ticker": ticker,
            "data": {"error": f"No data available for {ticker}"},
            "source": "error",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "cache_ttl": 30,
        }


def _fetch_individual(tickers: list[str]) -> list[dict[str, Any]]:
    """Fetch quotes one by one when batch fails."""
    results = []
    for ticker in tickers:
        results.append(_fallback_quote(ticker))
    return results