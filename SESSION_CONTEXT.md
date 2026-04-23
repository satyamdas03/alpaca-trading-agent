# Bull Agent — Full Session Context

**Purpose:** Restore complete context when new session starts. Read this FIRST.
**Last Updated:** 2026-04-23 Pre-Market (Day 1)
**Git Branch:** main
**Repo:** https://github.com/satyamdas03/alpaca-trading-agent.git

---

## What Is This Project

Bull is a 24/7 autonomous AI trading agent running on Claude Code. It wakes up on schedule, reads memory files, researches markets, executes trades via Alpaca paper trading, and emails daily summaries. Goal: beat S&P 500 with fundamentals-driven swing trading.

**This is 100% paper trading. No real money. Account prefix PA = paper.**

---

## Timeline — Everything That's Happened

### 2026-04-21: Initialization
- Bull agent created, CLAUDE.md written, strategy framework established
- Alpaca MCP tools verified working (get_clock, get_account_info, get_stock_snapshot, place_stock_order)
- Backtesting engine completed (46/46 tests passing, 10-year walk-forward infrastructure)
- First research sessions: identified Stress regime (VIX >25, Hormuz closed, oil $99)
- Zero trades placed — backtesting still being validated

### 2026-04-22 Pre-Market (Late Night / 1:53 AM ET)
- Regime: **STRESS** — VIX >25, Iran ceasefire extended but Hormuz still closed, oil $99
- Placed 3 market orders for 4/22 open:
  1. XLV BUY $7,000 (healthcare ETF — defensive sector in Stress)
  2. XLE BUY $7,000 (energy ETF — oil beneficiary, Hormuz closed)
  3. GLD BUY $6,000 (gold ETF — safe haven in geopolitical Stress)
- Total deployment: $20K (20%), $80K cash reserve
- Explicitly avoided TSLA (binary earnings risk tonight)

### 2026-04-22 Morning Session
- User laptop session, picked up from memory files
- Verified all MCP tools working, paper trading confirmed
- Set up 7 cron jobs for 4/22 and 4/23 routines

### 2026-04-22 Market Open (9:30 AM ET)
- **ALL 3 ORDERS FILLED:**
  - XLV: 47.707 shares @ $146.73 (filled 9:31 AM ET)
  - XLE: 124.076 shares @ $56.42 (filled 9:31 AM ET)
  - GLD: 13.772 shares @ $435.66 (filled 9:33 AM ET)
- Total deployed: $20,000

### 2026-04-22 Close / After-Hours
- **Portfolio value:** $99,991.31 (slight unrealized loss -$8.69)
- **Day P&L:** -$8.69 (-0.009%) — first trading day, barely moved
- **SPY:** $711.20 (+1.03% from $703.91) — S&P beat us today
- **TSLA after-hours:** $402.91 (+4.3% initially) → gave back gains on spending guidance

### 2026-04-22 After Close: TSLA Earnings Results
- **EPS: $0.41** (beat $0.37 est) ✅
- **Revenue: $22.39B** (miss vs $22.7B) ❌
- **Capex guidance: +$5B above prior → >$25B in 2026**
- **After-hours:** Initially +4.3%, then gave back gains
- **Decision: NO TSLA TRADE** — mixed signal, spending shock, not clean directional

### 2026-04-23 Pre-Market Routine
- **Stop-losses SET** for all 3 positions (GTC, -7% from entry):
  - XLV: SELL STOP $136.46 (ID: 71b7b3bf)
  - XLE: SELL STOP $52.47 (ID: 63cbc6a9)
  - GLD: SELL STOP $405.17 (ID: f91b4932)
- **Trailing stop on XLE blocked** — shares held by stop-loss order
- **No new trades** — regime uncertain (VIX says Late Cycle, Hormuz says Stress)
- **IRGC seized 2 ships in Hormuz** — escalation continues, oil $99-100
- **Portfolio:** $99,988.97 (-$11.07 unrealized, -0.06%)
- VIX dropped to ~21 range (from 25+), ceasefire cooling

---

## Current Portfolio (4/23 Pre-Market)

| Symbol | Qty | Entry | Current | Unrealized P&L | P&L % | Stop-Loss |
|--------|-----|-------|---------|----------------|-------|-----------|
| XLV | 47.707 | $146.73 | $146.52 | -$9.71 | -0.14% | $136.46 (GTC) |
| XLE | 124.076 | $56.42 | $56.60 | +$22.67 | +0.32% | $52.47 (GTC) |
| GLD | 13.772 | $435.66 | $433.92 | -$24.03 | -0.40% | $405.17 (GTC) |
| **Total** | | | | **-$11.07** | **-0.06%** | |

- Cash: $80,000
- Portfolio: $99,988.97
- Positions: 3 open
- Stop-losses: SET (GTC, -7% from entry)
- Trailing stop: XLE blocked by stop-loss order

---

## Key Market Context (4/23 Pre-Market)

### Macro
- SPY: $711.20 (4/22 close), extended hours ~$710.42
- VIX: ~21 (cooling from 25+, ceasefire holding)
- Oil: Brent ~$99-100, WTI ~$90-93 (Hormuz still closed)
- S&P futures: mildly positive

### Iran/Hormuz — ACTIVE ESCALATION, DIPLOMATIC STALEMATE
- Ceasefire extended indefinitely but SYMBOLIC — no airstrikes, no missiles
- IRGC attacked 3 ships, seized 2 (Epaminondas, MSC Francesca) on 4/22
- Peace talks collapsed — neither side attended Islamabad
- Iran won't talk until blockade lifted, U.S. won't lift until Iran negotiates
- UK/France convening 30+ nations to plan force-based Hormuz reopening
- EU: €500M/day disruption cost, possible fuel shortages
- Recovery timeline: 6-8 weeks after peace deal just to reposition tankers
- **Key risk:** If force reopening attempted → binary: success = oil crash, failure = VIX spike
- **Key risk:** If Hormuz suddenly reopens → exit XLE immediately

### TSLA Earnings Result
- EPS $0.41 beat $0.37 ✅, Revenue $22.39B missed $22.7B ❌
- Capex guidance +$5B above prior (> $25B in 2026)
- After-hours: +4.3% then gave back gains on spending shock
- **NO TSLA TRADE** — mixed signal, not clean directional

---

## Regime Assessment
**LATE CYCLE, leaning Stress.** VIX ~21 (below 25 Stress threshold) but Hormuz escalation ongoing. IRGC ship seizures = real escalation not reflected in VIX. Oil elevated. Strategy: stay defensive, keep 80% cash.

---

## What To Do Next (Priority Order)

### 4/23 Pre-Market — DONE
1. ✅ Read all memory files
2. ✅ Check TSLA earnings — mixed, no trade
3. ✅ Set stop-losses for XLV/XLE/GLD (-7%, GTC)
4. ❌ Trailing stop on XLE — blocked by stop-loss order (upgrade later if XLE appreciates)
5. ✅ Check Iran/Hormuz — escalation continues, ship seizures
6. ✅ No new trades — regime uncertain

### 4/23 Next Steps
- **Midday:** Check positions, monitor for stop triggers, check Iran news
- **Close:** Calculate daily P&L, send email summary
- **Key triggers to watch:**
  1. Hormuz force-reopening announcement → exit XLE immediately
  2. VIX breaks below 20 consistently → consider risk-on trades
  3. VIX spikes above 30 → add more defensive/hedges
  4. XLE appreciates +5% → cancel stop, set 10% trailing stop

### Later This Week
- Earnings: Boeing, P&G, other major reports
- Iran/Hormuz: watch for UK/France coalition progress
- Weekly review: compare vs S&P, assess if regime shifting

---

## Infrastructure Status

### Alpaca MCP — ALL WORKING
- get_clock, get_account_info, get_all_positions, get_orders
- get_stock_snapshot, get_stock_bars, place_stock_order
- get_asset, get_market_movers, get_most_active_stocks
- Account: PA3M6G5LMKMI (paper trading), API keys in env vars

### Gmail MCP — Available
- Send to: satyamdas03@gmail.com
- Use for: trade notifications, daily P&L, weekly reviews

### Backtesting Engine — COMPLETE
- 46/46 tests passing
- 10-year walk-forward infrastructure
- Ready for live validation

### Cron Jobs — SESSION ONLY
- Die when Claude session ends
- Need external scheduler for persistence
- 7 jobs were set for 4/22-4/23

---

## Strategy Quick Reference

| Regime | Signal | Factor Shift |
|--------|--------|--------------|
| Risk-On | VIX < 20 | Momentum ↑, Value ↓ |
| Late Cycle | VIX 20-25 | Value ↑, Momentum ↓ |
| Stress | VIX > 25 | Low Vol ↑, Momentum ↓ |
| Recovery | VIX declining from peak | Quality ↑, Momentum ↑ |

**Current regime: Late Cycle / Stress borderline (VIX ~21, Hormuz escalation)**

**Exit rules:** Stop-loss -7%, trailing stop 10%, time stop 30 days.

---

## Memory File Map

| File | Purpose |
|------|---------|
| `memory/STRATEGY.md` | Factor weights, regime rules, sizing |
| `memory/PORTFOLIO_STATE.md` | Current positions, P&L, account state |
| `memory/TRADE_LOG.md` | All trades executed |
| `memory/RESEARCH_LOG.md` | Research sessions, macro analysis |
| `memory/LESSONS_LEARNED.md` | Rules and observations |
| `memory/WEEKLY_REVIEW.md` | Weekly performance review |
| `SESSION_CONTEXT.md` | THIS FILE — full end-to-end context for session restore |

---

## Git Protocol
After every routine:
1. `git add memory/`
2. `git commit -m "bull: {routine_name} {date}"`
3. `git push origin main`