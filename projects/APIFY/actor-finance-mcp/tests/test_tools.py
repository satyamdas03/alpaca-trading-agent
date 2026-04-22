"""Tests for Finance Data MCP Server tool modules.

These tests use yfinance with real network calls (marked as integration tests).
For CI, they should be skipped if no network is available.
"""

import pytest
import sys

# Skip all tests in this module if yfinance is not available or network is down
pytestmark = pytest.mark.skipif(
    not sys.modules.get("yfinance"),
    reason="yfinance not available"
)


class TestStockQuote:
    """Integration tests for stock_quote tool."""

    def test_fetch_single_ticker(self):
        from src.tools.stock_quote import fetch_stock_quotes
        results = fetch_stock_quotes(["AAPL"], limit=1)
        assert len(results) == 1
        assert results[0]["tool"] == "stock_quote"
        assert results[0]["ticker"] == "AAPL"
        assert "data" in results[0]
        assert "source" in results[0]

    def test_fetch_multiple_tickers(self):
        from src.tools.stock_quote import fetch_stock_quotes
        results = fetch_stock_quotes(["AAPL", "MSFT"], limit=5)
        assert len(results) == 2
        tickers = [r["ticker"] for r in results]
        assert "AAPL" in tickers
        assert "MSFT" in tickers

    def test_invalid_ticker_fallback(self):
        from src.tools.stock_quote import fetch_stock_quotes
        results = fetch_stock_quotes(["INVALIDTICKER12345"], limit=1)
        assert len(results) == 1
        # Should return fallback data, not crash
        assert results[0]["ticker"] == "INVALIDTICKER12345"


class TestCryptoPrices:
    """Integration tests for crypto_prices tool."""

    def test_fetch_btc(self):
        from src.tools.crypto_prices import fetch_crypto_prices
        results = fetch_crypto_prices(["BTC-USD"], limit=1)
        assert len(results) == 1
        assert results[0]["tool"] == "crypto_prices"


class TestMarketOverview:
    """Integration tests for market_overview tool."""

    def test_fetch_overview(self):
        from src.tools.market_overview import fetch_market_overview
        result = fetch_market_overview()
        assert result["tool"] == "market_overview"
        assert "indices" in result["data"]


class TestCurrencyRates:
    """Integration tests for currency_rates tool."""

    def test_fetch_eur_usd(self):
        from src.tools.currency_rates import fetch_currency_rates
        results = fetch_currency_rates(["EURUSD=X"], limit=1)
        assert len(results) == 1
        assert results[0]["tool"] == "currency_rates"


class TestNewsSentiment:
    """Integration tests for news_sentiment tool."""

    def test_sentiment_scoring(self):
        from src.tools.news_sentiment import _score_sentiment
        pos = _score_sentiment("Apple stock surges after strong earnings beat")
        assert pos["label"] == "positive"

        neg = _score_sentiment("Company stock plunges on warning of weak demand")
        assert neg["label"] == "negative"

        neutral = _score_sentiment("Company reports quarterly results")
        assert neutral["label"] == "neutral"

    def test_empty_text(self):
        from src.tools.news_sentiment import _score_sentiment
        result = _score_sentiment("")
        assert result["label"] == "neutral"
        assert result["score"] == 0.0