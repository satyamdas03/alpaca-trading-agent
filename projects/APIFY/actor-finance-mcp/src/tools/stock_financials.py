"""Stock financials tool — income statement, balance sheet, cash flow."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)

# Key fields to extract per statement type (avoids dumping 100+ columns)
INCOME_KEYS = [
    "Total Revenue", "Cost of Revenue", "Gross Profit",
    "Operating Revenue", "Operating Expense", "Operating Income",
    "Net Income", "EBIT", "EBITDA",
    "Basic EPS", "Diluted EPS",
    "Interest Expense", "Tax Provision",
    "Research and Development",
]

BALANCE_KEYS = [
    "Total Assets", "Total Liabilities Net Minority Interest",
    "Total Equity", "Common Stock Equity",
    "Cash and Cash Equivalents", "Cash Equivalents",
    "Total Debt", "Long Term Debt", "Short Term Debt",
    "Net Receivables", "Inventory",
    "Property Plant and Equipment Net",
    "Goodwill", "Intangible Assets",
]

CASH_FLOW_KEYS = [
    "Operating Cash Flow", "Free Cash Flow",
    "Capital Expenditure",
    "Cash Flow from Continuing Investing Activities",
    "Cash Flow from Continuing Financing Activities",
    "Depreciation and Amortization",
    "Stock Based Compensation",
    "Dividends Paid", "Share Issuance", "Share Repurchase",
    "Net Income",
]


def fetch_financials(
    tickers: list[str],
    financial_type: str = "income_statement",
    period: str = "annual",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Fetch financial statements for given tickers."""
    tickers = tickers[:limit]
    results = []

    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            stmt = _get_statement(t, financial_type, period)

            if stmt is None or stmt.empty:
                results.append(_no_data(ticker, financial_type))
                continue

            keys = _keys_for_type(financial_type)
            filtered = _extract_keys(stmt, keys)
            results.append({
                "tool": "stock_financials",
                "ticker": ticker,
                "data": {
                    "statement_type": financial_type,
                    "period": period,
                    "currency": getattr(stmt, "currency", "USD"),
                    "fiscal_years": list(filtered.keys()) if isinstance(filtered, dict) else [],
                    "line_items": filtered,
                },
                "source": "yfinance",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "cache_ttl": 3600,
            })
        except Exception as e:
            logger.warning(f"Financials failed for {ticker}: {e}")
            results.append(_no_data(ticker, financial_type))

    return results


def _get_statement(t: yf.Ticker, ftype: str, period: str):
    """Retrieve the appropriate yfinance statement."""
    if ftype == "income_statement":
        return t.income_stmt if period == "annual" else t.quarterly_income_stmt
    elif ftype == "balance_sheet":
        return t.balance_sheet if period == "annual" else t.quarterly_balance_sheet
    elif ftype == "cash_flow":
        return t.cashflow if period == "annual" else t.quarterly_cashflow
    return None


def _keys_for_type(ftype: str) -> list[str]:
    return {
        "income_statement": INCOME_KEYS,
        "balance_sheet": BALANCE_KEYS,
        "cash_flow": CASH_FLOW_KEYS,
    }.get(ftype, [])


def _extract_keys(stmt, keys: list[str]) -> dict[str, Any]:
    """Extract only relevant keys from yfinance statement."""
    result = {}
    available_keys = set(stmt.index) if hasattr(stmt, "index") else set()

    for key in keys:
        if key in available_keys:
            row = stmt.loc[key]
            # Convert to dict with period labels
            if hasattr(row, "to_dict"):
                values = row.to_dict()
                # Convert Timestamp keys to strings
                result[key] = {
                    str(k): _safe_number(v) for k, v in values.items()
                }
            else:
                result[key] = _safe_number(row)

    # Also add any rows not in our key list but present
    return result


def _safe_number(val) -> Any:
    """Convert numpy types to Python types."""
    if val is None:
        return None
    try:
        if hasattr(val, "item"):
            return val.item()
        return float(val) if val != 0 else 0
    except (TypeError, ValueError):
        return None


def _no_data(ticker: str, ftype: str) -> dict[str, Any]:
    return {
        "tool": "stock_financials",
        "ticker": ticker,
        "data": {"statement_type": ftype, "error": f"No {ftype} data available for {ticker}"},
        "source": "error",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cache_ttl": 300,
    }