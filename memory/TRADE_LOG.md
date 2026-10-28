# Trade Log

| Timestamp | Symbol | Side | Qty | Price | Rationale | Signal | Status |
|-----------|--------|------|-----|-------|-----------|--------|--------|
| 2026-04-22 09:31 ET | XLV | BUY | 47.707 | $146.73 | Defensive sector in Stress, UNH beat earnings | Low Vol ↑ in Stress regime | OPEN (unverified — stop may have expired) |
| 2026-04-22 09:31 ET | XLE | BUY | 124.076 | $56.42 | Oil at $99, Hormuz closed, direct beneficiary | Hormuz supply disruption | OPEN (likely profitable, oil now $101-104) |
| 2026-04-22 09:33 ET | GLD | BUY | 13.772 | $435.66 | Safe haven in geopolitical Stress | Safe haven in Stress regime | OPEN (likely profitable, gold safe haven bid) |

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
| 4 | 71b7b3bf | XLV | SELL | 47 | STOP | $136.46 | **EXPIRED (GTC expiry 7/22/2026)** | 2026-04-23 00:05 ET |
| 5 | 63cbc6a9 | XLE | SELL | 124 | STOP | $52.47 | **EXPIRED (GTC expiry 7/22/2026)** | 2026-04-23 00:05 ET |
| 6 | f91b4932 | GLD | SELL | 13 | STOP | $405.17 | **EXPIRED (GTC expiry 7/22/2026)** | 2026-04-23 00:05 ET |

**⚠️ WARNING: All GTC stop orders set to expire 7/22. As of 10/28/2026, these have EXPIRED. Positions have NO stop-loss protection. IMMEDIATE ACTION REQUIRED: Place new stop orders once Alpaca access is restored.**

---

## Daily P&L Tracking

| Date | Portfolio Value | Day P&L | Day P&L % | Cumulative P&L | S&P Day | S&P Cum |
|------|----------------|---------|-----------|-----------------|---------|---------|
| 4/22 | $100,000 | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% |
| 4/23 | $99,988.99 | -$11.01 est | -0.011% | -$11.01 | +1.05% | +0.42% |
| 4/24 - 10/27 | **UNKNOWN — no sessions ran** | — | — | — | — | — |
| 10/28 | **UNKNOWN — Alpaca disconnected** | — | — | — | — | — |

**S&P 500 Apr 23 → Oct 27: ~7,138 → 7,722 = +8.2%**
**Portfolio Apr 23 → Oct 28: UNKNOWN — must verify via Alpaca**

---

## Planned Orders: 10/28/2026 (PENDING — MANUAL EXECUTION REQUIRED)

**Alpaca MCP is disconnected. Execute via Alpaca REST API or Alpaca web interface.**

### Step 1: Verify positions first
```
GET https://paper-api.alpaca.markets/v2/positions
Authorization: Bearer PK7CLPEOIIEKMEVPNWEF4GPL22:SECRET
```

### Step 2: Place new stop orders (old ones expired 7/22)
For each existing position still open, place new GTC stop orders at -7% from current price.

### Step 3: New momentum trades (execute after Fed decision at 2PM ET today if HOLD confirmed)

| # | Symbol | Side | Notional | Type | Rationale | Signal | Condition |
|---|--------|------|----------|------|-----------|--------|-----------|
| 7 | SMH | BUY | $10,000 | MARKET | Chip stocks leading rally (Oct 28), AI capex GOOGL/MSFT tonight | Momentum Risk-On | After Fed HOLD confirmed 2PM ET |
| 8 | QQQ | BUY | $10,000 | MARKET | Nasdaq near records, tech momentum | Momentum Risk-On | After Fed HOLD confirmed 2PM ET + GOOGL/MSFT earnings check |

**Risk: If Fed surprises with HIKE → cancel orders**
**Risk: If GOOGL/MSFT earnings disappoint → delay QQQ buy**

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

## Position Performance Summary (4/23 Close — LAST KNOWN)

| Symbol | Entry | Current | Total P&L | Day P&L | Stop | Distance to Stop |
|--------|-------|---------|-----------|---------|------|-------------------|
| XLV | $146.73 | $146.38 | -$16.59 | ~flat | $136.46 (EXPIRED) | N/A |
| XLE | $56.42 | $56.72 | +$37.56 | +0.32% | $52.47 (EXPIRED) | N/A |
| GLD | $435.66 | $433.43 | -$30.77 | -0.42% | $405.17 (EXPIRED) | N/A |
