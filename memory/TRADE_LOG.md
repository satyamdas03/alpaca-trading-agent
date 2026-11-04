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
| 4 | 71b7b3bf | XLV | SELL | 47 | STOP | $136.46 | **EXPIRED 7/22** | 2026-04-23 00:05 ET |
| 5 | 63cbc6a9 | XLE | SELL | 124 | STOP | $52.47 | **EXPIRED 7/22** | 2026-04-23 00:05 ET |
| 6 | f91b4932 | GLD | SELL | 13 | STOP | $405.17 | **EXPIRED 7/22** | 2026-04-23 00:05 ET |

**⚠️ ALL STOP-LOSS ORDERS EXPIRED JULY 22, 2026. POSITIONS UNPROTECTED FOR 3+ MONTHS.**

---

## REQUIRED ORDERS (11/4 Pre-Market — Manual Execution via Alpaca REST)

**Priority: Set stop-losses immediately at market open (9:30 AM ET)**

| # | Symbol | Side | Qty | Type | Stop Price | Rationale |
|---|--------|------|-----|------|------------|-----------|
| 7 | XLV | SELL | 47 | STOP GTC | $172.00 | -7% from est. $185.38. Lock in most of +26% gain. |
| 8 | XLE | SELL | 124 | STOP GTC | $62.50 | Tight stop (-6.3%). Hormuz deal = oil crash risk. |
| 9 | GLD | SELL | 13 | STOP GTC | [verify price first] | -7% from verified current price. |

**Manual REST execution format:**
```
curl -X POST https://paper-api.alpaca.markets/v2/orders \
  -H "APCA-API-KEY-ID: PK7CLPEOIIEKMEVPNWEF4GPL22" \
  -H "APCA-API-SECRET-KEY: [from docs/superpowers/plans]" \
  -d '{"symbol":"XLV","qty":"47","side":"sell","type":"stop","time_in_force":"gtc","stop_price":"172.00"}'
```

---

## Daily P&L Tracking

| Date | Portfolio Value | Day P&L | Day P&L % | Cumulative P&L | S&P Day | S&P Cum |
|------|----------------|---------|-----------|-----------------|---------|---------|
| 4/22 | $100,000 | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% |
| 4/23 | $99,988.99 | -$11.01 est | -0.011% | -$11.01 | +1.05% | +0.42% |
| 11/4 | ~$101,500 est | — | — | ~+$1,500 est | +10.3% YTD | — |

**Alpha vs S&P 500: approximately -8.8pp (portfolio ~+1.5% vs S&P +10.3% since Jan 2026)**
**Primary drag: 80% cash position + defensive positioning**

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

**All positions well above stops. No exits triggered.**

---

## Watchlist / New Trade Candidates (11/4)

| Symbol | Thesis | Entry Trigger | Size |
|--------|--------|--------------|------|
| PLTR | +96% revenue, AI gov spending, Dem Congress = more gov AI contracts | VIX < 20 sustained | $8K |
| QQQ | Tech recovery + Dem gridlock limits regulation | Hormuz deal closes + VIX < 19 | $10K |
| XLP | Consumer staples defensive hedge | If no Hormuz deal + VIX > 22 | $7K |
| XLK | Tech momentum in Risk-On | Same as QQQ trigger | $8K |
