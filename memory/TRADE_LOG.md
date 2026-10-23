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

## Risk Management Orders (4/23 Pre-Market) — ⚠️ ALL EXPIRED ~7/22/2026

| # | Order ID | Symbol | Side | Qty | Type | Stop Price | Status | Placed | Expiry |
|---|----------|--------|------|-----|------|------------|--------|--------|--------|
| 4 | 71b7b3bf | XLV | SELL | 47 | STOP | $136.46 | **EXPIRED** | 2026-04-23 | ~2026-07-22 |
| 5 | 63cbc6a9 | XLE | SELL | 124 | STOP | $52.47 | **EXPIRED** | 2026-04-23 | ~2026-07-22 |
| 6 | f91b4932 | GLD | SELL | 13 | STOP | $405.17 | **EXPIRED** | 2026-04-23 | ~2026-07-22 |

⚠️ CRITICAL: Alpaca GTC orders typically expire after 90 days. These expired around July 22, 2026.
Positions have been UNPROTECTED since then. Re-place immediately.

---

## URGENT: New Stop-Loss Orders to Place (2026-10-23)

Based on estimated current prices from WebSearch research.
**Execute manually via Alpaca web interface or REST API.**

| # | Symbol | Side | Qty | Type | Stop Price | Est. Current | Distance | Notes |
|---|--------|------|-----|------|------------|-------------|----------|-------|
| 7 | XLV | SELL | 47 | STOP GTC | $153.45 | ~$165 est | -7.0% | Replace expired #4 |
| 8 | XLE | SELL | 124 | STOP GTC | $63.24 | ~$68 est | -7.0% | Replace expired #5 |
| 9 | GLD | SELL | 13 | STOP GTC | $423.15 | ~$455 est | -7.0% | Replace expired #6 |

**Priority: Execute orders 7, 8, 9 BEFORE market open or at open.**
**Note:** Verify current prices first. Adjust stop prices based on actual current levels.

**Formula:** Stop = CurrentPrice × 0.93 (7% below current)

---

## Potential New Trades (2026-10-23 Watch List)

### Option A: QQQ Dip Buy (If VIX stays below 20)
- **Signal:** Nasdaq -2.9% Thursday (tech sell-off from META -6.9%, TSLA -3%)
- **Thesis:** Risk-On regime intact (VIX 19.03). Dip in tech = entry opportunity.
- **Size:** $10,000-$15,000 (10-15% of portfolio)
- **Entry:** Market buy at open IF VIX below 20.0
- **Stop:** -7% from entry
- **Risk:** VIX breaks 20 → regime shifts to Late Cycle → reduce momentum positions

### Option B: Add to XLE
- **Signal:** XLE +20.5% since entry, Hormuz still disrupted, Brent ~$100+
- **Thesis:** XLE thesis intact. Add to winner.
- **Size:** $5,000-$7,000 additional (bring XLE to ~15% of portfolio)
- **Entry:** Market buy at open
- **Stop:** Same as new stop order above ($63.24 est)
- **Risk:** Sudden Hormuz resolution = oil crash = stop triggered

### No Action Scenario
- **Condition:** VIX breaks above 20.0 at open → Late Cycle regime
- **Action:** Only re-place stop-losses. No new positions.
- **Hold:** All current positions (XLV, XLE, GLD all profitable)

---

## Daily P&L Tracking

| Date | Portfolio Value | Day P&L | Day P&L % | Cumulative P&L | S&P Day | S&P Cum |
|------|----------------|---------|-----------|-----------------|---------|---------|
| 4/22 | $100,000 | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% |
| 4/23 | $99,988.99 | -$11.01 est | -0.011% | -$11.01 | +1.05% | +0.42% |
| 10/23 | ~$102,570 est | N/A | N/A | ~+$2,570 | N/A | +12.7% YTD |

**Notes:** 6-month gap in tracking. Alpaca MCP unavailable. Values estimated via ETF price research.

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

## Position Performance Summary (4/23 Close)

| Symbol | Entry | Current | Total P&L | Day P&L | Stop | Distance to Stop |
|--------|-------|---------|-----------|---------|------|-------------------|
| XLV | $146.73 | $146.38 | -$16.59 | ~flat | $136.46 | -6.78% |
| XLE | $56.42 | $56.72 | +$37.56 | +0.32% | $52.47 | -7.50% |
| GLD | $435.66 | $433.43 | -$30.77 | -0.42% | $405.17 | -6.52% |

All positions well above stops. No exits triggered.
