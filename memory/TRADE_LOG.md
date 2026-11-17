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

## 2026-11-17 Pre-Market Assessment

**Regime: LATE CYCLE** | VIX: ~22.7 | S&P: 7,561 | WTI: ~$87 | Brent: ~$92

### Stop-Loss Status — EXPIRED
All GTC stop orders (placed 4/23) expired on July 22, 2026. Positions are UNPROTECTED.

### Estimated Position Status (Alpaca MCP unavailable — estimates based on market data)
| Symbol | Entry | Est. Current | Est. P&L | Stop (Expired) | Action |
|--------|-------|-------------|----------|----------------|--------|
| XLV | $146.73 | Unknown | Unknown | $136.46 (exp 7/22) | Verify + reset stop |
| XLE | $56.42 | ~$62-64 | +~$700-900 | $52.47 (exp 7/22) | Verify + tighten stop |
| GLD | $435.66 | Unknown (likely higher) | Likely positive | $405.17 (exp 7/22) | Verify + reset stop |

### Manual Orders for Execution (Alpaca MCP Disconnected)

**PRIORITY 1 — Replace Expired Stops (Execute at Market Open):**
```
ORDER 7: XLV SELL STOP 47 shares, recalculate at -7% from current price (GTC, 90-day expiry)
ORDER 8: XLE SELL STOP 124 shares, recalculate at -7% from current price (GTC, 90-day expiry)  
ORDER 9: GLD SELL STOP 13 shares, recalculate at -7% from current price (GTC, 90-day expiry)
```

**PRIORITY 2 — XLE: Assess profit-taking given oil thesis weakening**
- Oil thesis weakened: WTI $96 → $87 (-9.4%) since entry
- XLE still profitable from $56.42 entry (est. current $62-64)
- Recommended: Tighten stop to -4% from current (vs default -7%) given weakening thesis
- If XLE close > $64: Consider taking 50% profit, keeping 50% with tight stop

**PRIORITY 3 — Post-NVDA (After 4:20 PM ET close):**
- IF NVDA beats + guidance positive → Consider $5K SMH or QQQ position at next open
- IF NVDA misses → No new tech exposure, assess hedges
- IF NVDA in-line + CEO/margin concerns → No new positions, wait for follow-through

### Trade Decision: NO NEW TRADES PRE-MARKET
Reason: NVDA binary event today. VIX 22.7 = Late Cycle, not Risk-On. Assess after earnings.

---

## Position Performance Summary (4/23 Close)

| Symbol | Entry | Current | Total P&L | Day P&L | Stop | Distance to Stop |
|--------|-------|---------|-----------|---------|------|-------------------|
| XLV | $146.73 | $146.38 | -$16.59 | ~flat | $136.46 | -6.78% |
| XLE | $56.42 | $56.72 | +$37.56 | +0.32% | $52.47 | -7.50% |
| GLD | $435.66 | $433.43 | -$30.77 | -0.42% | $405.17 | -6.52% |

**All positions well above stops. No exits triggered.**