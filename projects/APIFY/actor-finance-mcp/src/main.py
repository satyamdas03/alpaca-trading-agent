"""Finance Data MCP Server — Apify Actor entry point.

10 financial data tools for AI agents:
  stock_quote, stock_financials, stock_analysis, market_overview,
  economic_indicators, crypto_prices, currency_rates, sec_filings,
  earnings_calendar, news_sentiment

PPE events:
  financial_data_retrieved  — base event for every successful data fetch
  stock_analysis_completed  — premium event for full analysis
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from apify import Actor

from cache import FinanceCache
from tools.stock_quote import fetch_stock_quotes
from tools.stock_financials import fetch_financials
from tools.stock_analysis import fetch_analysis
from tools.market_overview import fetch_market_overview
from tools.economic_indicators import fetch_economic_indicators
from tools.crypto_prices import fetch_crypto_prices
from tools.currency_rates import fetch_currency_rates
from tools.sec_filings import fetch_sec_filings
from tools.earnings_calendar import fetch_earnings_calendar
from tools.news_sentiment import fetch_news_sentiment
from validators import validate_input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PPE event names
EVT_DATA = "financial_data_retrieved"
EVT_ANALYSIS = "stock_analysis_completed"

# PPE pricing (set in Apify Console — these are reference values)
# financial_data_retrieved: $0.05/event
# stock_analysis_completed: $0.10/event

# Tool → function mapping
TOOL_ROUTER: dict[str, Any] = {
    "stock_quote": fetch_stock_quotes,
    "stock_financials": fetch_financials,
    "stock_analysis": fetch_analysis,
    "market_overview": fetch_market_overview,
    "economic_indicators": fetch_economic_indicators,
    "crypto_prices": fetch_crypto_prices,
    "currency_rates": fetch_currency_rates,
    "sec_filings": fetch_sec_filings,
    "earnings_calendar": fetch_earnings_calendar,
    "news_sentiment": fetch_news_sentiment,
}

cache = FinanceCache()


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        validated = validate_input(actor_input)

        tool = validated["tool"]
        tickers = validated["tickers"]
        financial_type = validated["financial_type"]
        period = validated["period"]
        indicators = validated["indicators"]
        filing_type = validated["filing_type"]
        query = validated["query"]
        limit = validated["limit"]

        logger.info(f"Tool: {tool}, Tickers: {tickers}, Limit: {limit}")

        # Check cache first
        cache_key = f"{tool}:{':'.join(tickers[:5])}:{financial_type}:{period}:{limit}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key}")
            await Actor.push_data(cached)
            await Actor.charge(event_name=EVT_DATA, count=1)
            return

        # Route to appropriate tool
        try:
            if tool == "stock_quote":
                results = fetch_stock_quotes(tickers, limit)
            elif tool == "stock_financials":
                results = fetch_financials(tickers, financial_type, period, limit)
            elif tool == "stock_analysis":
                results = fetch_analysis(tickers, period, limit)
            elif tool == "market_overview":
                results = fetch_market_overview(limit)
            elif tool == "economic_indicators":
                results = fetch_economic_indicators(indicators, limit)
            elif tool == "crypto_prices":
                results = fetch_crypto_prices(tickers, limit)
            elif tool == "currency_rates":
                results = fetch_currency_rates(tickers, limit)
            elif tool == "sec_filings":
                results = fetch_sec_filings(tickers, filing_type, limit)
            elif tool == "earnings_calendar":
                results = fetch_earnings_calendar(tickers, limit)
            elif tool == "news_sentiment":
                results = fetch_news_sentiment(tickers, query, limit)
            else:
                raise ValueError(f"Unknown tool: {tool}")
        except Exception as e:
            logger.error(f"Tool {tool} failed: {e}", exc_info=True)
            await Actor.push_data({
                "tool": tool,
                "error": str(e),
                "status": "error",
            })
            # Still charge for the attempt (data retrieval event)
            await Actor.charge(event_name=EVT_DATA, count=1)
            return

        # Push results and charge
        if isinstance(results, list):
            for item in results:
                await Actor.push_data(item)
        else:
            await Actor.push_data(results)

        # Cache the results
        cache.set(cache_key, results if isinstance(results, list) else [results])

        # Charge PPE events
        # Base event for every data retrieval
        data_count = len(results) if isinstance(results, list) else 1
        await Actor.push_data()  # Ensure all data is flushed before charging
        await Actor.charge(event_name=EVT_DATA, count=data_count)

        # Premium event for stock analysis
        if tool == "stock_analysis" and isinstance(results, list):
            await Actor.charge(event_name=EVT_ANALYSIS, count=len(results))

        logger.info(f"Completed {tool}: {data_count} results pushed, {data_count} PPE events charged")


if __name__ == "__main__":
    asyncio_run = None
    try:
        import asyncio
        asyncio_run = asyncio.run
    except ImportError:
        pass

    if asyncio_run:
        asyncio_run(main())
    else:
        import uvloop
        uvloop.install()
        import asyncio
        asyncio.run(main())