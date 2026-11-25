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

## 2026-11-25 Pre-Market Assessment (7-Month Gap Session)

**Regime: LATE CYCLE / STRESS BORDERLINE**
**Alpaca status: INACCESSIBLE (proxy blocks paper-api.alpaca.markets)**
**→ All orders below are for MANUAL EXECUTION**

### Critical Issue: Stop-Loss Expiry
GTC stop orders were set to expire 7/22 (July 22, 2026). They have EXPIRED.
Positions are currently UNPROTECTED if still open. Highest priority task.

### Inferred Position Status (MUST VERIFY)

| Symbol | Likely Status | Rationale |
|--------|--------------|-----------|
| XLV | OPEN (inferred) | Healthcare defensive sector — stop at $136.46 unlikely triggered in bull market |
| XLE | STOPPED OUT (inferred) | Oil from $96 → $83-85 (-13%); Hormuz deal June; XLE almost certainly < $52.47 at some point |
| GLD | OPEN (inferred) | Gold bull run, geopolitical uncertainty bids; stop at $405.17 unlikely triggered |

### Orders for Manual Execution (2026-11-25)

**Priority 1: Verify account state**
- Log into paper.alpaca.markets
- Check actual positions and cash balance

**Priority 2: If XLE still open**
```
SELL 124 XLE MARKET
Reason: Oil thesis invalidated (Hormuz deal June 2026, WTI now $83-85 vs $96 at trade entry-time)
Oil down ~13% → XLE likely near or below original $52.47 stop
```

**Priority 3: Reset stop-losses if XLV/GLD open (stops expired July 22)**
```
XLV: SELL 47 STOP $136.46 GTC (or use current price × 0.93 as new stop)
GLD: SELL 13 STOP $405.17 GTC (or use current price × 0.93 as new stop)
Note: If XLV price > $157, set stop to $146 (10% trailing). If GLD > $468, set stop to $435 (10% trailing).
```

**Priority 4: No new positions today**
- Nasdaq -3.11% futures, VIX spiking on tariff news
- PCE print due today — binary risk
- Short trading week (Thanksgiving tomorrow)
- Wait for regime clarity

### Today's Regime: Late Cycle → Stress Transition Signals

| Signal | Value | Interpretation |
|--------|-------|---------------|
| Nasdaq 100 futures | -3.11% | Risk-off, tech vulnerable |
| S&P 500 futures | -1.9% | Broad selloff |
| VIX trend | Spiked to 28, now ~22-26 | Late Cycle/Stress border |
| Fed December | 97% rate HIKE | Tightening = headwind |
| New tariffs | 20% China/EU/12 partners | Stagflation risk |
| PCE today | Hot expected | Confirms hike path |
| Oil | $83-85 (WTI) | Supply surplus, Hormuz premium gone |
| KOSPI | -6% | Semiconductor/tech global risk-off |

**Decision: HOLD CASH HEAVY. Confirm positions. Reset stops. No new buys.**

## Position Performance Summary (4/23 Close)

| Symbol | Entry | Current | Total P&L | Day P&L | Stop | Distance to Stop |
|--------|-------|---------|-----------|---------|------|-------------------|
| XLV | $146.73 | $146.38 | -$16.59 | ~flat | $136.46 | -6.78% |
| XLE | $56.42 | $56.72 | +$37.56 | +0.32% | $52.47 | -7.50% |
| GLD | $435.66 | $433.43 | -$30.77 | -0.42% | $405.17 | -6.52% |

**All positions well above stops. No exits triggered.**