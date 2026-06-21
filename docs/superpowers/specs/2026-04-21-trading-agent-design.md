# Alpaca Trading Agent — Design Specification

**Date:** 2026-04-21
**Status:** Approved
**Author:** Satyam Das + Claude Code

---

## Overview

A 24/7 autonomous AI trading agent built on Claude Code with Alpaca MCP integration. Runs on scheduled routines (cron), researches markets using live data + web search, executes trades via Alpaca paper trading, and notifies via email. Inspired by the NeuralQuant research methodology for depth and transparency.

**Goal:** Beat S&P 500 using fundamentals-driven swing trading. Paper trading mode — aggressive experimentation allowed.

---

## Architecture

```
Scheduled Trigger (cron)
  → Claude Code session wakes up stateless
  → Reads memory files (strategy, portfolio state, trade log, lessons)
  → Runs research phase (Alpaca MCP data + WebSearch + Claude analysis)
  → Makes trading decision with cited data points
  → Executes via Alpaca MCP tools
  → Updates memory files + git push
  → Sends email summary via Gmail MCP
```

---

## Components

### 1. Alpaca MCP Server

- **Tool:** `uvx alpaca-mcp-server` via Claude Code MCP integration
- **Mode:** Paper trading (ALPACA_PAPER_TRADE=true)
- **Toolsets enabled:** all (account, trading, stock-data, crypto-data, options-data, news, assets, watchlists, corporate-actions)
- **Key tools used:**
  - `get_account_info` — Portfolio balance, margin status
  - `get_portfolio_history` — Equity/P&L over time
  - `get_all_positions` — Current holdings
  - `place_stock_order`, `place_crypto_order`, `place_option_order` — Trade execution
  - `get_stock_bars`, `get_stock_snapshot` — Market data
  - `get_crypto_bars`, `get_crypto_snapshot` — Crypto data
  - `get_news` — Market news
  - `get_most_active_stocks`, `get_market_movers` — Screeners
  - `get_option_chain` — Options analysis
  - `get_clock`, `get_calendar` — Market hours

### 2. Memory Files

All git-tracked. Each routine reads on wake, updates before sleep. Pushed to GitHub after each run.

| File | Purpose | Updated By |
|------|---------|-----------|
| `memory/STRATEGY.md` | Trading rules, factor weights, signal definitions, regime logic | Weekly review, manual edits |
| `memory/PORTFOLIO_STATE.md` | Current positions, cash, P/L, allocation, last-updated timestamp | Every routine |
| `memory/TRADE_LOG.md` | Chronological trade entries (timestamp, symbol, side, qty, price, rationale) | On every trade |
| `memory/RESEARCH_LOG.md` | Research findings per session (catalysts, data points, analysis) | Pre-market, midday |
| `memory/LESSONS_LEARNED.md` | What worked, what didn't, adjustments made over time | Weekly review, ad hoc |
| `memory/WEEKLY_REVIEW.md` | End-of-week performance analysis vs S&P benchmark | Weekly review |

### 3. Research Methodology

Inspired by NeuralQuant's depth and transparency requirements.

**Data Sources:**
- **Alpaca MCP:** Live portfolio data, market data (bars, quotes, snapshots, news), option chains, corporate actions
- **WebSearch/WebFetch:** Earnings reports, SEC filings, macro data (FRED/BEA), sector trends, geopolitical events, analyst upgrades/downgrades
- **Claude Analysis:** Multi-factor synthesis with regime context

**Analysis Framework (per session):**
1. **Macro context:** Market regime assessment (risk-on/risk-off), VIX level, yield curve, Fed policy
2. **Universe scan:** Most active stocks, market movers, sector rotation signals
3. **Individual ticker deep-dive:** Quality (margins, Piotroski), Momentum (12-1 return), Value (P/E, P/B relative to sector), Sentiment (short interest, news, insider activity)
4. **Trade decision:** Cite specific data points. No "I think X is good." Must show numbers and sources.

**Transparency Rule:** Every trade must include:
- Specific data points that triggered the signal (with values)
- Source of each data point (Alpaca, WebSearch, etc.)
- Risk factors and counter-arguments
- Position sizing rationale

### 4. Notification System

**Gmail MCP** → satyamdas03@gmail.com

| Trigger | Content |
|---------|---------|
| Trade executed | Symbol, side, qty, price, rationale |
| Market close | Daily P&L, positions, portfolio value, % change |
| Weekly review | Weekly performance vs S&P, strategy adjustments, lessons |
| Urgent | Large drawdown, circuit breaker hit, market anomaly |

### 5. Scheduled Routines

All times US Eastern. Weekdays only (Mon-Fri).

| Routine | Cron (ET) | Purpose |
|---------|-----------|---------|
| Pre-market | `0 6 * * 1-5` | Research overnight catalysts, macro scan, draft trade ideas |
| Market Open | `30 9 * * 1-5` | Execute planned trades, set trailing stops on new positions |
| Midday | `0 12 * * 1-5` | Review positions, cut losers (-7% stop-loss default), tighten stops on winners |
| Market Close | `0 16 * * 1-5` | Final position review, journal, send daily summary email |
| Weekly Review | `0 16 * * 5` | Performance analysis, strategy adjustments, update LESSONS_LEARNED |

### 6. Project Structure

```
alpacaIntegrationWithClaudeCode/
├── CLAUDE.md                    # Agent instructions, rules, research methodology
├── README.md                    # High-quality project documentation
├── memory/
│   ├── STRATEGY.md              # Trading strategy, factors, signals
│   ├── PORTFOLIO_STATE.md       # Current positions and state
│   ├── TRADE_LOG.md             # Trade history
│   ├── RESEARCH_LOG.md          # Research findings
│   ├── LESSONS_LEARNED.md       # Learning over time
│   └── WEEKLY_REVIEW.md         # Weekly performance reviews
├── routines/
│   ├── pre_market.md             # Prompt for 6 AM run
│   ├── market_open.md            # Prompt for 9:30 AM run
│   ├── midday.md                 # Prompt for 12 PM run
│   ├── market_close.md           # Prompt for 4 PM run
│   └── weekly_review.md          # Prompt for Friday 4 PM run
├── skills/
│   ├── research.md               # How to do deep research
│   ├── trade_execution.md         # How to place trades via Alpaca MCP
│   ├── notification.md            # How to send email summaries
│   └── journal.md                 # How to update memory files
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-04-21-trading-agent-design.md
```

### 7. GitHub Repository

- **Public repo** on github.com/satyamdas03
- **High-quality README** with badges, architecture diagram, setup instructions, strategy overview, disclaimer
- **Updated continuously** as project evolves
- **Each routine git pushes** memory file changes so next session reads updated state

### 8. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Research method | WebSearch + Alpaca data + Claude analysis | No Perplexity needed; agent IS the synthesis layer |
| Notifications | Gmail MCP | No ClickUp dependency; email is universal |
| State management | Git-tracked memory files | Stateless agent pattern; each session reads/writes files |
| Trading mode | Paper trading (aggressive) | Experiment freely; learn before real money |
| Guardrails | Minimal (paper mode) | Full freedom to explore strategies |
| Agent model | Claude Opus 4.7 | Best agentic financial analysis per benchmarks |
| Transparency | Required data citations per trade | NeuralQuant-style; no blackbox decisions |

---

## Implementation Steps

1. Install `uv` package manager
2. Add Alpaca MCP server to Claude Code
3. Create GitHub repository (public, high-quality README)
4. Create CLAUDE.md with agent instructions
5. Create memory files (initial state)
6. Create skill files (research, trade, notification, journal)
7. Create routine prompts (5 schedules)
8. Set up Gmail notification integration
9. Set up scheduled triggers (cron jobs)
10. Test with a manual dry run