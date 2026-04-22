"""Crypto prices tool — BTC, ETH, and major altcoins via yfinance."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)

POPULAR_CRYPTOS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "MATIC-USD",
    "LINK-USD", "UNI-USD", "ATOM-USD", "LTC-USD", "BCH-USD",
]


def fetch_crypto_prices(tickers: list[str], limit: int = 20) -> list[dict[str, Any]]:
    """Fetch crypto prices and 24h stats."""
    tickers = tickers[:limit]
    now = datetime.now(timezone.utc).isoformat()
    results = []

    try:
        data = yf.download(tickers, period="3d", progress=False, threads=True)
    except Exception as e:
        logger.warning(f"Crypto batch download failed: {e}")
        return _fetch_crypto_individual(tickers)

    if len(tickers) == 1:
        ticker = tickers[0]
        try:
            result = _parse_crypto(ticker, data)
            results.append(result)
        except Exception:
            results.append(_fallback_crypto(ticker))
        return results

    for ticker in tickers:
        try:
            if ("Close", ticker) not in data.columns:
                results.append(_fallback_crypto(ticker))
                continue
            result = _parse_crypto_multi(ticker, data)
            results.append(result)
        except Exception as e:
            logger.warning(f"Crypto parse failed for {ticker}: {e}")
            results.append(_fallback_crypto(ticker))

    return results


def _parse_crypto_multi(ticker: str, data: Any) -> dict[str, Any]:
    """Parse crypto data from multi-ticker download."""
    try:
        close = data[("Close", ticker)]
        high = data[("High", ticker)]
        low = data[("Low", ticker)]
        volume = data[("Volume", ticker)]

        current = float(close.iloc[-1])
        prev = float(close.iloc[-2]) if len(close) > 1 else current
        change_24h_pct = ((current - prev) / prev * 100) if prev != 0 else 0

        return {
            "tool": "crypto_prices",
            "ticker": ticker,
            "data": {
                "price": round(current, 6),
                "price_change_24h": round(current - prev, 6),
                "price_change_pct_24h": round(change_24h_pct, 2),
                "24h_high": round(float(high.iloc[-1]), 6),
                "24h_low": round(float(low.iloc[-1]), 6),
                "24h_volume": int(volume.iloc[-1]) if not (volume.iloc[-1] != volume.iloc[-1]) else None,
            },
            "source": "yfinance",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "cache_ttl": 30,
        }
    except Exception as e:
        logger.warning(f"Multi-parse failed for {ticker}: {e}")
        return _fallback_crypto(ticker)


def _parse_crypto(ticker: str, data: Any) -> dict[str, Any]:
    """Parse crypto data from single-ticker download."""
    current = float(data["Close"].iloc[-1])
    prev = float(data["Close"].iloc[-2]) if len(data) > 1 else current
    change_pct = ((current - prev) / prev * 100) if prev != 0 else 0

    return {
        "tool": "crypto_prices",
        "ticker": ticker,
        "data": {
            "price": round(current, 6),
            "price_change_24h": round(current - prev, 6),
            "price_change_pct_24h": round(change_pct, 2),
            "24h_high": round(float(data["High"].iloc[-1]), 6),
            "24h_low": round(float(data["Low"].iloc[-1]), 6),
            "24h_volume": int(data["Volume"].iloc[-1]) if data["Volume"].iloc[-1] == data["Volume"].iloc[-1] else None,
        },
        "source": "yfinance",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cache_ttl": 30,
    }


def _fallback_crypto(ticker: str) -> dict[str, Any]:
    """Fetch crypto data individually as fallback."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="3d")
        if hist.empty:
            return _no_data(ticker)
        return _parse_crypto(ticker, hist)
    except Exception as e:
        logger.warning(f"Crypto fallback failed for {ticker}: {e}")
        return _no_data(ticker)


def _no_data(ticker: str) -> dict[str, Any]:
    return {
        "tool": "crypto_prices",
        "ticker": ticker,
        "data": {"error": f"No crypto data available for {ticker}"},
        "source": "error",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cache_ttl": 30,
    }


def _fetch_crypto_individual(tickers: list[str]) -> list[dict[str, Any]]:
    """Fetch crypto data one by one when batch fails."""
    results = []
    for ticker in tickers:
        results.append(_fallback_crypto(ticker))
    return results