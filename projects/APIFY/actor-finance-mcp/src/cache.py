"""Simple in-memory cache with TTL for financial data."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CacheEntry:
    data: Any
    expires_at: float


class FinanceCache:
    """Thread-safe-ish TTL cache. Evicts expired entries on read."""

    DEFAULT_TTLS: dict[str, int] = {
        "stock_quote": 60,         # 1 min — prices change fast
        "stock_financials": 3600,  # 1 hour — quarterly/annual data
        "stock_analysis": 1800,    # 30 min — recommendations shift
        "market_overview": 120,    # 2 min — indices move
        "economic_indicators": 86400,  # 24 hours — macro data infrequent
        "crypto_prices": 30,       # 30 sec — crypto volatile
        "currency_rates": 300,    # 5 min — forex somewhat stable
        "sec_filings": 86400,     # 24 hours — filings don't change
        "earnings_calendar": 3600,  # 1 hour
        "news_sentiment": 600,    # 10 min — news cycles
    }

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._store[key]
            return None
        return entry.data

    def set(self, key: str, data: Any, ttl_seconds: int | None = None) -> None:
        if ttl_seconds is None:
            # Infer TTL from key prefix
            for prefix, ttl in self.DEFAULT_TTLS.items():
                if key.startswith(prefix):
                    ttl_seconds = ttl
                    break
            else:
                ttl_seconds = 300  # fallback 5 min
        self._store[key] = CacheEntry(data=data, expires_at=time.time() + ttl_seconds)

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)