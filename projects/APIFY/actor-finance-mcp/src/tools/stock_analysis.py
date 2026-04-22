"""Stock analysis tool — analyst recommendations, price targets, insider activity."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_analysis(tickers: list[str], period: str = "annual", limit: int = 20) -> list[dict[str, Any]]:
    """Fetch analyst recommendations, price targets, and key stats."""
    tickers = tickers[:limit]
    results = []

    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}

            recommendations = _safe_recommendations(t)
            price_targets = _price_targets(info)
            key_stats = _key_stats(info)
            insider_info = _insider_info(info)

            results.append({
                "tool": "stock_analysis",
                "ticker": ticker,
                "data": {
                    "company_name": info.get("longName") or info.get("shortName"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "market_cap": info.get("marketCap"),
                    "recommendations": recommendations,
                    "price_targets": price_targets,
                    "key_stats": key_stats,
                    "insider": insider_info,
                },
                "source": "yfinance",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "cache_ttl": 1800,
            })
        except Exception as e:
            logger.warning(f"Analysis failed for {ticker}: {e}")
            results.append({
                "tool": "stock_analysis",
                "ticker": ticker,
                "data": {"error": f"Analysis unavailable for {ticker}: {str(e)}"},
                "source": "error",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "cache_ttl": 300,
            })

    return results


def _safe_recommendations(t: yf.Ticker) -> list[dict[str, Any]]:
    """Fetch analyst recommendations with error handling."""
    try:
        recs = t.recommendations
        if recs is None or recs.empty:
            return []
        recent = recs.tail(10)
        return [
            {
                "period": str(row.get("period", "")) if "period" in row.index else "",
                "strong_buy": int(row.get("strongBuy", 0)) if "strongBuy" in row.index else 0,
                "buy": int(row.get("buy", 0)) if "buy" in row.index else 0,
                "hold": int(row.get("hold", 0)) if "hold" in row.index else 0,
                "sell": int(row.get("sell", 0)) if "sell" in row.index else 0,
                "strong_sell": int(row.get("strongSell", 0)) if "strongSell" in row.index else 0,
            }
            for _, row in recent.iterrows()
        ]
    except Exception:
        return []


def _price_targets(info: dict) -> dict[str, Any]:
    """Extract price target information."""
    return {
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "target_low": info.get("targetLowPrice"),
        "target_mean": info.get("targetMeanPrice"),
        "target_median": info.get("targetMedianPrice"),
        "target_high": info.get("targetHighPrice"),
        "number_of_analysts": info.get("numberOfAnalystOpinions"),
        "recommendation_key": info.get("recommendationKey"),
        "recommendation_mean": info.get("recommendationMean"),
    }


def _key_stats(info: dict) -> dict[str, Any]:
    """Extract key valuation and growth stats."""
    return {
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),
        "price_to_book": info.get("priceToBook"),
        "ev_to_revenue": info.get("enterpriseToRevenue"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),
        "profit_margin": info.get("profitMargins"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "dividend_yield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "52_week_high": info.get("fiftyTwoWeekHigh"),
        "52_week_low": info.get("fiftyTwoWeekLow"),
        "50_day_ma": info.get("fiftyDayAverage"),
        "200_day_ma": info.get("twoHundredDayAverage"),
        "short_ratio": info.get("shortRatio"),
        "short_pct_float": info.get("shortPercentOfFloat"),
    }


def _insider_info(info: dict) -> dict[str, Any]:
    """Extract insider trading summary."""
    return {
        "held_percent_insiders": info.get("heldPercentInsiders"),
        "held_percent_institutions": info.get("heldPercentInstitutions"),
        "insider_transactions_last_6m": info.get("insiderTransactions"),
    }