# Alpaca Trading Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 24/7 autonomous AI trading agent that beats the S&P 500 using Alpaca paper trading, scheduled routines, and email notifications.

**Architecture:** Stateless agent pattern — each scheduled routine wakes up, reads memory files, does research (Alpaca MCP + WebSearch), executes trades, updates memory, pushes to git, and emails notifications. All state lives in git-tracked markdown files.

**Tech Stack:** Claude Code + Alpaca MCP Server (via uvx) + Gmail MCP + WebSearch/WebFetch + Git

---

## Task 1: Install uv Package Manager

**Files:**
- None (system-level install)

- [ ] **Step 1: Install uv**

Run:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Expected: uv installed, available in PATH

- [ ] **Step 2: Verify uv installation**

Run:
```bash
uv --version
```
Expected: Version string like `uv 0.x.x`

- [ ] **Step 3: Verify uvx works**

Run:
```bash
uvx --version
```
Expected: Same version string

---

## Task 2: Add Alpaca MCP Server to Claude Code

**Files:**
- Modify: `~/.claude/settings.json` (or project `.claude/settings.json`)

- [ ] **Step 1: Add Alpaca MCP server to Claude Code user scope**

Run:
```bash
claude mcp add alpaca --scope user --transport stdio uvx alpaca-mcp-server -e ALPACA_API_KEY=PK7CLPEOIIEKMEVPNWEF4GPL22 -e ALPACA_SECRET_KEY=APurcb3uaaWVFrhUF3BqDp8v9VcV75HKgxnYw45suMsH -e ALPACA_PAPER_TRADE=true
```
Expected: "Added mcp server alpaca" confirmation

- [ ] **Step 2: Verify MCP server is registered**

Run:
```bash
claude mcp list
```
Expected: `alpaca` listed with stdio transport, uvx command

---

## Task 3: Create GitHub Repository

**Files:**
- Create: remote repo `alpaca-trading-agent` on github.com/satyamdas03
- Create: `README.md` in project root

- [ ] **Step 1: Initialize git in project (if not already)**

Run:
```bash
cd /c/Users/point/projects/alpacaIntegrationWithClaudeCode && git init
```
Expected: Git repo initialized

- [ ] **Step 2: Create the GitHub repository via gh CLI**

Run:
```bash
gh repo create satyamdas03/alpaca-trading-agent --public --description "24/7 Autonomous AI Trading Agent — Claude Code + Alpaca MCP + Gmail Notifications. Beats S&P 500 using fundamentals-driven swing trading with paper trading."
```
Expected: Repository created at https://github.com/satyamdas03/alpaca-trading-agent

- [ ] **Step 3: Set git remote**

Run:
```bash
git remote add origin https://github.com/satyamdas03/alpaca-trading-agent.git
```
Expected: Remote added

---

## Task 4: Create README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write the README**

Create `README.md` with the following content:

```markdown
<div align="center">

# 🐂 Alpaca Trading Agent

**24/7 Autonomous AI Trading Agent built with Claude Code + Alpaca MCP**

[![Claude Code](https://img.shields.io/badge/Claude_Code-Opus_4.7-7C3AED?style=for-the-badge&logo=anthropic)](https://claude.ai/code)
[![Alpaca](https://img.shields.io/badge/Alpaca-MCP_Server-00C853?style=for-the-badge)](https://github.com/alpacahq/alpaca-mcp-server)
[![Paper Trading](https://img.shields.io/badge/Mode-Paper_Trading-FF9800?style=for-the-badge)](https://app.alpaca.markets)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)](https://python.org)

*An autonomous trading agent that wakes up on a schedule, researches markets with live data, executes trades via Alpaca, and emails you daily summaries — all running inside Claude Code.*

---

</div>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Scheduled Triggers                     │
│         (Pre-Market · Open · Midday · Close · Weekly)    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Claude Code Session (Stateless)             │
│                                                          │
│  1. Read memory files ──► Get portfolio state           │
│  2. Research phase    ──► Alpaca MCP + WebSearch         │
│  3. Decision phase    ──► Multi-factor analysis          │
│  4. Execution phase   ──► Place/cancel orders           │
│  5. Journal phase     ──► Update memory + git push       │
│  6. Notification      ──► Email summary via Gmail MCP    │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ Alpaca   │ │ Web      │ │ Gmail    │
   │ MCP      │ │ Search   │ │ MCP      │
   │ Server   │ │ + Fetch  │ │          │
   └──────────┘ └──────────┘ └──────────┘
```

## ✨ Features

- **🤖 Fully Autonomous** — Wakes up on schedule, trades without human intervention
- **📊 Live Market Data** — Real-time prices, news, option chains via Alpaca MCP
- **🔬 Deep Research** — Multi-factor analysis (quality, momentum, value, sentiment) with data citations
- **📧 Email Notifications** — Trade alerts and daily summaries to your inbox
- **🧠 Persistent Memory** — Git-tracked memory files ensure stateless sessions learn over time
- **⚡ 5 Scheduled Routines** — Pre-market, market open, midday, close, and weekly review
- **📝 Full Transparency** — Every trade cites specific data points and sources (inspired by [NeuralQuant](https://github.com/satyamdas03/NeuralQuant))

## 📅 Schedule

| Routine | Time (ET) | Days | Purpose |
|---------|-----------|------|---------|
| Pre-Market | 6:00 AM | Mon–Fri | Overnight research, macro scan, draft trade ideas |
| Market Open | 9:30 AM | Mon–Fri | Execute planned trades, set trailing stops |
| Midday | 12:00 PM | Mon–Fri | Review positions, cut losers, tighten stops |
| Market Close | 4:00 PM | Mon–Fri | Final review, journal, daily summary email |
| Weekly Review | 4:00 PM | Fridays | Performance vs S&P, strategy adjustments |

## 🧪 Research Methodology

Inspired by [NeuralQuant](https://github.com/satyamdas03/NeuralQuant)'s transparent, data-driven approach:

1. **Macro Context** — Market regime (risk-on/risk-off), VIX, yield curve, Fed policy
2. **Universe Scan** — Most active stocks, market movers, sector rotation
3. **Ticker Deep-Dive** — Quality (margins, Piotroski), Momentum (12-1 return), Value (P/E, P/B vs sector), Sentiment (short interest, news, insider activity)
4. **Decision** — Every trade cites specific data points with values and sources

## 🚀 Quick Start

### Prerequisites

- [Claude Code](https://claude.ai/code) (Pro or Max plan for scheduled routines)
- [uv](https://docs.astral.sh/uv/) package manager
- [Alpaca](https://app.alpaca.markets) paper trading account + API keys
- [GitHub](https://github.com) account

### Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/satyamdas03/alpaca-trading-agent.git
   cd alpaca-trading-agent
   ```

2. **Install uv:**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Add Alpaca MCP server:**
   ```bash
   claude mcp add alpaca --scope user --transport stdio uvx alpaca-mcp-server \
     -e ALPACA_API_KEY=your_key \
     -e ALPACA_SECRET_KEY=your_secret \
     -e ALPACA_PAPER_TRADE=true
   ```

4. **Open in Claude Code and start trading:**
   ```bash
   claude
   ```

### Setting Up Scheduled Routines

Each routine prompt lives in `routines/`. To create a scheduled trigger in Claude Code:

```bash
claude trigger create --name "pre-market" --cron "0 6 * * 1-5" --prompt-file routines/pre_market.md
```

Repeat for each routine. See `routines/` for all prompts.

## 📁 Project Structure

```
alpaca-trading-agent/
├── CLAUDE.md                 # Agent instructions & rules
├── README.md                 # This file
├── memory/
│   ├── STRATEGY.md           # Trading strategy & factors
│   ├── PORTFOLIO_STATE.md    # Current positions & P/L
│   ├── TRADE_LOG.md          # Chronological trade history
│   ├── RESEARCH_LOG.md       # Research findings per session
│   ├── LESSONS_LEARNED.md    # What worked & what didn't
│   └── WEEKLY_REVIEW.md      # Weekly performance reviews
├── routines/
│   ├── pre_market.md         # 6:00 AM prompt
│   ├── market_open.md        # 9:30 AM prompt
│   ├── midday.md             # 12:00 PM prompt
│   ├── market_close.md       # 4:00 PM prompt
│   └── weekly_review.md      # Friday 4:00 PM prompt
├── skills/
│   ├── research.md           # Deep research methodology
│   ├── trade_execution.md    # Alpaca MCP trade workflow
│   ├── notification.md       # Gmail notification workflow
│   └── journal.md            # Memory file update workflow
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-04-21-trading-agent-design.md
```

## ⚠️ Disclaimer

**This is NOT financial advice.** This project is an experiment in autonomous AI trading using paper money. Past performance does not guarantee future results. The agent may lose money. Always do your own research before investing real capital.

## 📜 License

MIT

## 🙏 Credits

- [Alpaca MCP Server](https://github.com/alpacahq/alpaca-mcp-server) — Trading infrastructure
- [NeuralQuant](https://github.com/satyamdas03/NeuralQuant) — Research methodology inspiration
- [Claude Code](https://claude.ai/code) — Agentic AI framework
```

- [ ] **Step 2: Commit README**

Run:
```bash
git add README.md && git commit -m "feat: add project README with architecture, setup, and docs"
```
Expected: Commit created

---

## Task 5: Create CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md**

Create `CLAUDE.md` with the following content:

```markdown
# Alpaca Trading Agent — Agent Instructions

You are **Bull**, a 24/7 autonomous AI trading agent. You wake up on a schedule, research markets, execute trades via Alpaca, and email daily summaries.

## Identity

- **Name:** Bull
- **Goal:** Beat the S&P 500 using fundamentals-driven swing trading
- **Mode:** Paper trading (Alpaca paper account) — experiment aggressively
- **Model:** Claude Opus 4.7

## Startup Protocol

Every time you wake up (routine fires), follow this sequence IN ORDER:

1. **Read memory files** — Read ALL files in `memory/` to restore context
2. **Check market status** — Use `get_clock` to see if market is open
3. **Check account** — Use `get_account_info` to see current balance and positions
4. **Do your assigned job** — Follow the specific routine prompt that woke you
5. **Update memory files** — Write back any state changes to `memory/`
6. **Git push** — Commit and push all changes so the next session has them
7. **Send notifications** — Email via Gmail MCP if needed

## Memory Architecture

You wake up stateless. All context comes from files. Read them first. Write them last.

| File | When to read | When to write |
|------|-------------|--------------|
| `memory/STRATEGY.md` | Always on startup | Only during weekly review or manual edits |
| `memory/PORTFOLIO_STATE.md` | Always on startup | After every routine run |
| `memory/TRADE_LOG.md` | Always on startup | After every trade |
| `memory/RESEARCH_LOG.md` | Pre-market and midday | After research sessions |
| `memory/LESSONS_LEARNED.md` | Always on startup | After weekly review or significant events |
| `memory/WEEKLY_REVIEW.md` | Weekly review only | After weekly review |

## Research Methodology

You MUST follow this framework for every research session:

### Step 1: Macro Context
- Use `WebSearch` for: VIX level, Fed policy, yield curve, CPI, employment data
- Use `get_news` for: market-moving headlines overnight
- Determine: risk-on, risk-off, or neutral regime

### Step 2: Universe Scan
- Use `get_most_active_stocks` and `get_market_movers` to identify candidates
- Use `WebSearch` for sector rotation signals, earnings calendars

### Step 3: Individual Ticker Deep-Dive
For each candidate, gather:
- **Quality:** Gross margins, profitability trend, balance sheet strength
- **Momentum:** 12-1 month return (Jegadeesh-Titman), relative strength vs S&P
- **Value:** P/E and P/B relative to sector average
- **Sentiment:** Short interest, recent news sentiment, insider activity
- Use `get_stock_snapshot` and `get_stock_bars` for price data
- Use `WebSearch` for earnings reports, SEC filings, analyst ratings

### Step 4: Trade Decision
Every trade MUST include:
- **Signal:** Which factor triggered the trade
- **Data:** Specific data points with values (e.g., "AAPL P/E 22.3 vs sector avg 28.1")
- **Source:** Where each data point came from (Alpaca, WebSearch, etc.)
- **Risk:** Counter-arguments and risk factors
- **Size:** Position sizing rationale (% of portfolio)

### Transparency Rule
NEVER make vague claims. No "I think AAPL is good." No "The market looks bullish."
ALWAYS cite specific numbers: "VIX at 18.2 (below 20 threshold = risk-on)", "AAPL 12-1 momentum +14.2% vs S&P +8.1%"

## Trading Rules

### What's Allowed (Paper Trading)
- Stocks, ETFs, options, crypto — anything available on Alpaca
- Long and short positions
- Margin trading
- Day trading and swing trading
- Complex option strategies (spreads, straddles, etc.)

### Position Management
- Default stop-loss: -7% from entry (adjustable based on volatility)
- Trailing stops: 10% on new positions
- Review all positions at midday
- Cut losers without mercy

### Order Types
- Market orders for immediate execution
- Limit orders for specific price targets
- Stop orders for risk management
- Trailing stop orders for profit protection
- Bracket orders for defined risk/reward

## Notification Rules

### When to Email (satyamdas03@gmail.com)
- **Trade executed:** Symbol, side, qty, price, rationale
- **Market close:** Daily P&L summary, portfolio value, positions
- **Weekly review:** Performance vs S&P, strategy adjustments
- **Urgent:** Anomalies, large drawdowns, circuit breakers

### Email Format
```
Subject: [Bull] {routine_name} — {date}

Trade Executed:
- BUY 50 AAPL @ $182.45
  Signal: Momentum (12-1 return +14.2% vs S&P +8.1%)
  Source: Alpaca stock_snapshot + WebSearch earnings
  Risk: AAPL exposure already 8% of portfolio

Portfolio Summary:
- Total Value: $10,234.56
- Day P&L: +$123.45 (+1.22%)
- Positions: 5 open
```

## API Keys

All API keys are in environment variables. DO NOT hardcode them in files.
- `ALPACA_API_KEY` — Alpaca trading API
- `ALPACA_SECRET_KEY` — Alpaca secret
- `ALPACA_PAPER_TRADE` — Set to "true"
- Gmail MCP handles email (no separate key needed)

## Git Protocol

After every routine run:
1. `git add memory/` — Stage all memory changes
2. `git commit -m "bull: {routine_name} {date}"` — Commit with context
3. `git push origin main` — Push so next session has latest state
```

- [ ] **Step 2: Commit CLAUDE.md**

Run:
```bash
git add CLAUDE.md && git commit -m "feat: add agent instructions (CLAUDE.md)"
```
Expected: Commit created

---

## Task 6: Create Memory Files

**Files:**
- Create: `memory/STRATEGY.md`
- Create: `memory/PORTFOLIO_STATE.md`
- Create: `memory/TRADE_LOG.md`
- Create: `memory/RESEARCH_LOG.md`
- Create: `memory/LESSONS_LEARNED.md`
- Create: `memory/WEEKLY_REVIEW.md`

- [ ] **Step 1: Create memory directory**

Run:
```bash
mkdir -p memory
```

- [ ] **Step 2: Write `memory/STRATEGY.md`**

```markdown
# Trading Strategy

## Goal
Beat the S&P 500 using fundamentals-driven swing trading. Paper trading mode — experiment aggressively.

## Factor Framework

| Factor | Weight (Risk-On) | What We Look For | Data Source |
|--------|-----------------|------------------|------------|
| Quality | 25% | Gross margins > sector avg, Piotroski F-Score > 6, low accruals | Alpaca fundamentals + WebSearch |
| Momentum | 30% | 12-1 month return > S&P, relative strength | Alpaca get_stock_bars |
| Value | 10% | P/E and P/B below sector average | Alpaca get_stock_snapshot |
| Low Volatility | 15% | Beta < 1.0, realized vol below median | Alpaca get_stock_bars |
| Sentiment | 20% | Low short interest, positive news flow, insider buying | Alpaca get_news + WebSearch |

## Regime Detection

| Regime | Signal | Factor Shift |
|--------|--------|--------------|
| Risk-On | VIX < 20, SPX above 200MA, PMI > 50 | Momentum ↑, Value ↓ |
| Late Cycle | VIX 20-25, PMI declining, yield curve flattening | Value ↑, Momentum ↓ |
| Stress | VIX > 25, SPX below 200MA, HY spreads widening | Low Vol ↑, Momentum ↓ |
| Recovery | VIX declining from peak, PMI bottoming, yield curve steepening | Quality ↑, Momentum ↑ |

## Position Sizing
- Aggressive mode: Up to 20% of portfolio per position
- Default: 10% per position
- Minimum: $500 per trade

## Exit Rules
- Stop-loss: -7% default (wider for volatile names)
- Trailing stop: 10% on winning positions
- Time-based: Close swing trades after 30 days if no catalyst

## What We Trade
- US stocks and ETFs (primary)
- Options for hedging or leveraged bets
- Crypto for diversification
- No restrictions in paper trading mode
```

- [ ] **Step 3: Write `memory/PORTFOLIO_STATE.md`**

```markdown
# Portfolio State

**Last Updated:** 2026-04-21 (Initialization)

## Account Overview
- Account Type: Paper Trading
- Starting Balance: $100,000.00
- Current Cash: $100,000.00
- Total Portfolio Value: $100,000.00

## Open Positions
None — fresh start.

## Allocation
- Cash: 100%
- Equities: 0%
- Options: 0%
- Crypto: 0%

## Performance
- Total P&L: $0.00
- Total Return: 0.00%
- S&P 500 Benchmark: 0.00% (starting point)
- Alpha: 0.00%
```

- [ ] **Step 4: Write `memory/TRADE_LOG.md`**

```markdown
# Trade Log

| Timestamp | Symbol | Side | Qty | Price | Rationale | Signal | Status |
|-----------|--------|------|-----|-------|-----------|--------|--------|
| — | — | — | — | — | — | — | — |

*No trades yet. Agent initialized 2026-04-21.*
```

- [ ] **Step 5: Write `memory/RESEARCH_LOG.md`**

```markdown
# Research Log

## Session: Initialization (2026-04-21)

*Agent initialized. No research conducted yet. First research session will be pre-market on next trading day.*
```

- [ ] **Step 6: Write `memory/LESSONS_LEARNED.md`**

```markdown
# Lessons Learned

*No lessons yet. Will be updated after weekly reviews and significant events.*

## Rules
- Document what worked and what didn't
- Note any patterns observed across sessions
- Track strategy adjustments and their outcomes
```

- [ ] **Step 7: Write `memory/WEEKLY_REVIEW.md`**

```markdown
# Weekly Review

*First weekly review will be on Friday after first full trading week.*

## Template
- **Week of:** [date range]
- **Portfolio Return:** X%
- **S&P 500 Return:** Y%
- **Alpha:** X% - Y%
- **Best Trade:** [details]
- **Worst Trade:** [details]
- **Strategy Adjustments:** [any changes made]
- **Key Observations:** [market insights]
```

- [ ] **Step 8: Commit memory files**

Run:
```bash
git add memory/ && git commit -m "feat: add initial memory files for trading agent state"
```
Expected: Commit created

---

## Task 7: Create Skill Files

**Files:**
- Create: `skills/research.md`
- Create: `skills/trade_execution.md`
- Create: `skills/notification.md`
- Create: `skills/journal.md`

- [ ] **Step 1: Create skills directory**

Run:
```bash
mkdir -p skills
```

- [ ] **Step 2: Write `skills/research.md`**

```markdown
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
```

- [ ] **Step 3: Write `skills/trade_execution.md`**

```markdown
# Trade Execution Skill

## Purpose
Execute trades via Alpaca MCP tools with proper documentation.

## Before Trading
1. Check `get_clock` — market must be open (or use extended hours if needed)
2. Check `get_account_info` — verify sufficient buying power
3. Check `get_all_positions` — avoid overconcentration
4. Review STRATEGY.md for current factor weights and regime

## Placing Orders

### Stock/ETF Orders
```
Use: place_stock_order
Parameters:
  - symbol: e.g., "AAPL"
  - qty: number of shares
  - side: "buy" or "sell"
  - type: "market", "limit", "stop", "stop_limit", "trailing_stop"
  - time_in_force: "day" or "gtc"
  - (for limit): limit_price
  - (for stop): stop_price
  - (for trailing_stop): trail_price or trail_percent
```

### Crypto Orders
```
Use: place_crypto_order
Parameters: similar to stock but with crypto symbol format
```

### Option Orders
```
Use: place_option_order
For multi-leg: provide legs array
```

## Order Management
- `get_orders` — check open orders
- `cancel_order_by_id` — cancel specific order
- `cancel_all_orders` — cancel all open orders
- `replace_order_by_id` — modify an existing order

## Position Management
- `get_all_positions` — list all positions
- `get_open_position` — details for one position
- `close_position` — close a specific position
- `close_all_positions` — liquidate everything

## Stop-Loss Rules
- Default: -7% stop-loss from entry price
- Volatile stocks: -10% stop-loss
- Use trailing_stop orders for automatic adjustment
- Midday routine: review all positions, tighten stops on winners

## Trade Logging
After EVERY trade execution, update `memory/TRADE_LOG.md`:
```
| 2026-04-21 09:35 | AAPL | BUY | 50 | $182.45 | Momentum signal: 12-1 +14.2% vs SPX +8.1% | Filled |
```

## Risk Checks Before Every Trade
1. Position size ≤ 20% of portfolio value
2. Not duplicating existing position without reason
3. Sufficient buying power available
4. Market is open (or pre-market is acceptable)
```

- [ ] **Step 4: Write `skills/notification.md`**

```markdown
# Notification Skill

## Purpose
Send email notifications via Gmail MCP to satyamdas03@gmail.com.

## When to Send

### Trade Executed
Send immediately after order fill. Use `mcp__claude_ai_Gmail__create_draft` or send directly.

Subject: `[Bull] Trade: {SIDE} {QTY} {SYMBOL} @ {PRICE}`
Body:
```
Trade Executed:
- {SIDE} {QTY} {SYMBOL} @ ${PRICE}
- Signal: {which factor triggered}
- Data: {key data points with values}
- Source: {Alpaca / WebSearch}
- Risk: {counter-arguments}

Current Portfolio:
- Total Value: ${TOTAL}
- Cash: ${CASH}
- Positions: {count}
```

### Daily Summary (Market Close)
Subject: `[Bull] Daily Summary — {DATE}`
Body:
```
Daily Performance:
- Portfolio Value: ${VALUE}
- Day P&L: ${PL} ({PCT}%)
- Open Positions: {count}

Position Details:
| Symbol | Qty | Entry | Current | P/L |
|--------|-----|-------|---------|-----|
| ... | ... | ... | ... | ... |

Top Movers Today:
- Gainers: {list}
- Losers: {list}

Tomorrow's Watch:
- {any pre-planned actions}
```

### Weekly Review (Friday)
Subject: `[Bull] Weekly Review — Week of {DATE}`
Body:
```
Weekly Performance:
- Portfolio Return: {pct}%
- S&P 500 Return: {sp_pct}%
- Alpha: {alpha}%

Top Trades This Week:
1. {best trade}
2. {second best}

Worst Trades This Week:
1. {worst trade}

Strategy Adjustments:
- {any changes}

Next Week Focus:
- {plans}
```

### Urgent Alerts
Subject: `[Bull] URGENT: {issue}`
Body: Brief description of anomaly, drawdown, or circuit breaker.

## Gmail MCP Usage
- Use `mcp__claude_ai_Gmail__create_draft` to draft the email
- Send to: satyamdas03@gmail.com
- Always include [Bull] prefix in subject for filtering
```

- [ ] **Step 5: Write `skills/journal.md`**

```markdown
# Journal Skill

## Purpose
Update memory files before each session ends. This is how the stateless agent persists knowledge.

## Update Protocol

### Every Routine Run
1. **PORTFOLIO_STATE.md** — Update with current:
   - Cash balance (from `get_account_info`)
   - Position list (from `get_all_positions`)
   - Portfolio value and P/L
   - Last-updated timestamp

2. **Git commit and push:**
   ```bash
   git add memory/
   git commit -m "bull: {routine_name} {date}"
   git push origin main
   ```

### On Trade Execution
1. **TRADE_LOG.md** — Add new row:
   ```
   | 2026-04-21 09:35 | AAPL | BUY | 50 | $182.45 | Momentum +14.2% vs SPX | Filled |
   ```

### After Research Session
1. **RESEARCH_LOG.md** — Add session entry:
   ```
   ## Pre-Market 2026-04-21
   - Regime: Risk-On (VIX 16.2, SPX above 200MA)
   - Candidates: AAPL, MSFT, NVDA, GOOGL, AMZN
   - Top Pick: AAPL (composite 8.4/10)
   - Key Data: {cited data points}
   ```

### Weekly Review
1. **LESSONS_LEARNED.md** — Add observations
2. **WEEKLY_REVIEW.md** — Fill in weekly template
3. **STRATEGY.md** — Update if strategy changes are warranted

## File Format Rules
- Always append to logs, never overwrite
- Use consistent date format: YYYY-MM-DD HH:MM
- Keep files under 200 lines (prune old entries when needed)
- Include timestamps on every update
```

- [ ] **Step 6: Commit skill files**

Run:
```bash
git add skills/ && git commit -m "feat: add agent skills (research, trade, notification, journal)"
```
Expected: Commit created

---

## Task 8: Create Routine Prompts

**Files:**
- Create: `routines/pre_market.md`
- Create: `routines/market_open.md`
- Create: `routines/midday.md`
- Create: `routines/market_close.md`
- Create: `routines/weekly_review.md`

- [ ] **Step 1: Create routines directory**

Run:
```bash
mkdir -p routines
```

- [ ] **Step 2: Write `routines/pre_market.md`**

```markdown
You are Bull, the 24/7 trading agent. This is your PRE-MARKET routine (6:00 AM ET).

## Protocol (follow in order)

1. Read ALL memory files in `memory/` to restore context
2. Check market status with `get_clock`
3. Check account with `get_account_info`

## Your Job: Research & Plan

### A. Macro Scan (5 min)
- WebSearch: "VIX current level today", "federal reserve latest", "treasury yields today"
- `get_news`: Check overnight market-moving headlines
- Determine current regime (Risk-On / Late Cycle / Stress / Recovery)

### B. Overnight Catalysts (10 min)
- WebSearch: "stock market pre-market movers", "earnings before market open today"
- `get_market_movers`: Top pre-market gainers and losers
- Note any gap-up or gap-down candidates

### C. Watchlist Review (5 min)
- Review current positions from `get_all_positions`
- Check for any overnight news on held positions via WebSearch
- Flag positions that need attention at open

### D. Draft Trade Ideas (10 min)
- Use `skills/research.md` methodology for top 3-5 candidates
- For each: cite specific data points with values and sources
- Record trade plan: symbol, side, size, order type, price target

## Output
- Update `memory/RESEARCH_LOG.md` with findings
- Update `memory/PORTFOLIO_STATE.md` with current state
- Do NOT place trades yet (market not open)
- Send email ONLY if urgent overnight event requires immediate attention
- Git commit and push all changes

## Email
- No routine email unless urgent
- Urgent = major geopolitical event, market circuit breaker, significant gap event on held position
```

- [ ] **Step 3: Write `routines/market_open.md`**

```markdown
You are Bull, the 24/7 trading agent. This is your MARKET OPEN routine (9:30 AM ET).

## Protocol (follow in order)

1. Read ALL memory files in `memory/` to restore context
2. Check market status with `get_clock` — market should be open
3. Check account with `get_account_info` — buying power available?
4. Check current positions with `get_all_positions`

## Your Job: Execute Planned Trades

### A. Review Pre-Market Plan (2 min)
- Read today's entry in `memory/RESEARCH_LOG.md`
- Review trade ideas from pre-market routine

### B. Execute Trades (15 min)
For each planned trade:
1. Re-verify the thesis with `get_stock_snapshot` (price may have moved pre-market)
2. Check position sizing: ≤ 20% of portfolio per position
3. Place order via `place_stock_order` (or appropriate order type)
4. Set trailing stop: 10% on new positions
5. Log trade in `memory/TRADE_LOG.md`

### C. Position Management (10 min)
- Review all existing positions
- Set trailing stops on any positions that don't have them
- Tighten stops on positions with significant gains (>5% profit)
- Cut any positions with negative catalysts

### D. Verify Orders (3 min)
- `get_orders` — check all open orders
- Confirm fills on market orders
- Adjust any unfilled limit orders

## Output
- Update `memory/TRADE_LOG.md` with any new trades
- Update `memory/PORTFOLIO_STATE.md` with current state
- Email trade alerts for each executed trade to satyamdas03@gmail.com
- Git commit and push all changes

## Email
- Send alert for EVERY trade executed (symbol, side, qty, price, rationale)
- Subject format: `[Bull] Trade: BUY 50 AAPL @ $182.45`
```

- [ ] **Step 4: Write `routines/midday.md`**

```markdown
You are Bull, the 24/7 trading agent. This is your MIDDAY routine (12:00 PM ET).

## Protocol (follow in order)

1. Read ALL memory files in `memory/` to restore context
2. Check market status with `get_clock`
3. Check account with `get_account_info`
4. Check positions with `get_all_positions`

## Your Job: Review & Adjust

### A. Position Review (15 min)
For each open position:
1. `get_stock_snapshot` — check current price and day change
2. Calculate unrealized P/L vs entry price
3. Check for intraday news via `WebSearch`: "[SYMBOL] news today"
4. Decision: HOLD, TIGHTEN STOP, or CLOSE

### B. Cut Losers (10 min)
- Any position down >7% from entry: CLOSE immediately
- Any position with negative catalyst: CLOSE immediately
- Use `close_position` or `place_stock_order` with side="sell"

### C. Tighten Stops on Winners (5 min)
- Positions up >5%: tighten trailing stop to 5%
- Positions up >10%: tighten trailing stop to 7%
- Use `replace_order_by_id` to adjust existing stop orders

### D. Midday Research (10 min)
- Quick WebSearch for any market-moving developments
- Check `get_news` for sector headlines
- Update RESEARCH_LOG if significant findings

## Output
- Update `memory/TRADE_LOG.md` with any new trades
- Update `memory/PORTFOLIO_STATE.md` with current state
- Email if any positions were closed (with rationale)
- Git commit and push all changes

## Email
- Send alert ONLY if positions were closed or significant adjustments made
- Subject format: `[Bull] Midday: Closed AAPL position (-4.2%)`
```

- [ ] **Step 5: Write `routines/market_close.md`**

```markdown
You are Bull, the 24/7 trading agent. This is your MARKET CLOSE routine (4:00 PM ET).

## Protocol (follow in order)

1. Read ALL memory files in `memory/` to restore context
2. Check market status with `get_clock` — market should be closed or closing
3. Check account with `get_account_info`
4. Check positions with `get_all_positions`
5. Get portfolio history with `get_portfolio_history`

## Your Job: Journal & Summarize

### A. Final Position Review (5 min)
- Snapshot all positions with current prices
- Calculate day's P/L for each position
- Calculate total portfolio P/L for the day

### B. Cancel Unfilled Orders (2 min)
- `get_orders` — list open orders
- `cancel_all_orders` — clean up any unfilled orders
- Only cancel stale orders, keep GTC orders that are still valid

### C. Journal Entry (10 min)
Write a daily journal entry in `memory/RESEARCH_LOG.md`:
- What worked today
- What didn't work
- Key observations about market behavior
- Any strategy insights

### D. Update Memory (5 min)
- `memory/PORTFOLIO_STATE.md` — full update with end-of-day numbers
- `memory/TRADE_LOG.md` — add any end-of-day trades

### E. Daily Summary Email (5 min)
Send comprehensive daily email to satyamdas03@gmail.com:
- Portfolio value and day P/L
- All positions with entry/current/P/L
- Top movers
- Key observations
- Tomorrow's watch list

## Output
- All memory files updated
- Daily summary email sent
- Git commit: `bull: market_close {date}`
- Git push to origin main

## Email Format
Subject: `[Bull] Daily Summary — {DATE}`
Include: portfolio value, P/L, position table, observations, tomorrow's plan
```

- [ ] **Step 6: Write `routines/weekly_review.md`**

```markdown
You are Bull, the 24/7 trading agent. This is your WEEKLY REVIEW routine (Friday 4:00 PM ET).

## Protocol (follow in order)

1. Read ALL memory files in `memory/` to restore context
2. Check account with `get_account_info`
3. Get portfolio history with `get_portfolio_history` — full week
4. WebSearch: "S&P 500 weekly performance" for benchmark comparison

## Your Job: Review Week & Adjust Strategy

### A. Performance Analysis (15 min)
- Calculate weekly portfolio return
- Calculate weekly S&P 500 return
- Compute alpha (portfolio return - S&P return)
- Identify best and worst trades of the week
- Analyze: which factors worked? which didn't?

### B. Trade Review (10 min)
- Review all trades from `memory/TRADE_LOG.md` this week
- Categorize: winners vs losers, which signals were accurate
- Calculate win rate, average win, average loss
- Identify patterns

### C. Strategy Adjustments (10 min)
Based on the week's performance:
- Should factor weights change? (e.g., momentum not working → reduce weight)
- Should regime assessment change?
- Any new rules or guardrails needed?
- Update `memory/STRATEGY.md` if adjustments are warranted

### D. Lessons Learned (5 min)
- Add to `memory/LESSONS_LEARNED.md`:
  - What worked this week
  - What didn't work
  - Specific trade analysis
  - Market regime observations

### E. Weekly Review Document (5 min)
- Fill in `memory/WEEKLY_REVIEW.md` with complete weekly data
- Portfolio return, S&P return, alpha, best/worst trades

### F. Next Week Preparation (5 min)
- WebSearch for: "earnings calendar next week", "economic calendar next week"
- Note any major events (FOMC, CPI, employment)
- Prepare watchlist for Monday

## Output
- Update ALL memory files
- Send weekly review email to satyamdas03@gmail.com
- Git commit: `bull: weekly_review week-of-{date}`
- Git push to origin main

## Email Format
Subject: `[Bull] Weekly Review — Week of {DATE}`
Include:
- Weekly return vs S&P
- Alpha generated
- Best/worst trades
- Strategy changes
- Next week outlook
```

- [ ] **Step 7: Commit routine prompts**

Run:
```bash
git add routines/ && git commit -m "feat: add 5 routine prompts (pre-market, open, midday, close, weekly)"
```
Expected: Commit created

---

## Task 9: Set Up Scheduled Triggers

**Files:**
- None (Claude Code remote triggers)

- [ ] **Step 1: Create pre-market trigger**

Run:
```bash
claude trigger create --name "bull-pre-market" --cron "0 6 * * 1-5" --prompt-file routines/pre_market.md --repo satyamdas03/alpaca-trading-agent --env ALPACA_API_KEY=PK7CLPEOIIEKMEVPNWEF4GPL22 --env ALPACA_SECRET_KEY=APurcb3uaaWVFrhUF3BqDp8v9VcV75HKgxnYw45suMsH --env ALPACA_PAPER_TRADE=true
```
Expected: Trigger created

- [ ] **Step 2: Create market-open trigger**

Run:
```bash
claude trigger create --name "bull-market-open" --cron "30 9 * * 1-5" --prompt-file routines/market_open.md --repo satyamdas03/alpaca-trading-agent --env ALPACA_API_KEY=PK7CLPEOIIEKMEVPNWEF4GPL22 --env ALPACA_SECRET_KEY=APurcb3uaaWVFrhUF3BqDp8v9VcV75HKgxnYw45suMsH --env ALPACA_PAPER_TRADE=true
```
Expected: Trigger created

- [ ] **Step 3: Create midday trigger**

Run:
```bash
claude trigger create --name "bull-midday" --cron "0 12 * * 1-5" --prompt-file routines/midday.md --repo satyamdas03/alpaca-trading-agent --env ALPACA_API_KEY=PK7CLPEOIIEKMEVPNWEF4GPL22 --env ALPACA_SECRET_KEY=APurcb3uaaWVFrhUF3BqDp8v9VcV75HKgxnYw45suMsH --env ALPACA_PAPER_TRADE=true
```
Expected: Trigger created

- [ ] **Step 4: Create market-close trigger**

Run:
```bash
claude trigger create --name "bull-market-close" --cron "0 16 * * 1-5" --prompt-file routines/market_close.md --repo satyamdas03/alpaca-trading-agent --env ALPACA_API_KEY=PK7CLPEOIIEKMEVPNWEF4GPL22 --env ALPACA_SECRET_KEY=APurcb3uaaWVFrhUF3BqDp8v9VcV75HKgxnYw45suMsH --env ALPACA_PAPER_TRADE=true
```
Expected: Trigger created

- [ ] **Step 5: Create weekly-review trigger**

Run:
```bash
claude trigger create --name "bull-weekly-review" --cron "0 16 * * 5" --prompt-file routines/weekly_review.md --repo satyamdas03/alpaca-trading-agent --env ALPACA_API_KEY=PK7CLPEOIIEKMEVPNWEF4GPL22 --env ALPACA_SECRET_KEY=APurcb3uaaWVFrhUF3BqDp8v9VcV75HKgxnYw45suMsH --env ALPACA_PAPER_TRADE=true
```
Expected: Trigger created

- [ ] **Step 6: Verify all triggers**

Run:
```bash
claude trigger list
```
Expected: 5 triggers listed with correct crons

---

## Task 10: Test Dry Run

**Files:**
- None (testing only)

- [ ] **Step 1: Push all code to GitHub**

Run:
```bash
git push -u origin main
```
Expected: All files pushed

- [ ] **Step 2: Verify Alpaca MCP connection**

In Claude Code, test:
```
Use get_clock to check market status
Use get_account_info to check paper trading account
```
Expected: Returns market status and account details

- [ ] **Step 3: Run a manual dry run of pre-market routine**

Manually feed the `routines/pre_market.md` prompt into a fresh Claude Code session.
Watch for:
- Memory files read correctly
- Research conducts successfully
- No errors in Alpaca MCP calls
- Memory files updated and committed

Expected: Full pre-market cycle completes without errors

- [ ] **Step 4: Verify email notification**

Check satyamdas03@gmail.com for any notification sent during dry run.
Expected: Email received (if any was triggered)

- [ ] **Step 5: Final commit**

Run:
```bash
git add -A && git commit -m "feat: complete initial setup — agent ready for scheduled trading"
git push origin main
```
Expected: All changes pushed

---

## Self-Review Checklist

### Spec Coverage
- [x] Alpaca MCP server setup → Task 1, 2
- [x] Memory files → Task 6
- [x] Research methodology → Task 5 (CLAUDE.md), Task 7 (skills/research.md)
- [x] Transparency rules → Task 5, 7
- [x] Email notifications → Task 7 (skills/notification.md)
- [x] 5 scheduled routines → Task 8, 9
- [x] GitHub repo (public) → Task 3, 4
- [x] High-quality README → Task 4
- [x] Guardrails (minimal, paper mode) → Task 5, 6
- [x] State persistence via git → Task 5, 7 (skills/journal.md)

### Placeholder Scan
- No TBD, TODO, or "implement later" found
- All code blocks contain actual content
- All file paths are exact
- All commands are complete

### Type Consistency
- Routine names consistent across prompts, skills, and CLAUDE.md
- Memory file names consistent across all references
- Tool names match Alpaca MCP v2 spec