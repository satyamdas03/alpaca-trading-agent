# Portfolio State

**Last Updated:** 2026-11-20 Pre-Market Routine
**WARNING: 7-month gap in updates. Alpaca MCP unavailable — using ESTIMATES from web data. Actual account state UNVERIFIED.**

## Account Overview (ESTIMATED — based on April 23 last confirmed + market data)
- Account Type: Paper Trading
- Account Number: PA3M6G5LMKMI
- Starting Balance: $100,000.00
- Current Cash: ~$80,000.00 (unchanged from April 23 — no new trades)
- **Estimated Portfolio Value: ~$103,500** (+3.5% from start)
- Buying Power: ~$183,000 est. (2x margin)
- Alpaca API Key: PK7CLPEOIIEKMEVPNWEF4GPL22
- Alpaca Paper: true

## Open Positions (ESTIMATED — NOT VERIFIED with Alpaca)
| Symbol | Side | Qty | Entry Price | Est. Current | Est. Unrealized P&L | Est. P&L % | Stop (OUTDATED) |
|--------|------|-----|-------------|-------------|---------------------|------------|-----------------|
| XLV | LONG | 47.707 | $146.73 | ~$178 | ~+$1,490 | ~+21% | $136.46 ← MUST UPDATE |
| XLE | LONG | 124.076 | $56.42 | ~$68 | ~+$1,450 | ~+20.5% | $52.47 ← MUST UPDATE |
| GLD | LONG | 13.772 | $435.66 | ~$473 | ~+$524 | ~+8.5% | $405.17 ← MUST UPDATE |

**Est. position value: ~$23,500. Cash: ~$80,000. Est. total: ~$103,500**
**Est. unrealized P&L: ~+$3,464 (+3.5% from $100K start)**

### Stop-Loss Orders (CRITICAL: ALL OUTDATED — Based on April entry prices)
| Symbol | Current Stop | Distance to Entry | Action Required |
|--------|-------------|-------------------|-----------------|
| XLV | $136.46 (Order 71b7b3bf) | -7% from $146.73 | CANCEL & reset to ~$165 |
| XLE | $52.47 (Order 63cbc6a9) | -7% from $56.42 | CANCEL & reset to ~$63 |
| GLD | $405.17 (Order f91b4932) | -7% from $435.66 | CANCEL & reset to ~$440 |

**ACTION: Stops based on ENTRY prices, not current prices. With 20%+ gains, these stops protect entry but surrender all profits. Update to trailing stops based on current estimated prices.**

### Manual Order Instructions (Alpaca MCP unavailable — execute via REST API or UI)
```
# XLV — Cancel old stop, set new trailing stop
DELETE order 71b7b3bf
POST order: SELL XLV, 47 shares, TRAILING_STOP, trail_percent=7.0

# XLE — Cancel old stop, set new trailing stop
DELETE order 63cbc6a9
POST order: SELL XLE, 124 shares, TRAILING_STOP, trail_percent=7.0

# GLD — Cancel old stop, set new trailing stop
DELETE order f91b4932
POST order: SELL GLD, 13 shares, TRAILING_STOP, trail_percent=7.0
```

## Allocation
- Cash: ~77.3% (est.)
- Equities: ~22.7% (est.)
- Options: 0%
- Crypto: 0%
- **Target in Late Cycle: 25-35% equities — slightly underdeployed but no momentum plays**

## Performance Tracking

### Daily Returns (incomplete — 7-month gap, only endpoints known)
| Date | Equity | Day P&L | Day P&L % | Cum P&L | S&P Day | S&P Cum | Alpha |
|------|--------|---------|-----------|---------|---------|---------|-------|
| 4/22 | $100,000 | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% | +0.62% |
| 4/23 | $99,988.99 | -$11.01 est | -0.011% | -$11.01 | +1.05% | +0.42% | -0.43% |
| 11/19 | ~$103,500 est. | unknown | ~+3.5% from start | +$3,500 est. | SPY $715.87 | SPY vs $711 start = +0.7% from 4/23 | ~+2.8% est. alpha |

### Benchmark Comparison
- S&P 500: SPY was $715.87 on 11/19 close, was ~$711 on 4/23. +0.7% over 7 months.
- Portfolio est.: +3.5% from start ($100K → ~$103.5K)
- **Estimated Alpha: ~+2.8%** (vs flat S&P over same period — primarily driven by oil/gold position)
- Note: Estimates only. S&P YTD from Jan 1 unknown. Positions may have changed.

## Market Context (2026-11-20 Pre-Market)
- S&P 500: ~7,350-7,416 (6-session losing streak, down 1.96% yesterday)
- SPY: $715.87 close 11/19; pre-market ~$710 (-0.81%)
- QQQ: pre-market ~-1.67%
- VIX: ~21-23 est. (confirmed 19.30 on 11/13; Nov 5 spike to 28.18)
- Oil: Brent est. ~$105-115 (Oct 28: $115.11), WTI est. ~$95-102
- 10Y yield: elevated (mortgage rates 7.4%)
- Regime: **LATE CYCLE (high stress risk)** — VIX 20-25 zone, Hormuz closed, Fed hiking

### Iran/Hormuz (11/20)
- Hormuz CLOSED by Iran (after July 7 ceasefire breakdown)
- US struck Qeshm Island Nov 17
- 3 ships attacked Nov 16-19
- Trump weighing Iran action
- Oil elevated — direct XLE tailwind

### Tech Sector (11/20)
- Chip stocks tumbling globally pre-market
- Anthropic -9%+
- Nvidia beat earnings (Nov 17) but stock now declining
- Jensen Huang resigned Nov 12 — Colette Kress interim CEO

## Infrastructure Status

### MCP Connectors
| Server | Status | Last Verified |
|--------|--------|---------------|
| Alpaca | DISCONNECTED (MCP) / Working (REST fallback) | 2026-04-23 (MCP), unknown current |
| Gmail | CONNECTED | 2026-11-20 |
| GitHub | CONNECTED | 2026-11-20 |

### CRON Jobs Status
**WARNING:** CRONs from April 23 were session-only and have long since expired. Need to recreate.
Previous job IDs: 93231087, b3f3cc68, 5a80a0f4, edd3dac0 — all expired.

## Previous Portfolio State (2026-04-23 Close — preserved for reference)

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

## Market Context (2026-04-23 Close)
- S&P 500: 7,137.90 (+1.05%) — record close, 8th record of 2026
- Nasdaq: 24,657.57 (+1.64%) — record close
- Dow: 49,490.03 (+0.69%)
- SPY: ~$711.21 (+1.01%)
- VIX: ~17-18 (Risk-On territory, below 20 threshold)
- 10Y yield: ~4.27%
- Regime: **RISK-ON** — VIX < 20, ceasefire holding, tech leading

### Sector Performance Today
- Info Tech: +2.31% (15 of last 16 sessions green)
- Semiconductors: 11 consecutive winning sessions (record)
- Energy (XLE): +1.20%
- Healthcare (XLV): +0.32%
- Gold (GLD): +1.32%

### Oil (Hormuz Escalation)
- WTI: ~$96.73 (+4.06%)
- Brent: ~$105.63 (+3.62%)
- Iran seized 2 ships, fired on 3 in Hormuz
- Only 1 ship/day passing through (vs 130/day normal)
- Diplomacy stalled: Iran won't talk until blockade lifted

### After-Hours Earnings
- Boeing (BA): Q1 beat significantly. Rev $22.22B vs $21.78B est, loss ($0.20) vs ($0.83) est. +5.53%
- IBM: Q1 beat but -6-7% AH on decelerating growth, AI disruption fears
- GE Vernova: +13.75% (best S&P, raised revenue forecast)
- Micron: +8.48% (AI memory demand, record close)
- United Airlines: -5.58% (jet fuel costs from Hormuz)

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