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

Phase 1 targets a single asset class: **US equities** (S&P 500 universe). It is explicitly organized as **two independent research lanes** under one meta-system, and has two sub-phases:

- **Lane S — Structural Alpha:** Persistent, low-turnover factor premia (momentum, value, quality, low volatility, insider conviction, macro regime rotation). Certification horizon: months to years.
- **Lane I — Informational Alpha:** Fast-decaying signals from news, earnings, sentiment, and short-term price patterns. Certification horizon: days to weeks; rapid retirement.

- **Phase 1a — Build & Certification:** 8–10 weeks. Build the dual-lane data lab, backtest engine, conformal validator, BEAR chamber, and certify ≥ 2 Lane S and ≥ 2 Lane I strategies.
- **Phase 1b — Live Validation:** 90 trading days (~18 weeks). Deploy top-2 Lane S and top-2 Lane I strategies on Alpaca paper, monitor coverage, and publish results.

Phase 1 will:

1. Ingest free data (yfinance, FRED, EDGAR Form 4, Finnhub, FMP free tier, Polygon free tier, RSS + FinBERT).
2. Generate candidate signals from a curated literature seed list plus LLM-driven symbolic combinations, **separated into Lane S and Lane I candidate pools**.
3. Run point-in-time walk-forward backtests with transaction costs and survivorship-bias handling, **per lane with lane-appropriate holding periods and rebalancing frequencies**.
4. Apply a conformalized selection test to control family-wise error rate **within each lane**.
5. Run every surviving candidate through an adversarial BEAR review, including the question: *Is this candidate pretending to be the other lane?*
6. Deploy the **top-2 Lane S + top-2 Lane I** surviving strategies on Alpaca paper with **lane-specific capital budgets, risk limits, and kill switches**.
7. Publish a public dashboard + a research paper/report explaining the dual-lane methodology and live results.

Out of scope for Phase 1: India market, options, crypto, full genetic-programming symbolic regression, real-money trading, institutional data, and voice UI.

## 4. Core mathematical insight

The central theorem AQRA will implement and test is a **dual-lane conformalized strategy-selection guarantee**:

> Let \(\mathcal{S}\) and \(\mathcal{I}\) be the candidate sets for Lane S (structural) and Lane I (informational), generated and calibrated independently. Within each lane, if returns are exchangeable under the null hypothesis that a candidate has no edge, then conformal p-values constructed from a hold-out window satisfy \(P(p_j \leq \alpha) \leq \alpha\) for each true-null \(j\). By applying a multiple-testing correction (e.g., Benjamini–Yekutieli) **within each lane**, AQRA controls the false discovery rate separately for structural and informational strategies.

Because Lane S and Lane I have different return distributions, calibration windows, and rebalancing cadences, **pooling them would violate exchangeability** and break coverage. AQRA therefore maintains two independent conformal pipelines.

This turns strategy discovery into a **statistical inference problem** rather than a backtest-optimization problem. AQRA reports not only Sharpe ratios but also:

- Per-lane conformal p-values for each strategy
- Per-lane coverage of prediction intervals
- Adjusted Sharpe bounds (Opdyke/Lo-style bias corrections)
- Lane S: drawdown-at-risk bounds under regime-stress scenarios
- Lane I: signal half-life and cost-adjusted edge bounds

## 5. System architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              AQRA — Phase 1 Architecture (Dual-Lane)                          │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                               │
│  Shared Front End                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                                  │
│  │  Literature  │───▶│  Hypothesis  │───▶│   Signal     │                                  │
│  │  Seed Corpus │    │  Generator   │    │   Library    │                                  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘                                  │
│         │                                        │                                            │
│         ▼                                        ▼                                            │
│  ┌──────────────┐                        ┌──────────────┐                                  │
│  │   arXiv /    │                        │  Symbolic /  │                                  │
│  │   SSRN feed  │                        │  LLM-driven  │                                  │
│  └──────────────┘                        │  candidates  │                                  │
│                                          └──────────────┘                                   │
│                                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐      │
│  │                            Data Laboratory                                          │      │
│  │  Lane S feeds: yfinance · FRED · EDGAR · FMP · Alpha Vantage                        │      │
│  │  Lane I feeds: yfinance · Polygon · Finnhub · RSS+FinBERT · EDGAR earnings calendar  │      │
│  │  Shared: point-in-time · survivorship-bias-free · transaction costs                │      │
│  └──────────────────────────┬─────────────────────────────────────────────────────────┘      │
│                             │                                                                 │
│           ┌─────────────────┴─────────────────┐                                               │
│           ▼                                   ▼                                               │
│  ┌──────────────────────┐          ┌──────────────────────┐                                │
│  │   Lane S Pipeline    │          │   Lane I Pipeline    │                                │
│  │  · quarterly signals │          │  · daily signals     │                                │
│  │  · 1–3 month holds   │          │  · 1–5 day holds     │                                │
│  │  · low turnover      │          │  · high turnover     │                                │
│  └──────────┬───────────┘          └──────────┬───────────┘                                │
│             │                                   │                                             │
│             ▼                                   ▼                                             │
│  ┌──────────────────────┐          ┌──────────────────────┐                                │
│  │   Backtest Engine    │          │   Backtest Engine    │                                │
│  │  walk-forward ·      │          │  walk-forward ·      │                                │
│  │  regime-stratified   │          │  event-stratified    │                                │
│  └──────────┬───────────┘          └──────────┬───────────┘                                │
│             │                                   │                                             │
│             ▼                                   ▼                                             │
│  ┌──────────────────────┐          ┌──────────────────────┐                                │
│  │ Conformal Validator  │          │ Conformal Validator  │                                │
│  │  p-values · coverage │          │  p-values · coverage │                                │
│  └──────────┬───────────┘          └──────────┬───────────┘                                │
│             │                                   │                                             │
│             ▼                                   ▼                                             │
│  ┌──────────────────────┐          ┌──────────────────────┐                                │
│  │   Certifier          │          │   Certifier          │                                │
│  │  Sharpe adjustment · │          │  Sharpe adjustment · │                                │
│  │  drawdown bounds     │          │  half-life bounds    │                                │
│  └──────────┬───────────┘          └──────────┬───────────┘                                │
│             │                                   │                                             │
│             └─────────────────┬─────────────────┘                                             │
│                               ▼                                                               │
│                  ┌──────────────────────────┐                                                │
│                  │  Adversarial BEAR Chamber │                                                │
│                  │  · look-ahead bias        │                                                │
│                  │  · lane misclassification │                                                │
│                  │  · data mining / p-hacking │                                                │
│                  │  · economic rationale     │                                                │
│                  └───────────┬──────────────┘                                                │
│                              │                                                                │
│                              ▼                                                                │
│              ┌───────────────────────────────┐                                               │
│              │    Dual-Lane Strategy Registry │                                               │
│              │  Lane S · Lane I · cross-lane  │                                               │
│              │  correlation limits             │                                               │
│              └───────────────┬───────────────┘                                               │
│                              │                                                                │
│                              ▼                                                                │
│              ┌───────────────────────────────┐                                               │
│              │   Allocator + Risk Governor   │                                               │
│              │  regime signal → lane weights │                                               │
│              │  drawdown → capital reduction  │                                               │
│              └───────────────┬───────────────┘                                               │
│                              │                                                                │
│                              ▼                                                                │
│                  ┌──────────────────────────┐                                                │
│                  │  Live Deployment Gate      │                                                │
│                  │  Alpaca paper · lane caps │                                                │
│                  └───────────┬──────────────┘                                                │
│                              │                                                                │
│                              ▼                                                                │
│                  ┌──────────────────────────┐                                                │
│                  │  Monitoring + Reflection │                                                │
│                  │  coverage drift · alpha  │                                                │
│                  │  decay · auto-retirement │                                                │
│                  └──────────────────────────┘                                                │
│                                                                                               │
│  Public outputs: research report · live dashboard · git-tracked memory files                  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Component responsibilities

| Component | What it does | Input | Output |
|---|---|---|---|
| **Literature Seed Corpus** | Curated list of seminal quant papers and factor ideas | arXiv q-fin, SSRN, JFQA abstracts | Seed hypotheses tagged for Lane S or Lane I |
| **Hypothesis Generator** | Combines seed factors and LLM-driven ideas into testable signals; tags lane | Seed corpus + data schema | Candidate signal specifications (formula + parameters + rationale + lane) |
| **Data Laboratory** | Builds clean, point-in-time datasets with costs and bias guards, **separate Lane S/Lane I tables** | Raw free APIs | `lane_s_features.parquet`, `lane_i_features.parquet`, `returns.parquet`, `metadata.json` |
| **Backtest Engine** | Runs walk-forward and purged k-fold validation per lane | Dataset + candidate signals | Per-lane, per-strategy return series, IC, turnover, Sharpe, drawdown |
| **Conformal Validator** | Computes conformal p-values and coverage tests **per lane** | Backtest predictions + hold-out labels | Per-lane p-values, prediction sets, coverage flags |
| **Certifier** | Adjusts Sharpe, bounds drawdown/half-life, stress-tests regimes or events | Backtest stats + conformal outputs | Certified strategy dossier with lane tag |
| **Adversarial Debate Chamber** | BEAR agent attacks every candidate for bias, robustness, rationale, **and correct lane classification** | Candidate dossier | Challenge report + pass/fail verdict |
| **Strategy Registry** | Tracks certified candidates per lane, ranks by adjusted edge, enforces cross-lane correlation cap | Certified dossiers | Dual-lane ranked strategy list with risk budgets |
| **Allocator + Risk Governor** | Sets lane weights by regime, adjusts for drawdown and coverage drift | Strategy registry + HMM regime + live P&L | Capital allocation per lane and per strategy |
| **Live Deployment Gate** | Executes paper trades on Alpaca with lane-specific safety rules | Top-k strategies per lane | Order log + position updates + git commits |
| **Monitoring + Reflection** | Tracks live performance per lane, retires failing strategies, updates memory | Live P&L + market data | Updated registry + research log + dashboard |

### 5.2 Dual-Lane architecture (Lane S + Lane I)

The single most important design decision in AQRA is to **never let a fast informational strategy contaminate the certification of a slow structural strategy**, and vice versa. Each lane has its own data feeds, holding periods, rebalancing cadence, conformal calibration window, and risk budget.

#### Lane S — Structural Alpha

**Philosophy:** Harvest persistent risk premia and behavioral/institutional frictions that decay slowly.

| Attribute | Lane S setting |
|---|---|
| **Holding period** | 1 week – 3 months |
| **Rebalancing** | Weekly to monthly |
| **Target turnover** | ≤ 100% annualized |
| **Calibration window** | 10+ years, multiple regimes |
| **Certification metric** | Regime-conditional Sharpe, FDR-adjusted p-value, max drawdown bound |
| **Kill trigger** | Coverage breaks for 2+ consecutive months or 20% drawdown |
| **Capital budget** | 60–70% of paper portfolio |

**Candidate signal families:**
- Cross-sectional momentum (12-1 month Jegadeesh-Titman)
- Value (P/E, P/B, EV/EBITDA quintiles)
- Quality (Piotroski F-score, gross margin stability, accruals)
- Low volatility / low beta
- Insider conviction (EDGAR Form 4 clusters)
- Macro regime rotation (HMM on VIX, yields, spreads)

#### Lane I — Informational Alpha

**Philosophy:** Exploit short-lived information events before they are fully priced.

| Attribute | Lane I setting |
|---|---|
| **Holding period** | 1 day – 1 week |
| **Rebalancing** | Daily or intraday event trigger |
| **Target turnover** | 500–2000% annualized |
| **Calibration window** | 2–4 years recent history |
| **Certification metric** | Event-study abnormal return, half-life of signal, coverage on next-day return |
| **Kill trigger** | Half-life < 1 day, coverage breaks for 1 week, or 10% lane drawdown |
| **Capital budget** | 30–40% of paper portfolio |

**Candidate signal families:**
- Earnings-announcement drift + surprise signals
- News/social sentiment shocks (RSS + FinBERT)
- Overnight gap reversals / continuation
- Short-term volume-profile anomalies
- Insider Form 4 filing clusters near events

#### Cross-lane guardrails

- **Correlation cap:** Lane S and Lane I portfolios must have absolute cross-lane correlation ≤ 0.5 on a rolling 60-day basis.
- **Independent certification:** A strategy failing in Lane I cannot be rebranded as Lane S to escape stricter turnover tests.
- **Shared BEAR chamber:** The BEAR agent receives both lane definitions and must argue whether a candidate is correctly classified.
- **Regime-aware allocator:** Macro regime signal shifts capital between Lane S and Lane I. For example, high-volatility Bear regimes may reduce Lane I budget because fast signals become noisier.

### 5.3 Allocator + Risk Governor

The allocator is **not** a strategy itself; it is a meta-rule that changes capital weights across lanes and strategies:

1. **Lane weights:** Set monthly by HMM regime classification (Risk-On, Late-Cycle, Bear, Recovery).
2. **Within-lane weights:** Proportional to certified risk-adjusted edge, with a risk-parity floor so no single strategy dominates.
3. **Drawdown governor:** If total portfolio drawdown exceeds 15%, reduce Lane I budget by 50% and pause any Lane I strategy with negative live edge.
4. **Coverage governor:** If any strategy's live prediction-interval coverage falls below 80%, its weight is reduced to zero until recertification.

## 6. Data sources for Phase 1

| Source | Data | Cost | Lane | Use |
|---|---|---|---|---|
| **yfinance** | Daily OHLCV, fundamentals, news | Free | Both | Primary price + fallback fundamentals |
| **FRED** | Macro series (VIX, yields, spreads, CPI, PMI, unemployment) | Free | Lane S | Regime detection + structural overlays |
| **EDGAR SEC Form 4** | Insider transactions | Free | Both | Insider conviction; Lane I near events |
| **EDGAR 10-K/10-Q XBRL** | Accruals, ownership changes | Free | Lane S | Quality factor + ownership signals |
| **Finnhub** | Candles + news | Free tier | Both | Technical indicators + sentiment fallback |
| **FMP free tier** | Profile + key metrics (limited calls) | Free | Lane S | Fundamentals fallback |
| **Polygon.io free tier** | Real-time aggregates, historical bars | Free (5 calls/min) | Lane I | Better OHLCV for short-term signals |
| **Alpha Vantage** | Fundamentals, forex, crypto | 25 calls/day | Lane S | Additional fundamentals |
| **RSS + FinBERT** | News sentiment | Free | Lane I | Sentiment shock signal without paid APIs |
| **Earnings calendars (FMP/yfinance)** | Announcement dates, EPS estimates | Free tier | Lane I | Earnings drift signals |
| **Wikipedia historical S&P 500 lists** | Constituent changes | Free | Both | Survivorship-bias-free universe |

All data will be cached in a local DuckDB database with versioned snapshots, so results are reproducible. Lane S and Lane I will use separate feature tables with explicit lag and look-ahead guards.

## 7. Validation strategy

### 7.1 Lane S internal validation

- **Known-factor reproduction:** AQRA must rediscover momentum, value, and quality effects with the correct signs and approximate magnitudes. If it cannot, the pipeline is broken.
- **Placebo test:** Randomly shuffled labels should produce zero certified Lane S strategies.
- **Regime-stress test:** Evaluate each certified Lane S strategy separately in Bear (2008, 2020, 2022) and Recovery regimes.
- **Transaction-cost sensitivity:** Report results at 0 bps, 10 bps, 20 bps, and 50 bps round-trip costs.

### 7.2 Lane I internal validation

- **Event-study benchmark:** Each candidate must produce positive mean abnormal return around the trigger event on a hold-out event sample.
- **Half-life test:** Signal rank correlation must decay with a measurable half-life > 2 trading days; if it does not, the signal is noise.
- **Placebo test:** Random event dates should produce zero certified Lane I strategies.
- **Transaction-cost sensitivity:** Lane I is especially cost-sensitive; report at 0 bps, 5 bps, 10 bps, 20 bps round-trip.

### 7.3 Conformal validation (both lanes)

- Build conformal prediction intervals for each candidate strategy's next-period return, **calibrated separately per lane** because the return distributions differ.
- Test marginal coverage on a hold-out period disjoint from calibration.
- Report empirical coverage vs. nominal coverage (target: 90%).
- Use conformal p-values + Benjamini–Yekutieli to control FDR **within each lane**.

### 7.4 Live validation

- Deploy **top-2 Lane S + top-2 Lane I** strategies on Alpaca paper for a minimum of **90 trading days**.
- Compare live portfolio to SPY, report alpha, Sharpe, max drawdown, hit rate, and IC.
- Report **lane-attributed P&L** separately so we can verify that Lane I is not subsidizing Lane S or vice versa.
- If coverage or FDR guarantees break in live data, retire the strategy and log the failure.

## 8. Risk and safety design

| Risk | Mitigation |
|---|---|
| Data mining / p-hacking | Conformal p-values + multiple-testing correction + placebo tests, **per lane** |
| Look-ahead bias | Point-in-time data construction with explicit lag rules per lane |
| Lane contamination | Separate feature tables, separate calibration, BEAR lane-classification challenge |
| Survivorship bias | Use historical constituent lists (Wikipedia + yfinance delisted history) |
| Overfitting | Purged k-fold cross-validation + regime/event-stratified splits |
| Fast-lane overtrading / cost blowup | Lane I turnover cap + transaction-cost sensitivity up to 20 bps |
| Live capital loss | Paper trading only; per-strategy capital cap; daily loss limit; kill switch |
| LLM hallucination in hypothesis generation | BEAR agent + metric reconciliation + all signals must be numerically expressible |
| API rate limits | Tiered fallback chain + local cache + retry with backoff |
| Model drift | Continuous coverage monitoring; auto-retire if coverage breaks |

## 9. Success metrics

| Metric | Phase 1 target | How measured |
|---|---|---|
| **Combined / system-level** | | |
| Certified strategies | ≥ 2 Lane S + ≥ 2 Lane I, cross-lane correlation ≤ 0.5 | Registry + dossiers |
| Live portfolio Sharpe | ≥ 0.8 (paper) | Alpaca P&L vs. T-bill rate |
| Live alpha vs. SPY | Positive at 90-day horizon | Regression on SPY excess returns |
| Max drawdown | ≤ 20% | Alpaca portfolio equity curve |
| Reproducibility | Full pipeline reruns from a single command | `make reproduce` |
| **Lane S — Structural Alpha** | | |
| Known-factor reproduction | Sign + significance on momentum, value, quality | Internal backtest |
| Regime-conditional Sharpe | ≥ 0.6 in at least 3 of 4 regimes | Regime-stratified backtest |
| Turnover | ≤ 100% annualized | Trade count × avg position size |
| Conformal coverage | 85–95% empirical coverage on hold-out | Coverage test |
| FDR control | ≤ 20% estimated false discoveries among selected | BY correction within Lane S |
| **Lane I — Informational Alpha** | | |
| Event-study abnormal return | Positive mean abnormal return on hold-out events | Event-study t-test |
| Signal half-life | ≥ 2 trading days | Rank autocorrelation decay fit |
| Turnover | 500–2000% annualized | Trade count × avg position size |
| Conformal coverage | 85–95% empirical coverage on next-period return | Coverage test |
| FDR control | ≤ 20% estimated false discoveries among selected | BY correction within Lane I |
| Hit rate | ≥ 55% | Percentage of positive trades |
| Information coefficient (IC) | ≥ 0.03 | Spearman rank correlation |
| Cost-adjusted edge | Positive at ≥ 10 bps round-trip | Backtest with transaction costs |

## 10. Public outputs

1. **Open-source repository** with full code, data pipeline, backtest engine, and certification logic.
2. **Research paper / report** titled *AQRA: An Autonomous Conformal Agent for Quantitative Strategy Discovery* targeting arXiv q-fin.PM or Quantitative Finance journal.
3. **Live dashboard** showing certified strategies, paper portfolio P&L, coverage diagnostics, and audit log.
4. **Git-tracked memory files** similar to the Alpaca agent: daily summaries, strategy registry, research log.

## 11. Roadmap beyond Phase 1

- **Phase 2:** Lane portability — add India (NSE 500) using NSE Bhavcopy + RBI macro; test whether certified Lane S and Lane I signals transfer across markets.
- **Phase 3:** Symbolic discovery — genetic-programming symbolic regression for truly novel signal discovery, with strict BEAR vetting.
- **Phase 4:** New asset classes — options (implied-vol signals) and crypto (24/7 Lane I), plus microstructure signals from Polygon/TAQ.
- **Phase 5:** Reviewer community — multi-agent peer-review where strategies must survive independent specialist agents (not only BEAR).
- **Phase 6:** Meta-learning allocator — learn the lane-weight policy itself under conformal regret bounds.

---

## 12. Open questions

1. Should Phase 1 use a fixed literature seed corpus, or should it actively scrape arXiv/SSRN?
2. What is the initial capital for the paper-trading portfolio? ($10,000 suggested)
3. What should the default Lane S / Lane I capital split be? (Suggested: 65% / 35%)
4. Should the system run fully autonomously, or require a human approval gate before live deployment? **(Recommended: human approval gate for Phase 1b, fully autonomous monitoring/reflection only.)**
5. Which multiple-testing correction should be the default? **(Recommended: Benjamini–Yekutieli for arbitrary dependence.)**
6. Should we publish the code immediately, or keep it private until after 90 days of live results? **(Recommended: open-source the methodology and pipeline immediately; publish live results after 90 days.)**
7. For Lane I, what is the maximum acceptable turnover before costs destroy the edge? **(Recommended: 1000% annualized cap.)**

---

*Design prepared for user review. No implementation code has been written yet.*
