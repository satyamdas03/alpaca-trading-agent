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
   claude mcp add alpaca \
     -e ALPACA_API_KEY=your_key \
     -e ALPACA_SECRET_KEY=your_secret \
     -e ALPACA_PAPER_TRADE=true \
     -- uvx alpaca-mcp-server
   ```

4. **Open in Claude Code and start trading:**
   ```bash
   claude
   ```

### Setting Up Scheduled Routines

Each routine prompt lives in `routines/`. Scheduled routines can be set up two ways:

**Option A: Claude Code session (temporary, 7-day limit)**

Inside a Claude Code session, use CronCreate to schedule routines. Note: recurring jobs auto-expire after 7 days.

**Option B: Windows Task Scheduler / cron (persistent, 24/7)**

For true 24/7 operation, use your OS scheduler to run `claude` with the routine prompt at market hours:

```powershell
# Windows Task Scheduler example — runs pre-market at 6:03 AM ET weekdays
schtasks /create /tn "Bull-PreMarket" /tr "claude -p \"Read routines/pre_market.md and execute the pre-market routine\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 06:03
```

Or use Linux cron on a server for uninterrupted operation. See `routines/` for all prompt files.

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
│   ├── market_close.md      # 4:00 PM prompt
│   └── weekly_review.md     # Friday 4:00 PM prompt
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