# Bull Agent — Full Session Context

**Purpose:** Restore complete context when new session starts. Read this FIRST.
**Last Updated:** 2026-04-22 Evening (Day 0 — first trading day complete)
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
- **TSLA after-hours:** $402.91 (+4.3% from $387.26 close) — earnings beat?
- VIX dropped to ~21 range (from 25+), ceasefire cooling

---

## Current Portfolio (End of 4/22)

| Symbol | Qty | Entry | Current (4/22 close) | Unrealized P&L | P&L % |
|--------|-----|-------|----------------------|----------------|-------|
| XLV | 47.707 | $146.73 | $146.34 | -$9.71 | -0.14% |
| XLE | 124.076 | $56.42 | $56.53 | +$23.92 | +0.34% |
| GLD | 13.772 | $435.66 | $434.00 | -$22.92 | -0.38% |
| **Total** | | | | **-$8.69** | **-0.04%** |

- Cash: $80,000
- Portfolio: $99,991.31
- Positions: 3 open
- Stop-loss: -7% from entry (not yet set as orders)
- Trailing stop: 10% on winners (not yet set)

---

## Key Market Context (4/22 Close)

### Macro
- SPY: $711.20 (+1.03%)
- VIX: ~21 (down from 25+, ceasefire cooling)
- Oil: Brent ~$98-99, WTI ~$93
- S&P 500: 7,064 → 7,134 (relief rally on ceasefire)

### Iran/Hormuz — ACTIVE ESCALATION
- Ceasefire extended indefinitely but SYMBOLIC
- IRGC attacked 3 ships, seized 2 (MSC Francesca, Epaminodes) on 4/22
- Peace talks collapsed — neither side attended Islamabad
- U.S. naval blockade continues, Iran won't negotiate until lifted
- UK/France convening 30+ nations to plan force-based Hormuz reopening
- **Key risk:** If force reopening attempted and fails → oil spikes, VIX spikes → Stress regime returns
- **Key risk:** If Hormuz suddenly reopens → oil crashes → exit XLE immediately

### TSLA After-Hours
- TSLA: $402.91 (+4.3% from $387.26 close)
- Earnings appear to have beat expectations (stock rallying in after-hours)
- Conference call at 5:30 PM ET 4/22
- Post-earnings plan: if confirmed beat → consider small momentum long ($3-5K)

---

## Regime Assessment
**LATE CYCLE, leaning Stress.** VIX ~21 (below 25 Stress threshold) but Hormuz escalation ongoing. IRGC ship seizures = real escalation not reflected in VIX. Oil elevated. Strategy: stay defensive, keep 80% cash.

---

## What To Do Next (Priority Order)

### 4/23 Pre-Market (9:30 AM ET)
1. **Read all memory files** — restore context
2. **Check TSLA earnings results** — confirm beat/miss, execute post-earnings plan
3. **Set stop-loss orders** for XLV, XLE, GLD (-7% from entry):
   - XLV stop: $136.46 (146.73 × 0.93)
   - XLE stop: $52.47 (56.42 × 0.93)
   - GLD stop: $405.17 (435.66 × 0.93)
4. **Set trailing stops** on XLE winner (10% trail)
5. **Check Iran/Hormuz** — any overnight escalation or de-escalation
6. **Consider TSLA momentum trade** if earnings beat confirmed ($3-5K max)

### Ongoing
- Midday: review positions, adjust stops
- Close: calculate P&L, send email summary
- Weekly review: compare vs S&P, adjust strategy

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