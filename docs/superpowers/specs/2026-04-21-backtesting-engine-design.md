# Phase 1: Backtesting Engine & Signal System — Design Spec

**Date:** 2026-04-21
**Status:** Approved
**Strategy:** NexusTrade-validated Quality + Momentum
**Framework:** PyBroker-first with Alpaca data

---

## 1. Architecture

PyBroker orchestrates backtesting. Alpaca provides price data. edgartools provides SEC fundamentals. Riskfolio-Lib computes Kelly-optimal position sizing. VIX-based regime overlay selects signal weights. Walk-forward validator prevents overfitting.

**Data flow:**

```
Alpaca API ──► alpaca_fetcher ──► Parquet cache ──► PyBroker DataSource
edgartools  ──► edgar_fetcher  ──► JSON cache    ──► Quality signal
FINRA API   ──► finra_fetcher  ──► JSON cache    ──► Sentiment signal
                                                                  │
                                                                  ▼
                                              ┌─────────────────────────────┐
                                              │     bull_strategy.py        │
                                              │                             │
                                              │  Quality ──► 25% weight    │
                                              │  Momentum ──► 30% weight   │
                                              │  Value ──► 10% weight      │
                                              │  Low Vol ──► 15% weight    │
                                              │  Sentiment ──► 20% weight  │
                                              │                             │
                                              │  Regime overlay adjusts     │
                                              │  weights per VIX threshold  │
                                              └─────────────┬───────────────┘
                                                            │
                                                            ▼
                                              Riskfolio-Lib ──► Kelly sizing
                                                            │
                                                            ▼
                                              PyBroker walk-forward runner
                                                            │
                                                            ▼
                                              Metrics: Sharpe, max DD, CI
```

**Walk-forward parameters:**
- Train window: 504 bars (2 years)
- Test window: 63 bars (1 quarter)
- Embargo: 5 bars (1 week)
- No lookahead. Only out-of-sample test window metrics reported.

---

## 2. Project Structure & Data Flow

```
src/
├── data/
│   ├── __init__.py
│   ├── alpaca_fetcher.py      # Alpaca price data → Parquet
│   ├── edgar_fetcher.py       # SEC filings → JSON fundamentals
│   ├── finra_fetcher.py       # Dark pool volume → JSON
│   └── cache.py               # Parquet/JSON read-through cache
├── signals/
│   ├── __init__.py
│   ├── quality.py             # Profitability + Piotroski F-score
│   ├── momentum.py            # 12-1 month return ranking
│   └── regime.py              # VIX-based regime classifier
├── strategy/
│   ├── __init__.py
│   └── bull_strategy.py       # Multi-factor composite + PyBroker integration
├── sizing/
│   ├── __init__.py
│   └── kelly.py               # Half-Kelly position sizing via Riskfolio-Lib
├── backtest/
│   ├── __init__.py
│   ├── runner.py              # PyBroker walk-forward execution
│   └── metrics.py             # Sharpe, max DD, bootstrap CI, regime stats
data/
├── prices/                    # Parquet price caches (gitignored)
└── fundamentals/              # JSON fundamental caches (gitignored)
tests/
├── fixtures/
│   ├── spy_2yr.parquet
│   ├── fundamentals_5companies.json
│   └── regime_history.csv
├── test_quality.py
├── test_momentum.py
├── test_regime.py
├── test_bull_strategy.py
├── test_kelly.py
├── test_runner.py
└── test_integration.py
```

**Data flow (runtime):**

1. `alpaca_fetcher.py` pulls bars from Alpaca API, writes to `data/prices/{symbol}.parquet`
2. `edgar_fetcher.py` pulls 10-K/10-Q from SEC via edgartools, writes to `data/fundamentals/{ticker}.json`
3. `finra_fetcher.py` pulls ATS volume from FINRA API, writes to `data/fundamentals/{ticker}_darkpool.json`
4. `cache.py` provides read-through: if Parquet/JSON exists and fresh (<24hr for prices, <90d for fundamentals), serve from disk. Otherwise, fetch and cache.
5. `runner.py` feeds PyBroker's `DataSource` from cached Parquet, registers `bull_strategy` as a PyBroker `Strategy`, and executes walk-forward.

---

## 3. Error Handling & Data Gaps

**Price data gaps:** Alpaca returns None for missing bars. PyBroker forward-fills by default — we set `lookahead=False` to prevent leakage. Bars missing >5 consecutive days: drop ticker from that window.

**SEC filing failures:** edgartools throws `EDGARFileNotFound` for companies that stopped filing. Catch per-ticker, log, skip. Fundamentals cache has TTL — stale data >90 days gets purged and re-fetched.

**FINRA ATS delays:** Dark pool data has 2-4 week lag. Every record timestamped with `as_of_date`. Signal generation only uses data where `as_of_date >= current_date - 4 weeks`. Stale dark pool data gets a decay weight: `weight = 1 - (weeks_stale / 4)`.

**Rate limits:** Alpaca paper API: 200 req/min. edgartools: 10 req/sec (SEC mandate). Built-in `tenacity` retry with exponential backoff. PyBroker fetches batch by default — we set batch size to 50 tickers.

**Walk-forward failures:** If a test window has <20 trading days of data (delistings, IPOs), skip that window. Log skipped windows. Metrics computed only on complete windows.

---

## 4. Anti-Overfitting Measures

**Walk-forward validation (primary guard):** 504-bar train, 63-bar test, 5-bar embargo. No lookahead. No in-sample metrics reported as "results." Only out-of-sample test windows count.

**Hard cap on single-year outliers:** Any year returning >60% gets capped at 60% before computing overall metrics. Prevents "lucky year" bias (validated by NexusTrade's Austin Starks).

**Multi-regime requirement:** Strategy must show positive Sharpe in ≥2 of 3 regimes (risk-on, late-cycle, stress). VIX thresholds: <20=risk-on, 20-30=late-cycle, >30=stress. Strategy failing in 2+ regimes gets rejected.

**Parameter count ceiling:** Max 8 tunable parameters. Current design uses 5 (quality margin threshold, momentum lookback, momentum top-N, VIX regime thresholds, stop-loss %). Adding factors requires removing existing ones.

**Bootstrap confidence intervals:** PyBroker computes 1000 bootstrap resamples. Report Sharpe and max drawdown with 95% CI. If Sharpe CI includes 0, strategy is statistically indistinguishable from random — reject.

**No data snooping:** Feature engineering only on training data. Signal thresholds locked before test windows. No mid-validation adjustments based on observed patterns.

---

## 5. Exit Rules & Risk Management

**Stop-loss:** -7% from entry (hard). Alpaca stop order at entry time.

**Trailing stop:** 10% on new positions. PyBroker `trailing_stop` built into strategy. Converted to Alpaca trailing stop order after fill confirmation.

**Time-based exit:** 30 calendar days max hold. Market order to close at next open if not hit stop/target.

**Regime-based exit:** VIX >30 (stress) → close 50% of positions at next open. Remaining 50% get stops tightened to -4%. Overrides normal exit rules.

**Position sizing:** Half-Kelly via Riskfolio-Lib. Inputs: backtest Sharpe, asset volatility, correlation matrix. Output: optimal fraction. Single position cap: 20% of portfolio. Default: 10%.

**Correlation limit:** Max 3 positions in same GICS level-2 sector. Checked at order time. Breach = reject order.

**Daily review:** Existing Bull midday routine handles position reviews.

**Re-entry cooldown:** 5-day cooldown after stop-out before re-entering same ticker. Prevents whipsaw revenge trading.

---

## 6. Testing Strategy

**Unit tests:** Each signal module (quality, momentum, regime) tested independently with fixed inputs and expected outputs. Mock Alpaca/SEC responses via `pytest` fixtures.

**Integration tests:** Full pipeline from raw data → signal generation → strategy output. Uses cached Parquet files as test fixtures (not live API calls).

**Walk-forward tests:** Anti-overfitting validation IS the integration test. `pytest` parametrizes over all walk-forward windows. Failing window ≠ test failure — logged and reported. Test fails only if <50% of windows are profitable.

**Backtest smoke test:** Run full pipeline on SPY alone. Must complete in <60 seconds. Catches data pipeline breaks.

**Test data:** `tests/fixtures/` contains:
- 2yr SPY price bars (Parquet)
- 5 company fundamental snapshots (JSON)
- Regime label history (CSV)

Committed to git. Regenerated only when schema changes.

**CI:** Run on push. Walk-forward suite ~5 min with cached data. Full pipeline test under 2 min.