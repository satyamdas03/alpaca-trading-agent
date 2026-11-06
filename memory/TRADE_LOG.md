# Trade Log

| Timestamp | Symbol | Side | Qty | Price | Rationale | Signal | Status |
|-----------|--------|------|-----|-------|-----------|--------|--------|
| 2026-04-22 09:31 ET | XLV | BUY | 47.707 | $146.73 | Defensive sector in Stress, UNH beat earnings | Low Vol ↑ in Stress regime | OPEN (unconfirmed) |
| 2026-04-22 09:31 ET | XLE | BUY | 124.076 | $56.42 | Oil at $99, Hormuz closed, direct beneficiary | Hormuz supply disruption | OPEN (unconfirmed) |
| 2026-04-22 09:33 ET | GLD | BUY | 13.772 | $435.66 | Safe haven in geopolitical Stress | Safe haven in Stress regime | OPEN (unconfirmed) |

---

## Orders Placed: 4/22 Pre-Market (Stress Regime) — ALL FILLED

| # | Order ID | Symbol | Side | Notional | Type | Status | Fill Price | Fill Time |
|---|----------|--------|------|----------|------|--------|------------|-----------|
| 1 | 69ed3794 | XLV | BUY | $7,000 | MARKET | FILLED | $146.73 | 9:31 AM ET |
| 2 | fa0dd584 | XLE | BUY | $7,000 | MARKET | FILLED | $56.42 | 9:31 AM ET |
| 3 | b2bb3e3b | GLD | BUY | $6,000 | MARKET | FILLED | $435.66 | 9:33 AM ET |

**Regime at entry: STRESS → Late Cycle borderline**
**Total deployed: $20K (20%). Cash: $80K.**

---

## Risk Management Orders (4/23 Pre-Market)

| # | Order ID | Symbol | Side | Qty | Type | Stop Price | Status | Time |
|---|----------|--------|------|-----|------|------------|--------|------|
| 4 | 71b7b3bf | XLV | SELL | 47 | STOP | $136.46 | GTC — verify active | 2026-04-23 00:05 ET |
| 5 | 63cbc6a9 | XLE | SELL | 124 | STOP | $52.47 | GTC — verify active | 2026-04-23 00:05 ET |
| 6 | f91b4932 | GLD | SELL | 13 | STOP | $405.17 | GTC — verify active | 2026-04-23 00:05 ET |

**⚠️ GTC stop orders set April 23. Must verify these are still active on Alpaca paper account.**

---

## 2026-11-06 Pre-Market: Trade Plan

### Regime: STRESS (VIX ~27-28 after Nov 5 AI selloff)

**No new trades today. Verification first.**

### PRIORITY ACTIONS AT OPEN:
1. **Verify positions** — get_account_info to confirm XLV/XLE/GLD still open
2. **Verify stops** — check stop orders 71b7b3bf, 63cbc6a9, f91b4932 still active
3. **Reset any lapsed stops** — if GTC orders expired, re-enter:
   - XLV: SELL STOP 47 shares @ $136.46 (or recalculate -7% from new price)
   - XLE: SELL STOP 124 shares @ $52.47 (or recalculate -7% from new price)
   - GLD: SELL STOP 13 shares @ $405.17 (or recalculate -7% from new price)

### CONDITIONAL ORDERS (for manual execution or Alpaca):

**IF XLV is still open AND current price > $146 (above entry):**
- HOLD. Raise stop to $136.46 or recalculate at current_price × 0.93

**IF XLV is still open AND current price $136-$146 (near stop):**
- HOLD with existing stop. Healthcare is defensive in AI selloff — may hold up.
- If price near $136-137 → consider exiting manually to preserve capital

**IF XLV is stopped out:**
- ACCEPT. Focus on XLE and GLD which are more likely to have appreciated.

**IF XLE is still open (likely):**
- Oil thesis intact: WTI ~$90, Brent ~$98, Hormuz still restricted
- HOLD. Raise stop to entry ($52.47) or trail at 10% from current high.

**IF GLD is still open (likely):**
- Safe haven demand elevated in STRESS regime
- Gold likely higher than entry ($435.66) over 6 months
- HOLD. Consider adding more GLD on this AI-shock market stress.

### POTENTIAL NEW TRADE (STRESS regime play):
- **GLD ADD:** If confirmed STRESS regime persists, add $5-7K more GLD
  - Signal: VIX > 25, Iran escalation, rate hike fears, AI regulation uncertainty
  - Risk: Snap-back rebound (chip stocks +5-8% premarket) = risk-off unwind
  - Sizing: $5K notional (~10 shares at ~$500)
  - Entry condition: VIX still above 24 at 9:30 AM open
  
- **DO NOT BUY** tech, AI names, semiconductors — mid-regime transition too risky

---

## Daily P&L Tracking (4/22-4/23 confirmed)

| Date | Portfolio Value | Day P&L | Day P&L % | Cumulative P&L | S&P Day | S&P Cum |
|------|----------------|---------|-----------|-----------------|---------|---------|
| 4/22 | $100,000 | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% |
| 4/23 | $99,988.99 | -$11.01 est | -0.011% | -$11.01 | +1.05% | +0.42% |
| 4/24–11/5 | UNTRACKED | -- | -- | -- | +7.7% (index) | -- |

---

## TSLA Earnings Decision (4/22 After Close — historical)

**DECISION: NO TSLA TRADE.** EPS beat but revenue miss + massive spending increase = negative FCF.
