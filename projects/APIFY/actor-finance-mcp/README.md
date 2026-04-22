# Finance Data MCP Server

**Real-time financial data for AI agents — 10 tools, 2 markets, 0 API keys needed.**

Covers US (NYSE/NASDAQ) and India (NSE/BSE) markets. Designed for MCP/AI agent consumption with structured, clean output and intelligent fallbacks.

## Tools

| Tool | Description | PPE Event | Cache TTL |
|------|-------------|-----------|-----------|
| `stock_quote` | Real-time/delayed prices, volume, change | `financial_data_retrieved` ($0.05) | 60s |
| `stock_financials` | Income statement, balance sheet, cash flow | `financial_data_retrieved` ($0.05) | 1h |
| `stock_analysis` | Analyst recommendations, price targets, key stats | `financial_data_retrieved` + `stock_analysis_completed` ($0.10) | 30m |
| `market_overview` | Major indices, sector performance, market status | `financial_data_retrieved` ($0.05) | 2m |
| `economic_indicators` | GDP, inflation, interest rates, unemployment | `financial_data_retrieved` ($0.05) | 24h |
| `crypto_prices` | BTC, ETH, and 15+ altcoin prices with 24h stats | `financial_data_retrieved` ($0.05) | 30s |
| `currency_rates` | 15+ forex pairs with change tracking | `financial_data_retrieved` ($0.05) | 5m |
| `sec_filings` | Search SEC EDGAR filings by ticker and type | `financial_data_retrieved` ($0.05) | 24h |
| `earnings_calendar` | Upcoming earnings dates, EPS estimates | `financial_data_retrieved` ($0.05) | 1h |
| `news_sentiment` | Financial news with keyword sentiment scoring | `financial_data_retrieved` ($0.05) | 10m |

## Usage

### Stock Quote
```json
{
  "tool": "stock_quote",
  "tickers": ["NVDA", "RELIANCE.NS", "AAPL"]
}
```

### Stock Financials
```json
{
  "tool": "stock_financials",
  "tickers": ["AAPL"],
  "financial_type": "income_statement",
  "period": "annual"
}
```

### Stock Analysis
```json
{
  "tool": "stock_analysis",
  "tickers": ["TCS.NS", "MSFT"],
  "period": "quarterly"
}
```

### Market Overview
```json
{
  "tool": "market_overview"
}
```

### Economic Indicators
```json
{
  "tool": "economic_indicators",
  "indicators": ["GDP", "INFLATION", "INTEREST_RATE", "UNEMPLOYMENT"]
}
```

### Crypto Prices
```json
{
  "tool": "crypto_prices",
  "tickers": ["BTC-USD", "ETH-USD", "SOL-USD"]
}
```

### Currency Rates
```json
{
  "tool": "currency_rates",
  "tickers": ["EURUSD=X", "USDINR=X"]
}
```

### SEC Filings
```json
{
  "tool": "sec_filings",
  "tickers": ["AAPL"],
  "filing_type": "10-K",
  "limit": 5
}
```

### Earnings Calendar
```json
{
  "tool": "earnings_calendar",
  "tickers": ["NVDA", "TSLA"]
}
```

### News Sentiment
```json
{
  "tool": "news_sentiment",
  "tickers": ["AAPL"],
  "limit": 10
}
```

## India Market Support

For NSE stocks, use `.NS` suffix: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`
For BSE stocks, use `.BO` suffix: `RELIANCE.BO`

## Data Sources

| Source | Tools | Notes |
|--------|-------|-------|
| Yahoo Finance (yfinance) | Most tools | Free, no API key needed |
| SEC EDGAR | sec_filings | Free, public data |
| FRED (optional) | economic_indicators | Set `FRED_API_KEY` env var for live data |

## PPE Pricing

- `financial_data_retrieved`: **$0.05** per data point returned
- `stock_analysis_completed`: **$0.10** per full analysis (additional on top of base event)

## Architecture

```
src/
├── main.py              # Entry point, tool routing, PPE charging
├── cache.py             # TTL cache layer
├── validators.py        # Input validation
└── tools/
    ├── stock_quote.py
    ├── stock_financials.py
    ├── stock_analysis.py
    ├── market_overview.py
    ├── economic_indicators.py
    ├── crypto_prices.py
    ├── currency_rates.py
    ├── sec_filings.py
    ├── earnings_calendar.py
    └── news_sentiment.py
```

## MCP Integration

This actor is designed for MCP (Model Context Protocol) consumption. AI agents can call it as a tool with structured input/output, making it ideal for:
- Claude Code MCP integrations
- Cursor IDE data lookups
- ChatGPT custom GPTs
- Any AI agent that needs financial data