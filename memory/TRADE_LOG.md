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
| 4 | 71b7b3bf | XLV | SELL | 47 | STOP | $136.46 | **EXPIRED 7/22/2026** | 2026-04-23 00:05 ET |
| 5 | 63cbc6a9 | XLE | SELL | 124 | STOP | $52.47 | **EXPIRED 7/22/2026** | 2026-04-23 00:05 ET |
| 6 | f91b4932 | GLD | SELL | 13 | STOP | $405.17 | **EXPIRED 7/22/2026** | 2026-04-23 00:05 ET |

**⚠️ WARNING: All GTC stop-losses EXPIRED 7/22/2026. Positions unprotected since then.**

---

## URGENT: Stop-Loss Reset Orders (11/12 Pre-Market) — MANUAL EXECUTION REQUIRED

**Alpaca REST API unavailable (proxy blocked). Execute these orders manually in Alpaca paper account.**

Estimated current prices (from web research — verify at market open):
- XLV: ~$158-165 (Schwab showed $158.66 on 6/30/2026)
- XLE: ~$68-78 (extrapolated from Brent $115 Oct peak, oil thesis intact)
- GLD: ~$470-510 (gold strong on geopolitical tensions)

**Orders to place at 9:30 AM ET (market open):**

| # | Symbol | Side | Qty | Type | Stop Price (-7% from est) | Priority |
|---|--------|------|-----|------|--------------------------|---------|
| 7 | XLV | SELL | 47 | STOP GTC | ~$150 (verify: 0.93 × current) | HIGH |
| 8 | XLE | SELL | 124 | STOP GTC | ~$65 (verify: 0.93 × current) | HIGH |
| 9 | GLD | SELL | 13 | STOP GTC | ~$440 (verify: 0.93 × current) | HIGH |

**Formula: Stop price = current_price × 0.93 (7% stop-loss)**

---

## New Trade Orders — 11/12 Pre-Market Assessment

**Regime: LATE CYCLE (leaning Stress). Two tanker fires in Hormuz today.**

### Recommended New Trades (pending Alpaca access):

**TRADE A: Add XLE (Energy ETF)**
- Side: BUY
- Notional: $10,000
- Type: MARKET at open
- Rationale: Two tankers carrying 4M+ barrels ablaze in Hormuz on 11/12. Oil spike likely.
- Signal: Supply disruption (direct catalyst today)
- Source: Al Arabiya + IRGC statement (11/12); CNBC Hormuz coverage
- Risk: Fire confirmed as accident (not attack) → oil normalizes
- Size: $10K brings total energy exposure to ~$17-18K

**TRADE B: Add GLD (Gold ETF)**
- Side: BUY
- Notional: $5,000
- Type: MARKET at open
- Rationale: Safe haven bid from tanker fires + Trump "no deal needed with Iran" = persistent geopolitical risk
- Signal: Safe haven demand + inflation from oil spike
- Source: Reuters/CNBC Hormuz coverage; Trump statement 11/11
- Risk: Tanker fires resolve quickly, gold gives back gains
- Size: $5K to bring total gold exposure to ~$11K

**NO TRADES — Nvidia/Tech:**
- NVDA: Wait for board investigation clarity (11/18 congressional briefing)
- QQQ, XLK: Nasdaq -0.8% futures due to Nvidia. Avoid today.

---

## Daily P&L Tracking

| Date | Portfolio Value | Day P&L | Day P&L % | Cumulative P&L | S&P Day | S&P Cum |
|------|----------------|---------|-----------|-----------------|---------|---------|
| 4/22 | $100,000 | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% |
| 4/23 | $99,988.99 | -$11.01 est | -0.011% | -$11.01 | +1.05% | +0.42% |
| 11/12 | UNKNOWN* | UNKNOWN | UNKNOWN | UNKNOWN | +5.8%** | -- |

*Cannot access Alpaca API (proxy blocked in this environment). Portfolio value estimated from position price movements.
**S&P 500 moved from 7,137.90 (4/23) to ~7,550 (11/9) = +5.8% since last session.

**Estimated portfolio value (11/12):**
- Starting: $99,989
- XLV appreciation: 47.707 shares × ($160 est - $146.73) = +$633 est
- XLE appreciation: 124.076 shares × ($72 est - $56.42) = +$1,931 est
- GLD appreciation: 13.772 shares × ($490 est - $435.66) = +$748 est
- Cash unchanged: $80,000
- **Estimated total: ~$103,301 (+$3,312, +3.3%)**
- **vs S&P +5.8% over same period = Alpha: -2.5% (defensive tilt cost us)**

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

## Position Performance Summary (Last Known: 4/23 Close)

| Symbol | Entry | Last Close | Entry→Close | Day Chg | Stop | Distance to Stop |
|--------|-------|------------|-------------|---------|------|-------------------|
| XLV | $146.73 | $146.38 | -$16.59 | 0.00% | $136.46 | -6.78% |
| XLE | $56.42 | $56.72 | +$37.56 | +0.32% | $52.47 | -7.50% |
| GLD | $435.66 | $433.43 | -$30.77 | -0.42% | $405.17 | -6.52% |

**All positions well above stops at 4/23. Stops expired 7/22 — reset required TODAY.**
