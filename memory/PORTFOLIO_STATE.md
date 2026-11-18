# Portfolio State

**Last Updated:** 2026-11-18 Pre-Market Routine

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

## Market Context (2026-11-17 Close — LATEST)
- S&P 500: 7,340.53 (-1.03%) — 4th consecutive loss, lowest since late July 2026
- Nasdaq: 24,328.38 (-0.74%) — 4th consecutive loss
- Dow: 50,759.42 (-1.64%, -848.75 pts)
- VIX: ~20-22 (estimated; was 19.92 on 11/9, now likely above 20 given selling)
- WTI: $86.01 (+0.34%)
- Brent: $93.14 (+0.76%)
- Regime: **LATE CYCLE** (tipping toward Stress)

### After-Hours Earnings (11/17)
- Nvidia (NVDA): Q3 FY27 — $115.8B rev (+103% YoY), EPS $2.70, Q4 guided $130B. MASSIVE BEAT but stock DECLINED (sell-the-news + leadership vacuum)
- Salesforce (CRM): -9% (AI disruption fears, decelerating growth)

### Iran/Hormuz Status
- Conflict Day ~263: Strait still effectively closed
- Nov 11-12: 4 oil tankers hit in Hormuz; US downed Iranian drones
- US naval blockade of Iranian ports still active (since July 14, 2026)
- Oil lower than April peak (~$97 WTI) — market normalizing some supply routes

### CRITICAL WARNING: Stop-Loss Expiry Risk
- Stop-loss orders set "GTC expire 7/22" (likely July 22, 2026) — MAY HAVE EXPIRED
- If expired, XLV/XLE/GLD positions have been UNPROTECTED since July
- **MUST VERIFY positions and re-set stops at market open**

## Key Assessment
**Portfolio lagging S&P significantly.** Defensive positioning in Risk-On = opportunity cost.
- XLV flat (+0.32%) vs tech +2.31% = wrong sector for this regime
- XLE working (+0.54%) = Hormuz/oil thesis correct
- GLD underwater (-0.51%) = entry was near peak, gold bid still present
- 80% cash drag = missing most of S&P rally

**Regime is Risk-On. Strategy says increase Momentum, reduce Low Vol.**
Consider: adding XLK/QQQ for momentum exposure, maintaining XLE (oil tailwind).

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