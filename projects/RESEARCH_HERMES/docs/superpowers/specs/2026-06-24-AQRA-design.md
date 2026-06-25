# AQRA — Autonomous Quant Research Agent

**Date:** 2026-06-24  
**Status:** Design draft pending approval  
**Type:** Theorem-backed autonomous quant-research system with live paper-trading validation  

## 1. One-sentence thesis

Build the first autonomous AI scientist that discovers, debates, validates, certifies, and deploys quantitative trading strategies — with conformal non-spuriousness guarantees and adversarial review — and prove it works by running a live, auditable paper-trading portfolio.

## 2. Why this is revolutionary

Most quantitative finance research is broken by hidden human bias: the researcher generates hypotheses, cherry-picks factors, tunes parameters, and then reports a backtest. AQRA removes the human from the loop between hypothesis generation and live deployment. It is not a product like NeuralQuant; it is a **meta-research engine** whose output is publishable, validated strategies.

No public system combines all of these in one closed loop:

- LLM-driven hypothesis generation from literature and data
- Adversarial multi-agent debate (inherited from PARA-DEBATE)
- Conformal prediction to bound forecast uncertainty
- Rigorous statistical certification of backtest claims
- Autonomous paper-trading deployment with bounded capital
- Continuous reflection and strategy retirement

## 3. Phase 1 scope (bounded, buildable)

Phase 1 runs for **8–10 weeks** and targets a single asset class: **US equities** (S&P 500 universe). It will:

1. Ingest free data (yfinance, FRED, EDGAR Form 4, Finnhub, FMP free tier, Polygon free tier).
2. Generate candidate signals from a curated literature seed list plus LLM-driven symbolic combinations.
3. Run point-in-time walk-forward backtests with transaction costs and survivorship-bias handling.
4. Apply a conformalized selection test to control family-wise error rate.
5. Run every surviving candidate through an adversarial BEAR review.
6. Deploy the top-k surviving strategies on Alpaca paper with capital limits and kill switches.
7. Publish a public dashboard + a research paper/report explaining the methodology and live results.

Out of scope for Phase 1: India market, options, crypto, full genetic-programming symbolic regression, real-money trading, institutional data, and voice UI.

## 4. Core mathematical insight

The central theorem AQRA will implement and test is a **conformalized strategy-selection guarantee**:

> Let \(S_1, \dots, S_m\) be candidate strategies generated on a calibration window. If returns are exchangeable under the null hypothesis that a strategy has no edge, then conformal p-values constructed from a hold-out window satisfy \(P(p_i \leq \alpha) \leq \alpha\) for each true-null \(i\). By applying a multiple-testing correction (e.g., Benjamini–Yekutieli or a closed testing procedure), AQRA controls the false discovery rate or family-wise error rate over the selected strategy set.

This turns strategy discovery into a **statistical inference problem** rather than a backtest-optimization problem. AQRA reports not only Sharpe ratios but also:

- Conformal p-values for each strategy
- Coverage of prediction intervals
- Adjusted Sharpe bounds (Opdyke/Lo-style bias corrections)
- Drawdown-at-risk bounds under regime-stress scenarios

## 5. System architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AQRA — Phase 1 Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  Literature  │───▶│  Hypothesis  │───▶│   Signal     │                  │
│  │  Seed Corpus │    │  Generator   │    │   Library    │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                                              │                      │
│         ▼                                              ▼                      │
│  ┌──────────────┐                            ┌──────────────┐                │
│  │   arXiv /    │                            │  Symbolic /  │                │
│  │   SSRN feed  │                            │  LLM-driven  │                │
│  └──────────────┘                            │  candidates  │                │
│                                               └──────────────┘                │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │                    Data Laboratory                            │         │
│  │  yfinance · FRED · EDGAR · Finnhub · FMP · Polygon (free tier) │         │
│  │  point-in-time · survivorship-bias-free · transaction costs   │         │
│  └───────────────────────┬────────────────────────────────────────┘         │
│                          │                                                  │
│                          ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │                 Backtest Engine                               │         │
│  │  walk-forward · purged k-fold · regime-stratified splits      │         │
│  └───────────────────────┬────────────────────────────────────────┘         │
│                          │                                                  │
│                          ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │            Conformal Validator + Certifier                    │         │
│  │  conformal p-values · coverage test · bias-adjusted Sharpe    │         │
│  └───────────────────────┬────────────────────────────────────────┘         │
│                          │                                                  │
│                          ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │            Adversarial Debate Chamber (BEAR)                  │         │
│  │  look-ahead bias · data mining · economic rationale · robustness│        │
│  └───────────────────────┬────────────────────────────────────────┘         │
│                          │                                                  │
│                          ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │              Strategy Registry & Ranking                      │         │
│  │  certified candidates sorted by adjusted edge · risk budget   │         │
│  └───────────────────────┬────────────────────────────────────────┘         │
│                          │                                                  │
│                          ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │           Live Deployment Gate (Alpaca paper)                │         │
│  │  capital limits · kill switches · audit logging · git commit  │         │
│  └───────────────────────┬────────────────────────────────────────┘         │
│                          │                                                  │
│                          ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │           Monitoring + Reflection Loop                        │         │
│  │  live P&L · drawdown · coverage drift · strategy retirement   │         │
│  └──────────────────────────────────────────────────────────────┘         │
│                                                                             │
│  Public outputs: research report · live dashboard · git-tracked memory files  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Component responsibilities

| Component | What it does | Input | Output |
|---|---|---|---|
| **Literature Seed Corpus** | Curated list of seminal quant papers and factor ideas | arXiv q-fin, SSRN, JFQA abstracts | Seed hypotheses (momentum, value, quality, low vol, accruals, etc.) |
| **Hypothesis Generator** | Combines seed factors and LLM-driven ideas into testable signals | Seed corpus + data schema | Candidate signal specifications (formula + parameters + rationale) |
| **Data Laboratory** | Builds clean, point-in-time datasets with costs and bias guards | Raw free APIs | `features.parquet`, `returns.parquet`, `metadata.json` |
| **Backtest Engine** | Runs walk-forward and purged k-fold validation | Dataset + candidate signals | Per-strategy return series, IC, turnover, Sharpe, drawdown |
| **Conformal Validator** | Computes conformal p-values and coverage tests | Backtest predictions + hold-out labels | p-values, prediction sets, coverage flags |
| **Certifier** | Adjusts Sharpe, bounds drawdown, stress-tests regimes | Backtest stats + conformal outputs | Certified strategy dossier |
| **Adversarial Debate Chamber** | BEAR agent attacks every candidate for bias, robustness, rationale | Candidate dossier | Challenge report + pass/fail verdict |
| **Strategy Registry** | Tracks certified candidates, ranks by adjusted edge, allocates capital | Certified dossiers | Ranked strategy list with risk budgets |
| **Live Deployment Gate** | Executes paper trades on Alpaca with strict safety rules | Top-k strategies | Order log + position updates + git commits |
| **Monitoring + Reflection** | Tracks live performance, retires failing strategies, updates memory | Live P&L + market data | Updated registry + research log + dashboard |

## 6. Data sources for Phase 1

| Source | Data | Cost | Use |
|---|---|---|---|
| **yfinance** | Daily OHLCV, fundamentals, news | Free | Primary price + fallback fundamentals |
| **FRED** | Macro series (VIX, yields, spreads, CPI, PMI, unemployment) | Free | Regime detection + macro overlays |
| **EDGAR SEC Form 4** | Insider transactions | Free | Insider signal |
| **Finnhub** | Candles + news | Free tier | Technical indicators + sentiment fallback |
| **FMP free tier** | Profile + key metrics (limited calls) | Free | Fundamentals fallback |
| **Polygon.io free tier** | Real-time aggregates, historical bars | Free (5 calls/min) | Microstructure experiments, better OHLCV |
| **Alpha Vantage** | Fundamentals, forex, crypto | 25 calls/day | Additional fundamentals |
| **RSS + FinBERT** | News sentiment | Free | Sentiment signal without paid APIs |

All data will be cached in a local DuckDB or SQLite database with versioned snapshots, so results are reproducible.

## 7. Validation strategy

### 7.1 Internal validation

- **Known-factor reproduction:** AQRA must rediscover momentum, value, and quality effects with the correct signs and approximate magnitudes. If it cannot, the pipeline is broken.
- **Placebo test:** Randomly shuffled labels should produce zero certified strategies.
- **Regime-stress test:** Evaluate each certified strategy separately in Bear (2008, 2020, 2022) and Recovery regimes.
- **Transaction-cost sensitivity:** Report results at 0 bps, 10 bps, 20 bps, and 50 bps round-trip costs.

### 7.2 Conformal validation

- Build conformal prediction intervals for each candidate strategy's next-period return.
- Test marginal coverage on a hold-out period disjoint from calibration.
- Report empirical coverage vs. nominal coverage (target: 90%).
- Use conformal p-values + Benjamini–Yekutieli to control FDR over the candidate set.

### 7.3 Live validation

- Deploy top-k strategies on Alpaca paper for a minimum of **90 trading days**.
- Compare live portfolio to SPY, report alpha, Sharpe, max drawdown, hit rate, and IC.
- If coverage or FDR guarantees break in live data, retire the strategy and log the failure.

## 8. Risk and safety design

| Risk | Mitigation |
|---|---|
| Data mining / p-hacking | Conformal p-values + multiple-testing correction + placebo tests |
| Look-ahead bias | Point-in-time data construction with explicit lag rules |
| Survivorship bias | Use historical constituent lists (Wikipedia + yfinance delisted history) |
| Overfitting | Purged k-fold cross-validation + regime-stratified splits |
| Live capital loss | Paper trading only; per-strategy capital cap; daily loss limit; kill switch |
| LLM hallucination in hypothesis generation | BEAR agent + metric reconciliation + all signals must be numerically expressible |
| API rate limits | Tiered fallback chain + local cache + retry with backoff |
| Model drift | Continuous coverage monitoring; auto-retire if coverage breaks |

## 9. Success metrics

| Metric | Phase 1 target | How measured |
|---|---|---|
| Certified strategies | ≥ 3 distinct, non-overlapping strategies | Registry + dossiers |
| Known-factor reproduction | Sign + significance on momentum, value, quality | Internal backtest |
| Conformal coverage | 85–95% empirical coverage on hold-out | Coverage test |
| FDR control | ≤ 20% estimated false discoveries among selected | BY correction |
| Live portfolio Sharpe | ≥ 0.8 (paper) | Alpaca P&L vs. T-bill rate |
| Live alpha vs. SPY | Positive at 90-day horizon | Regression on SPY excess returns |
| Max drawdown | ≤ 20% | Alpaca portfolio equity curve |
| Hit rate | ≥ 55% | Percentage of positive trades |
| Information coefficient (IC) | ≥ 0.03 | Spearman rank correlation |
| Reproducibility | Full pipeline reruns from a single command | `make reproduce` |

## 10. Public outputs

1. **Open-source repository** with full code, data pipeline, backtest engine, and certification logic.
2. **Research paper / report** titled *AQRA: An Autonomous Conformal Agent for Quantitative Strategy Discovery* targeting arXiv q-fin.PM or Quantitative Finance journal.
3. **Live dashboard** showing certified strategies, paper portfolio P&L, coverage diagnostics, and audit log.
4. **Git-tracked memory files** similar to the Alpaca agent: daily summaries, strategy registry, research log.

## 11. Roadmap beyond Phase 1

- **Phase 2:** Add India (NSE 500) using NSE Bhavcopy + RBI macro; test cross-market portability.
- **Phase 3:** Add genetic-programming symbolic regression for truly novel signal discovery.
- **Phase 4:** Add options and crypto, plus microstructure signals from Polygon/TAQ.
- **Phase 5:** Introduce a multi-agent "reviewer community" where strategies must survive peer-review by multiple specialized agents.

---

## 12. Open questions

1. Should Phase 1 use a fixed literature seed corpus, or should it actively scrape arXiv/SSRN?
2. What is the initial capital for the paper-trading portfolio? ($10,000 suggested)
3. Should the system run fully autonomously, or require a human approval gate before live deployment?
4. Which multiple-testing correction should be the default? (Benjamini–Yekutieli recommended for arbitrary dependence)
5. Should we publish the code immediately, or keep it private until after 90 days of live results?

---

*Design prepared for user review. No implementation code has been written yet.*
