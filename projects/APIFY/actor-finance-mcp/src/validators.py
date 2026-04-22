"""Input validation for Finance Data MCP Server."""

from __future__ import annotations

import re
from typing import Any

VALID_TOOLS = {
    "stock_quote", "stock_financials", "stock_analysis",
    "market_overview", "economic_indicators", "crypto_prices",
    "currency_rates", "sec_filings", "earnings_calendar", "news_sentiment",
}

TICKER_RE = re.compile(r"^[A-Z0-9.\-=^]+$", re.IGNORECASE)

# FRED series IDs for economic indicators
FRED_SERIES = {
    "GDP": "GDP",
    "REAL_GDP": "GDPC1",
    "INFLATION": "CPIAUCSL",
    "CORE_INFLATION": "CPILFESL",
    "INTEREST_RATE": "FEDFUNDS",
    "UNEMPLOYMENT": "UNRATE",
    "RETAIL_SALES": "RSAFS",
    "CONSUMER_SENTIMENT": "UMCSENT",
    "HOUSING_STARTS": "HOUST",
    "INDUSTRIAL_PRODUCTION": "INDPRO",
    "M2_MONEY_SUPPLY": "M2SL",
    "TREASURY_10Y": "DGS10",
    "TREASURY_2Y": "DGS2",
    "YIELD_SPREAD": "T10Y2Y",
    "VIX": "VIXCLS",
}

SEC_FILING_TYPES = {"10-K", "10-Q", "8-K", "DEF 14A", "13-F", "ALL"}

FINANCIAL_TYPES = {"income_statement", "balance_sheet", "cash_flow"}

PERIODS = {"annual", "quarterly"}


def validate_tool(tool: str) -> str:
    if tool not in VALID_TOOLS:
        raise ValueError(f"Unknown tool: {tool}. Valid: {sorted(VALID_TOOLS)}")
    return tool


def validate_tickers(tickers: list[str]) -> list[str]:
    if not tickers:
        raise ValueError("tickers must be a non-empty list")
    cleaned = []
    for t in tickers:
        t = t.strip().upper()
        if not TICKER_RE.match(t):
            raise ValueError(f"Invalid ticker format: {t}")
        cleaned.append(t)
    return cleaned[:50]  # cap at 50


def validate_financial_type(ft: str) -> str:
    if ft not in FINANCIAL_TYPES:
        raise ValueError(f"Invalid financial_type: {ft}. Valid: {sorted(FINANCIAL_TYPES)}")
    return ft


def validate_period(period: str) -> str:
    if period not in PERIODS:
        raise ValueError(f"Invalid period: {period}. Valid: {sorted(PERIODS)}")
    return period


def validate_indicators(indicators: list[str]) -> list[str]:
    known = set(FRED_SERIES.keys())
    valid = []
    for ind in indicators:
        ind = ind.strip().upper()
        if ind in known:
            valid.append(ind)
        else:
            # Allow custom FRED series IDs
            valid.append(ind)
    return valid[:20]  # cap at 20


def validate_filing_type(ft: str) -> str:
    if ft not in SEC_FILING_TYPES:
        raise ValueError(f"Invalid filing_type: {ft}. Valid: {sorted(SEC_FILING_TYPES)}")
    return ft


def validate_limit(limit: int) -> int:
    return max(1, min(100, limit))


def validate_input(raw: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize all actor inputs."""
    tool = validate_tool(raw.get("tool", "stock_quote"))
    tickers = validate_tickers(raw.get("tickers", ["NVDA"]))
    financial_type = validate_financial_type(raw.get("financial_type", "income_statement"))
    period = validate_period(raw.get("period", "annual"))
    indicators = validate_indicators(raw.get("indicators", ["GDP", "INFLATION", "INTEREST_RATE", "UNEMPLOYMENT"]))
    filing_type = validate_filing_type(raw.get("filing_type", "ALL"))
    query = str(raw.get("query", ""))[:500]
    limit = validate_limit(raw.get("limit", 20))

    return {
        "tool": tool,
        "tickers": tickers,
        "financial_type": financial_type,
        "period": period,
        "indicators": indicators,
        "filing_type": filing_type,
        "query": query,
        "limit": limit,
    }