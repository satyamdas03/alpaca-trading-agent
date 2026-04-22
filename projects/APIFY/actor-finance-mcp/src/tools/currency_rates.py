"""Currency rates tool — forex pairs via yfinance."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)

MAJOR_PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X",
    "AUDUSD=X", "USDCHF=X", "NZDUSD=X", "USDCNY=X",
    "USDINR=X", "USDMXN=X", "USDBRL=X", "USDKRW=X",
    "EURGBP=X", "EURJPY=X", "EURCHF=X",
]


def fetch_currency_rates(tickers: list[str], limit: int = 20) -> list[dict[str, Any]]:
    """Fetch forex rates. Defaults to major pairs if no tickers specified."""
    if not tickers or tickers == ["NVDA"]:
        tickers = MAJOR_PAIRS[:12]
    else:
        tickers = [t.upper().replace("/", "") if "/" in t else t.upper() for t in tickers]
        tickers = [_ensure_forex_suffix(t) for t in tickers]
    tickers = tickers[:limit]

    now = datetime.now(timezone.utc).isoformat()
    results = []

    try:
        data = yf.download(tickers, period="5d", progress=False, threads=True)
    except Exception as e:
        logger.warning(f"Forex batch download failed: {e}")
        return _fetch_forex_individual(tickers)

    if data.empty:
        return _fetch_forex_individual(tickers)

    if len(tickers) == 1:
        ticker = tickers[0]
        try:
            results.append(_parse_forex_single(ticker, data))
        except Exception:
            results.append(_fallback_forex(ticker))
        return results

    for ticker in tickers:
        try:
            close_col = ("Close", ticker)
            if close_col not in data.columns:
                results.append(_fallback_forex(ticker))
                continue
            series = data[close_col]
            if series.empty:
                results.append(_fallback_forex(ticker))
                continue
            current = float(series.iloc[-1])
            prev = float(series.iloc[-2]) if len(series) > 1 else current
            change_pct = ((current - prev) / prev * 100) if prev != 0 else 0

            results.append({
                "tool": "currency_rates",
                "ticker": ticker,
                "data": {
                    "pair": _clean_pair(ticker),
                    "rate": round(current, 6),
                    "previous_close": round(prev, 6),
                    "change_pct": round(change_pct, 4),
                },
                "source": "yfinance",
                "fetched_at": now,
                "cache_ttl": 300,
            })
        except Exception:
            results.append(_fallback_forex(ticker))

    return results or _fetch_forex_individual(tickers)


def _parse_forex_single(ticker: str, data: Any) -> dict[str, Any]:
    current = float(data["Close"].iloc[-1])
    prev = float(data["Close"].iloc[-2]) if len(data) > 1 else current
    change_pct = ((current - prev) / prev * 100) if prev != 0 else 0

    return {
        "tool": "currency_rates",
        "ticker": ticker,
        "data": {
            "pair": _clean_pair(ticker),
            "rate": round(current, 6),
            "previous_close": round(prev, 6),
            "change_pct": round(change_pct, 4),
        },
        "source": "yfinance",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cache_ttl": 300,
    }


def _ensure_forex_suffix(ticker: str) -> str:
    """Ensure ticker has =X suffix for yfinance forex."""
    if ticker.endswith("=X"):
        return ticker
    if "/" in ticker:
        return ticker.replace("/", "") + "=X"
    return ticker + "=X"


def _clean_pair(ticker: str) -> str:
    """Convert yfinance forex ticker to readable pair."""
    pair = ticker.replace("=X", "")
    if len(pair) == 6:
        return f"{pair[:3]}/{pair[3:]}"
    return pair


def _fallback_forex(ticker: str) -> dict[str, Any]:
    """Individual forex fetch as fallback."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if hist.empty:
            return _no_forex(ticker)
        return _parse_forex_single(ticker, hist)
    except Exception:
        return _no_forex(ticker)


def _no_forex(ticker: str) -> dict[str, Any]:
    return {
        "tool": "currency_rates",
        "ticker": ticker,
        "data": {"error": f"No forex data for {ticker}"},
        "source": "error",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cache_ttl": 300,
    }


def _fetch_forex_individual(tickers: list[str]) -> list[dict[str, Any]]:
    results = []
    for ticker in tickers:
        results.append(_fallback_forex(ticker))
    return results