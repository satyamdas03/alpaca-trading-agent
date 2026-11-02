# Trade Log

| Timestamp | Symbol | Side | Qty | Price | Rationale | Signal | Status |
|-----------|--------|------|-----|-------|-----------|--------|--------|
| 2026-04-22 09:31 ET | XLV | BUY | 47.707 | $146.73 | Defensive sector in Stress, UNH beat earnings | Low Vol ↑ in Stress regime | OPEN |
| 2026-04-22 09:31 ET | XLE | BUY | 124.076 | $56.42 | Oil at $99, Hormuz closed, direct beneficiary | Hormuz supply disruption | OPEN |
| 2026-04-22 09:33 ET | GLD | BUY | 13.772 | $435.66 | Safe haven in geopolitical Stress | Safe haven in Stress regime | OPEN |

---

## Orders Placed: 4/22 Pre-Market (Stress Regime) — ALL FILLED

| # | Order ID | Symbol | Side | Notional | Type | Status | Fill Price | Fill Time |
|---|----------|--------|------|----------|------|--------|------------|-----------|
| 1 | 69ed3794 | XLV | BUY | $7,000 | MARKET | FILLED | $146.73 | 9:31 AM ET |
| 2 | fa0dd584 | XLE | BUY | $7,000 | MARKET | FILLED | $56.42 | 9:31 AM ET |
| 3 | b2bb3e3b | GLD | BUY | $6,000 | MARKET | FILLED | $435.66 | 9:33 AM ET |

**Regime: STRESS → Late Cycle borderline**
**Total deployed: $20K (20%). Cash: $80K.**

---

## Risk Management Orders (4/23 Pre-Market)

| # | Order ID | Symbol | Side | Qty | Type | Stop Price | Status | Time |
|---|----------|--------|------|-----|------|------------|--------|------|
| 4 | 71b7b3bf | XLV | SELL | 47 | STOP | $136.46 | accepted | 2026-04-23 00:05 ET |
| 5 | 63cbc6a9 | XLE | SELL | 124 | STOP | $52.47 | accepted | 2026-04-23 00:05 ET |
| 6 | f91b4932 | GLD | SELL | 13 | STOP | $405.17 | accepted | 2026-04-23 00:05 ET |

**All GTC. Stop-loss at -7% from entry. Trailing stop on XLE blocked (shares held by stop order).**

---

## Daily P&L Tracking

| Date | Portfolio Value | Day P&L | Day P&L % | Cumulative P&L | S&P Day | S&P Cum |
|------|----------------|---------|-----------|-----------------|---------|---------|
| 4/22 | $100,000 | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% |
| 4/23 | $99,988.99 | -$11.01 est | -0.011% | -$11.01 | +1.05% | +0.42% |

**Notes:** Day 1 P&L is unrealized. Actual close prices from Alpaca show portfolio at $99,988.99. S&P significantly outperforming — defensive positioning is the drag.

---

## TSLA Earnings Decision (4/22 After Close)

**TSLA Q1 2026 Results:**
- EPS: $0.41 (beat $0.37 est) ✅
- Revenue: $22.39B (miss vs $22.7B) ❌
- Gross margin: 21.1% (up 478 bps YoY)
- Capex guidance: $5B ABOVE prior → spending >$25B in 2026
- Robotaxi: expanded to Dallas/Houston, unsupervised, no fleet size disclosed
- After-hours: +4.3% initially, then gave back gains on spending news

**DECISION: NO TSLA TRADE.** EPS beat but revenue miss + massive spending increase = negative FCF. Stock gave back gains. Not a clean momentum signal.

---

---

## Pre-Market Routine (2026-11-02) — Stop-Loss Reset Orders

**CONTEXT:** Alpaca MCP unavailable. Stop-losses expired 7/22/2026. Positions unprotected.
**ACTION REQUIRED:** Execute via Alpaca web UI or REST API immediately at market open.

### PRIORITY: Reset Stop-Loss Orders at Market Open

| # | Symbol | Side | Qty | Type | Stop Price | Basis | Notes |
|---|--------|------|-----|------|-----------|-------|-------|
| A | XLV | SELL | 47 | STOP_GTC | Need current price × 0.93 | Entry $146.73 | Get current quote first, set -7% from current |
| B | XLE | SELL | 124 | STOP_GTC | Need current price × 0.93 | Entry $56.42 | **HIGH PRIORITY**: Hormuz deal could close oil -20% |
| C | GLD | SELL | 13 | STOP_GTC | Need current price × 0.93 | Entry $435.66 | Get current quote first, set -7% from current |

**Steps to execute:**
1. Get current quotes for XLV, XLE, GLD via Alpaca
2. Calculate stop = current_price × 0.93 (7% below current)
3. Place GTC stop orders for each via: `POST /v2/orders`
4. XLE special note: If Hormuz deal confirmed TODAY → cancel stop order, place MARKET SELL immediately

### Regime Trigger Orders (Watch, Do Not Execute Yet)

| Trigger | Action | Size | Rationale |
|---------|--------|------|-----------|
| Hormuz deal confirmed | SELL XLE 124 shares at MARKET | Exit full position | WTI drops from $102 to ~$80 (-20%) |
| AAPL beats + strong guidance | BUY AAPL $8-10K MARKET (next session) | New position | Earnings momentum play |
| VIX breaks below 18 + AAPL beat | BUY QQQ or XLK $10-15K | Momentum in Risk-On | Increase equity exposure |
| VIX spikes above 25 | BUY SPY PUTS $5K hedge | Hedge | Election/Hormuz stress scenario |

---

## Position Performance Summary (4/23 Close)

| Symbol | Entry | Current | Total P&L | Day P&L | Stop | Distance to Stop |
|--------|-------|---------|-----------|---------|------|-------------------|
| XLV | $146.73 | $146.38 | -$16.59 | ~flat | $136.46 | -6.78% |
| XLE | $56.42 | $56.72 | +$37.56 | +0.32% | $52.47 | -7.50% |
| GLD | $435.66 | $433.43 | -$30.77 | -0.42% | $405.17 | -6.52% |

**All positions well above stops. No exits triggered.**