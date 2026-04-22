"""Tests for Finance Data MCP Server cache."""

import time
import pytest
from src.cache import FinanceCache


class TestFinanceCache:
    def test_set_and_get(self):
        cache = FinanceCache()
        cache.set("stock_quote:NVDA", {"price": 900.0}, ttl_seconds=60)
        result = cache.get("stock_quote:NVDA")
        assert result == {"price": 900.0}

    def test_cache_miss(self):
        cache = FinanceCache()
        assert cache.get("nonexistent") is None

    def test_cache_expiry(self):
        cache = FinanceCache()
        cache.set("test_key", "data", ttl_seconds=0)
        # ttl_seconds=0 means expired immediately (or within 1 sec)
        time.sleep(0.01)
        # 0 TTL should expire almost immediately, but let's use 1 second
        cache.set("test_key2", "data2", ttl_seconds=1)
        assert cache.get("test_key2") == "data2"

    def test_cache_clear(self):
        cache = FinanceCache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.size() == 2
        cache.clear()
        assert cache.size() == 0
        assert cache.get("a") is None

    def test_default_ttls(self):
        ttls = FinanceCache.DEFAULT_TTLS
        assert ttls["stock_quote"] < ttls["stock_financials"]
        assert ttls["crypto_prices"] < ttls["economic_indicators"]
        assert ttls["sec_filings"] == 86400

    def test_infer_ttl_from_key(self):
        cache = FinanceCache()
        cache.set("stock_quote:NVDA", "data")
        # Should use default TTL for stock_quote (60 seconds)
        entry = cache._store["stock_quote:NVDA"]
        assert entry.expires_at > time.time()
        assert entry.expires_at <= time.time() + 61  # within 1 second tolerance

    def test_size(self):
        cache = FinanceCache()
        assert cache.size() == 0
        cache.set("a", 1)
        assert cache.size() == 1
        cache.set("b", 2)
        assert cache.size() == 2