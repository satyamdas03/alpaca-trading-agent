# Portfolio State

**Last Updated:** 2026-11-19 Pre-Market Routine

## Account Overview (ESTIMATED — Alpaca MCP unavailable, last verified 4/23/2026)
- Account Type: Paper Trading
- Account Number: PA3M6G5LMKMI
- Starting Balance: $100,000.00
- Cash at Last Check (4/23): $80,000.00
- **CURRENT ACCOUNT STATUS: UNVERIFIED — must check via Alpaca REST or next MCP session**

## Open Positions (Estimated as of 2026-11-19)
| Symbol | Side | Qty | Entry Price | Est. Current Price | Est. Unrealized P&L | P&L % | Cost Basis |
|--------|------|-----|-------------|-------------------|---------------------|-------|------------|
| XLV | LONG | 47.707 | $146.73 | ~$189.65 (SSGA Nov 4) | ~+$2,048 | ~+29.3% | $7,000.00 |
| XLE | LONG | 124.076 | $56.42 | ~$54-58 (est, oil ↓) | Unknown | Unknown | $7,000.03 |
| GLD | LONG | 13.772 | $435.66 | Unknown | Unknown | Unknown | $6,000.00 |

**⚠️ WARNING: Stop-loss orders (IDs 71b7b3bf, 63cbc6a9, f91b4932) set GTC expiring 7/22/2026 have EXPIRED.**
**Positions are currently UNPROTECTED. Must re-set stops immediately on next Alpaca session.**

### Stop-Loss Orders — EXPIRED (were set 4/23/2026, GTC expired 7/22/2026)
| Symbol | Side | Qty | Type | Stop Price | Order ID | STATUS |
|--------|------|-----|------|-----------|----------|--------|
| XLV | SELL | 47 | STOP | $136.46 | 71b7b3bf | **EXPIRED** |
| XLE | SELL | 124 | STOP | $52.47 | 63cbc6a9 | **EXPIRED** |
| GLD | SELL | 13 | STOP | $405.17 | f91b4932 | **EXPIRED** |

### New Stops Needed (URGENT — place via Alpaca REST or next MCP session)
| Symbol | Recommended Stop (-7%) | Basis |
|--------|------------------------|-------|
| XLV | ~$176.37 (-7% from ~$189.65) | SSGA Nov 4 price |
| XLE | Determine from current price | Oil dropped since April |
| GLD | Determine from current price | Gold likely higher |

## Allocation (Estimated)
- Cash: ~80% (unchanged since April — no new trades executed)
- Equities: ~20% (3 positions: XLV, XLE, GLD)
- Options: 0%
- Crypto: 0%
- **Target in Late Cycle: 35-40% equities. Still underdeployed.**

## Performance Tracking

### Historical Returns
| Date | Equity | Day P&L | Day P&L % | Cum P&L | S&P Day | S&P Cum | Alpha |
|------|--------|---------|-----------|----------|---------|---------|-------|
| 4/22 | $100,000* | -$6.90 | -0.007% | -$6.90 | -0.63% | -0.63% | +0.62% |
| 4/23 | $99,988.99 | -$4.11 est | -0.004% | -$11.01 | +1.05% | +0.42% | -0.43% |
| 11/19 | Unverified | Unknown | Unknown | Unknown | — | +10.5% | — |

*Note: 7 months of P&L untracked. Must verify via Alpaca. XLV +29% suggests significant positive contribution.

### Benchmark Comparison (Estimated)
- S&P 500 YTD 2026: +10.5% (as of Nov 13, 2026)
- Portfolio YTD: Unverified — likely significantly positive given XLV +29%
- **Need Alpaca verification to calculate accurate alpha**

## Market Context (2026-11-19 Pre-Market)
- S&P 500: ~7,400 (+10.5% YTD as of Nov 13)
- VIX: **24.56** (down from 25.46 yesterday) — LATE CYCLE/borderline Stress
- 10Y Treasury yield: Rising (hawkish Fed minutes cited)
- Fed funds rate: **3.75-4.0%** — hawkish, two Oct dissents for hike
- Regime: **LATE CYCLE** (VIX 20-25, Fed hawkish, Hormuz partial)

### Iran/Hormuz Update (November 2026)
- Partial peace deal reached around June 2026 → Hormuz now flowing at **54% of pre-war** (9.34M bpd vs 17.15M prewar)
- WTI: ~$86/bbl (down from April's $96)
- Brent: ~$93/bbl (down from April's $105)
- Attacks continue to blunt hopes for full Iran truce
- Key risk: oil price volatility if talks collapse again

### Key Overnight Events
- **Nvidia Q3 FY2027 (reported Nov 18):** Revenue $115.8B (+103% YoY), EPS $2.68 vs $2.47 est. Beat across board. Jensen Huang resigned as CEO (Colette Kress interim). Stock slipping today (sell-the-news).
- **Anthropic IPO (ANT, Nasdaq):** Market debut today. Last private valuation $965B, IPO could reach $2T. Tech stocks rallied pre-market.
- **Alibaba:** Cloud revenue growth +53% — AI demand narrative reinforced.

## Key Assessment (November 19, 2026)
**Regime shifted: Risk-On (April) → Late Cycle now.**
- XLV massive winner: Entry $146.73, est. current ~$189.65 (+29%)
- Stop-losses EXPIRED. This is the most urgent action item.
- 80% cash drag continues but Late Cycle (not Risk-On) = less aggressive deployment warranted
- Nvidia post-earnings dip = potential value entry in AI secular winner
- VIX near Stress boundary = keep some defensive posture

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