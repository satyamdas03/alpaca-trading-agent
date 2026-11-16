# Portfolio State

**Last Updated:** 2026-11-16 Pre-Market Routine

## Account Overview
- Account Type: Paper Trading
- Account Number: PA3M6G5LMKMI
- Starting Balance: $100,000.00
- Current Cash: $80,000.00
- Total Portfolio Value: $99,988.99
- Buying Power: $179,988.99 (2x margin)
- Equity: $99,988.99
- Pattern Day Trader: No
- Alpaca API Key: PK7CLPEOIIEKMEVPNWEF4GPL22
- Alpaca Paper: true

## Open Positions
| Symbol | Side | Qty | Entry Price | Current Price | Unrealized P&L | P&L % | Cost Basis | Market Value |
|--------|------|-----|-------------|---------------|----------------|-------|------------|--------------|
| XLV | LONG | 47.707 | $146.73 | $146.38 | -$16.59 | -0.24% | $7,000.00 | $6,983.41 |
| XLE | LONG | 124.076 | $56.42 | $56.72 | +$37.56 | +0.54% | $7,000.03 | $7,037.59 |
| GLD | LONG | 13.772 | $435.66 | $433.43 | -$30.77 | -0.51% | $6,000.00 | $5,969.23 |

**Total position value: $19,990.23. Cash: $80,000.**
**Net unrealized P&L: -$9.80 (-0.01%)**

### Stop-Loss Orders (SET — GTC, expire 7/22)
| Symbol | Side | Qty | Type | Stop Price | Order ID | Distance |
|--------|------|-----|------|-----------|----------|----------|
| XLV | SELL | 47 | STOP | $136.46 | 71b7b3bf | -7.00% |
| XLE | SELL | 124 | STOP | $52.47 | 63cbc6a9 | -7.00% |
| GLD | SELL | 13 | STOP | $405.17 | f91b4932 | -6.97% |

### Trailing Stops
- None currently. Stop-losses block trailing stops on same shares.
- Strategy: Cancel stop-loss, place trailing stop when position appreciates enough.

## Allocation
- Cash: 80.0%
- Equities: 20.0%
- Options: 0%
- Crypto: 0%
- **Target in Risk-On: 40-50% equities (currently underdeployed)**

## Performance Tracking

### Daily Returns
| Date | Equity | Day P&L | Day P&L % | Cum P&L | S&P Day | S&P Cum | Alpha |
|------|--------|---------|-----------|----------|---------|---------|-------|
| 4/22 | $100,000* | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% | +0.62% |
| 4/23 | $99,988.99 | -$4.11 est | -0.004% | -$11.01 | +1.05% | +0.42% | -0.43% |

*Portfolio history API shows $100,000 for 4/15-4/21 (no positions), then $99,993.10 on 4/22 close.

### Position P&L Detail
| Symbol | Entry | Last Close | Entry→Close | Day Chg | Stop | Distance to Stop |
|--------|-------|------------|-------------|---------|------|-------------------|
| XLV | $146.73 | $146.38 | -$16.59 | 0.00% | $136.46 | -6.78% |
| XLE | $56.42 | $56.72 | +$37.56 | +0.32% | $52.47 | -7.50% |
| GLD | $435.66 | $433.43 | -$30.77 | -0.42% | $405.17 | -6.52% |

All positions well above stops. No exits triggered.

### Benchmark Comparison
- S&P 500 YTD: +4.27%
- Portfolio YTD: -0.011% (since first trade 4/22)
- **Alpha: -4.28%** (significantly underperforming)
- Primary cause: defensive positioning in Risk-On market + 80% cash drag

## Market Context (2026-11-16 Pre-Market)

**⚠️ NOTE: Last Alpaca account verification was 2026-04-23. MCP still DISCONNECTED. Prices below are web search estimates.**
**Stop-loss orders (GTC expire 7/22) have EXPIRED. Need to re-enter stops via REST API.**

- S&P 500: ~7,592 (Nov 12 close), SPY premarket Nov 16: ~$749.85 (-0.60%)
- Nasdaq/QQQ: Premarket -1.23% (Nov 16)
- VIX: **20.08** (Late Cycle boundary — AT the 20 threshold)
- 10Y yield: ~4.3-4.5% (est., rising with Dec hike expectations)
- Regime: **LATE CYCLE** — VIX at 20, 4 consecutive down weeks, Fed hiking in December
- SPY YTD: +10.61% (from Jan 2026 base), down 5.65% from Oct 6 record high

### Oil/Hormuz (Updated)
- WTI: ~$90.34 (Nov 8, down from ~$97 at our April entry)
- Brent: ~$97.75 (Nov 8, down from ~$105 at entry)
- Hormuz: ~30.3 vessels/day avg (vs 1/day in April) — SIGNIFICANT IMPROVEMENT
- Status: Partially open, US claims control, Iran warns of "forceful response"
- 131 maritime incidents confirmed since conflict start

### Upcoming Catalyst (THIS WEEK)
- **NVIDIA Q3 FY2027 earnings: Nov 17 after close (4:20 PM ET)**
  - Options-implied move: ±10.6%
  - CEO Jensen Huang under investigation
  - Hedge funds cutting AI risk fastest pace in a decade
- Disney Q4/FY2026: Nov 17 before open
- Palo Alto Networks: Nov 18
- Intuit: Nov 19

### Estimated Position Status (Unconfirmed — Need Alpaca REST Verification)
| Symbol | Entry | Old Stop (EXPIRED 7/22) | Est. Current Price | Est. P&L |
|--------|-------|------------------------|-------------------|----------|
| XLV | $146.73 | $136.46 (EXPIRED) | ~$186 | ~+$1,870 (+27%) |
| XLE | $56.42 | $52.47 (EXPIRED) | ~$54-56 (uncertain) | ~flat to -5% |
| GLD | $435.66 | $405.17 (EXPIRED) | ~$450-480 est. | ~+$700-$600 |

**CRITICAL: Stop-loss orders expired July 22. Positions may be unprotected. Need to:**
1. Verify positions via Alpaca REST API
2. Re-enter stop-loss orders immediately
3. Raise XLV stop to protect +27% gain

## Key Assessment — November 16, 2026
**Portfolio materially changed over 7 months.**
- XLV: Likely big winner (+27%) — healthcare resilient in Late Cycle correction
- XLE: Oil thesis partially resolved — Hormuz improving, oil $7/barrel lower than entry
- GLD: Likely a winner — gold benefits from inflation/rate uncertainty
- 80% cash: Both opportunity cost AND protection — now appropriate for Late Cycle
- Major near-term risk: NVIDIA earnings tomorrow (±10.6% implied move)

**Action: Hold all positions. Re-enter stops. Wait for NVIDIA earnings before any new deployment.**

## Infrastructure Status

### MCP Connectors
| Server | Status | Last Verified |
|--------|--------|---------------|
| Alpaca | DISCONNECTED (MCP) / WORKING (REST) | 2026-04-23 |
| Gmail | CONNECTED | 2026-04-23 |
| Google Calendar | CONNECTED | 2026-04-23 |

### API Keys
- Alpaca API Key: PK7CLPEOIIEKMEVPNWEF4GPL22
- Alpaca Secret: stored in docs/superpowers/plans (REST fallback working)
- Alpaca Paper: true

### CRON Jobs (Session-Only, Expire 7 Days)
| Routine | Schedule | Job ID | Next Fire |
|---------|----------|--------|-----------|
| Pre-Market | Weekdays 8:55 AM ET | 93231087 | 4/24 8:55 AM |
| Midday | Weekdays 12:00 PM ET | b3f3cc68 | 4/24 12:00 PM |
| Market Close | Weekdays 3:50 PM ET | 5a80a0f4 | 4/24 3:50 PM |
| Weekly Review | Fridays 5:00 PM ET | edd3dac0 | 4/25 5:00 PM |

**WARNING:** These CRONs are session-only. They die when Claude session ends and auto-expire after 7 days. For persistent scheduling, implement Windows Task Scheduler or cloud-based trigger.

### Backtesting Engine
- Phase 1: COMPLETE (46/46 tests passing)
- Modules: data/cache, data/alpaca_fetcher, signals/quality, signals/momentum, signals/regime, strategy/bull_strategy, sizing/half-Kelly, backtest/walk-forward
- Status: Ready for live validation

### Self-Learning Roadmap
- Saved in memory/SELF_LEARNING_ROADMAP.md
- 5 phases: Feedback Loop → Strategy Evolution → ML Enhancement → Multi-Agent → Continuous Improvement
- MVP: SQLite trade database with automated post-mortem