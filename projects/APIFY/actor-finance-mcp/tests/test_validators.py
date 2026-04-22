"""Tests for Finance Data MCP Server validators."""

import pytest
from src.validators import (
    validate_tool,
    validate_tickers,
    validate_financial_type,
    validate_period,
    validate_indicators,
    validate_filing_type,
    validate_limit,
    validate_input,
)


class TestValidateTool:
    def test_valid_tools(self):
        for tool in ["stock_quote", "stock_financials", "stock_analysis",
                      "market_overview", "economic_indicators", "crypto_prices",
                      "currency_rates", "sec_filings", "earnings_calendar", "news_sentiment"]:
            assert validate_tool(tool) == tool

    def test_invalid_tool(self):
        with pytest.raises(ValueError, match="Unknown tool"):
            validate_tool("invalid_tool")


class TestValidateTickers:
    def test_valid_tickers(self):
        result = validate_tickers(["AAPL", "RELIANCE.NS", "BTC-USD"])
        assert result == ["AAPL", "RELIANCE.NS", "BTC-USD"]

    def test_empty_tickers(self):
        with pytest.raises(ValueError, match="non-empty"):
            validate_tickers([])

    def test_max_tickers(self):
        result = validate_tickers(["A"] * 100)
        assert len(result) == 50

    def test_uppercase_conversion(self):
        assert validate_tickers(["nvda"]) == ["NVDA"]

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_tickers(["INVALID TICKER!"])


class TestValidateFinancialType:
    def test_valid_types(self):
        for ft in ["income_statement", "balance_sheet", "cash_flow"]:
            assert validate_financial_type(ft) == ft

    def test_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid financial_type"):
            validate_financial_type("invalid")


class TestValidatePeriod:
    def test_valid_periods(self):
        assert validate_period("annual") == "annual"
        assert validate_period("quarterly") == "quarterly"

    def test_invalid_period(self):
        with pytest.raises(ValueError, match="Invalid period"):
            validate_period("monthly")


class TestValidateIndicators:
    def test_known_indicators(self):
        result = validate_indicators(["GDP", "INFLATION"])
        assert result == ["GDP", "INFLATION"]

    def test_custom_indicator(self):
        result = validate_indicators(["CUSTOM_SERIES"])
        assert "CUSTOM_SERIES" in result

    def test_max_indicators(self):
        result = validate_indicators(["GDP"] * 50)
        assert len(result) == 20


class TestValidateFilingType:
    def test_valid_filing_types(self):
        for ft in ["10-K", "10-Q", "8-K", "DEF 14A", "13-F", "ALL"]:
            assert validate_filing_type(ft) == ft

    def test_invalid_filing_type(self):
        with pytest.raises(ValueError, match="Invalid filing_type"):
            validate_filing_type("S-1")


class TestValidateLimit:
    def test_normal_limit(self):
        assert validate_limit(20) == 20

    def test_below_min(self):
        assert validate_limit(0) == 1

    def test_above_max(self):
        assert validate_limit(200) == 100


class TestValidateInput:
    def test_defaults(self):
        result = validate_input({})
        assert result["tool"] == "stock_quote"
        assert result["tickers"] == ["NVDA"]
        assert result["financial_type"] == "income_statement"
        assert result["period"] == "annual"
        assert result["limit"] == 20

    def test_custom_input(self):
        result = validate_input({
            "tool": "crypto_prices",
            "tickers": ["BTC-USD", "ETH-USD"],
            "limit": 10,
        })
        assert result["tool"] == "crypto_prices"
        assert result["tickers"] == ["BTC-USD", "ETH-USD"]
        assert result["limit"] == 10

    def test_invalid_tool_raises(self):
        with pytest.raises(ValueError):
            validate_input({"tool": "invalid"})