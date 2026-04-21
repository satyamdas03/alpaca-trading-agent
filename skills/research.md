# Research Skill

## Purpose
Deep, transparent market research inspired by NeuralQuant's methodology.

## Process

### 1. Macro Context (5 minutes)
- Use `WebSearch` for: "VIX current level", "federal reserve interest rate decision", "treasury yield curve today"
- Use `get_clock` to check market status
- Use `get_news` for overnight market-moving headlines
- Determine regime: Risk-On / Late Cycle / Stress / Recovery
- Document regime assessment in RESEARCH_LOG

### 2. Universe Scan (10 minutes)
- Use `get_most_active_stocks` for volume leaders
- Use `get_market_movers` for top gainers and losers
- Use `WebSearch` for: "earnings calendar this week", "sector rotation today"
- Build a watchlist of 5-10 candidates

### 3. Ticker Deep-Dive (15-20 minutes)
For each candidate:
- `get_stock_snapshot` — current price, day change, volume
- `get_stock_bars` — 14-month history for momentum calculation
- `WebSearch` — "[TICKER] earnings report", "[TICKER] analyst ratings", "[TICKER] insider trading"
- Rate each factor: Quality, Momentum, Value, Sentiment
- Record data points with EXACT values and sources

### 4. Synthesis
- Combine factor ratings into composite score
- Weight by current regime
- Generate trade ideas with full data citations
- Record in RESEARCH_LOG with timestamp

## Data Citation Format
Every data point MUST include:
- Exact value (e.g., "AAPL P/E 22.3")
- Source (e.g., "Alpaca get_stock_snapshot")
- Comparison (e.g., "vs sector avg 28.1")

Example:
```
AAPL Research Summary:
- Quality: Gross margin 58.3% (Alpaca), Piotroski 7/9 (WebSearch)
- Momentum: 12-1 return +14.2% (Alpaca get_stock_bars), SPX +8.1% → relative strength +6.1%
- Value: P/E 22.3 vs sector 28.1 (Alpaca) → 20% discount to sector
- Sentiment: Short interest 1.2% (Alpaca), positive earnings beat (WebSearch)
- Composite: 8.4/10 — STRONG BUY candidate
```

## Anti-Patterns (NEVER do these)
- Vague claims without numbers: "AAPL looks good"
- Uncited data: "P/E is low" without the actual P/E value
- Generic market commentary: "The market is bullish"
- Skipping the macro step
- Making trade decisions before research is complete