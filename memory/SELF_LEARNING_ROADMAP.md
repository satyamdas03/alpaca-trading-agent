# Self-Learning Architecture Roadmap

**Created:** 2026-04-23
**Last Updated:** 2026-04-23 (Session 2 — full infrastructure log added)

## Current System Capabilities
- Factor-based strategy: Quality 25%, Momentum 30%, Value 10%, Low Vol 15%, Sentiment 20%
- Regime detection: VIX-based (Risk-On <20, Late Cycle 20-25, Stress >25, Recovery)
- Position sizing: Half-Kelly, max 20% per position, min $500
- Stop management: -7% stop-loss, 10% trailing stop (when applicable)
- Order execution: Alpaca REST API (MCP disconnected, REST fallback working)
- Notifications: Gmail MCP for trade/P&L emails
- Scheduling: CRON jobs (session-only, 7-day expiry)
- State persistence: Markdown memory files (6 files)
- Backtesting: Phase 1 complete (46/46 tests passing)

## Current System Limitations
- No quantitative feedback loop (trades evaluated manually)
- No automated strategy optimization
- No ML models (regime = VIX threshold only, factors = fixed weights)
- No sentiment pipeline (manual WebSearch only)
- No correlation/portfolio optimization
- No structured analytics database
- Memory = manual markdown files (no SQL queries possible)
- CRONs session-only (die when session ends)
- Alpaca MCP unreliable (server crashes, need REST fallback)

---

## Phase 1: Feedback Loop (Week 1-2) — PRIORITY
**Goal:** Close the loop — every trade outcome feeds back into strategy improvement.

### 1.1 SQLite Trade Database
Replace markdown trade log with structured database:

```sql
-- Core trade record
CREATE TABLE trades (
    trade_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,                   -- 'long' or 'short'
    entry_time TEXT NOT NULL,
    exit_time TEXT,
    entry_price REAL NOT NULL,
    exit_price REAL,
    qty REAL NOT NULL,
    pnl REAL,
    pnl_pct REAL,
    exit_reason TEXT,                     -- 'stop_loss','trailing_stop','take_profit','weak_signal','time_exit','manual'
    status TEXT DEFAULT 'open',
    quality_score REAL,
    momentum_score REAL,
    value_score REAL,
    low_vol_score REAL,
    sentiment_score REAL,
    composite_score REAL,
    vix_at_entry REAL,
    regime_at_entry TEXT,
    spx_at_entry REAL,
    vix_at_exit REAL,
    regime_at_exit TEXT,
    spx_at_exit REAL,
    max_favorable REAL,                   -- Max % gain during hold
    max_adverse REAL,                     -- Max % drawdown during hold
    hold_bars INTEGER,
    quality_contribution REAL,
    momentum_contribution REAL,
    value_contribution REAL,
    low_vol_contribution REAL,
    sentiment_contribution REAL,
    order_id TEXT,
    strategy_version TEXT,
    notes TEXT
);

-- Daily portfolio snapshots
CREATE TABLE portfolio_snapshots (
    date TEXT PRIMARY KEY,
    equity REAL NOT NULL,
    cash REAL NOT NULL,
    positions_count INTEGER,
    daily_return REAL,
    cumulative_return REAL,
    vix REAL,
    regime TEXT,
    spx_close REAL,
    spx_return_ytd REAL
);

-- Factor performance tracking (rolling)
CREATE TABLE factor_performance (
    date TEXT NOT NULL,
    factor TEXT NOT NULL,
    regime TEXT NOT NULL,
    rolling_sharpe_30d REAL,
    rolling_win_rate_30d REAL,
    rolling_avg_pnl_30d REAL,
    trade_count_30d INTEGER,
    PRIMARY KEY (date, factor, regime)
);

-- Strategy variant tracking (for A/B testing)
CREATE TABLE strategy_variants (
    variant_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    weights_json TEXT NOT NULL,
    regime_shifts_json TEXT,
    created_date TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    rolling_sharpe REAL,
    rolling_win_rate REAL,
    trade_count INTEGER DEFAULT 0,
    total_pnl REAL DEFAULT 0
);

-- Regime history for backtesting regime detector
CREATE TABLE regime_history (
    date TEXT PRIMARY KEY,
    vix REAL,
    detected_regime TEXT,
    actual_regime TEXT,                   -- Retrospectively labeled
    confidence REAL,
    notes TEXT
);
```

**File:** `data/bull_trades.db` (gitignored, backed up separately)

### 1.2 Automated Trade Post-Mortem
When a trade closes, compute:
- Factor attribution: which factors predicted the outcome?
- Regime correctness: was the regime call right?
- Max favorable/excursion: how far did it go right/wrong?
- Hold time vs. expected hold time
- Exit quality: was stop-loss hit or did we exit on signal?

### 1.3 Rolling Factor Performance
Track 30-day rolling metrics per factor × regime:
- Sharpe ratio
- Win rate
- Average P&L
- Trade count
→ This is what enables strategy evolution in Phase 2

---

## Phase 2: Strategy Evolution (Week 3-4)
**Goal:** Optimize factor weights and regime detection automatically.

### 2.1 Bayesian Weight Optimization (Optuna)
- Objective: maximize Sharpe ratio of composite score on walk-forward validation
- Search space: 5 factor weights (Quality, Momentum, Value, Low Vol, Sentiment) summing to 1.0
- Constraints: each weight 0.05-0.50
- Evaluation: walk-forward on last 252 trading days
- Run weekly, keep champion variant unless challenger beats by >0.1 Sharpe

### 2.2 A/B Testing Framework
- Champion: current strategy (fixed weights from STRATEGY.md)
- Challenger: optimized weights from Optuna
- Paper-trade both in parallel for 2 weeks
- Promote challenger only if Sharpe improvement >0.1 with p<0.05

### 2.3 Regime Detection Upgrade
**Current:** VIX thresholds only (3 bands: <20, 20-25, >25)
**Target:** Multi-signal classifier
- VIX (volatility)
- HY spreads (credit risk)
- PMI (economic cycle)
- Yield curve slope (recession signal)
- Put/call ratio (sentiment)
- Correlation index (stress measure)

Hysteresis: 10pp band + 14-day cooldown before regime switches (proven to improve returns, reduces transitions 132→36)

### 2.4 Regime Hysteresis
- Current: Hard VIX thresholds cause whipsaws
- Fix: Add 10pp buffer band + 14-day minimum regime duration
- Result: Reduces regime transitions from 132→36, turns -12% to +28% (Hermoso 2026)

---

## Phase 3: ML Enhancement (Month 2)
**Goal:** Replace hardcoded rules with learned models.

### 3.1 XGBoost Factor Scoring
- Input: fundamental data (margins, growth, quality) + technical (momentum, volatility)
- Output: composite score (0-1) per stock
- Training data: ~100 trades minimum (need 2-3 months of live trading)
- Walk-forward validation with expanding window

### 3.2 LSTM Regime Detection
- Input: daily VIX, HY spreads, PMI, yield curve, correlation
- Output: regime probability distribution
- Needs ~200 days of data
- 2-layer LSTM, 64 hidden units, dropout 0.3
- Retrain monthly

### 3.3 RL Position Sizing (DQN)
- State: current portfolio, regime, factor scores, volatility
- Action: position size (0%, 5%, 10%, 15%, 20%)
- Reward: Sharpe ratio of resulting portfolio
- Environment: Alpaca paper trading with 1-day episodes
- Start with half-Kelly as baseline, let RL improve on it

### 3.4 Sentiment Pipeline
- News NLP: classify headlines as positive/negative/neutral per stock
- SEC filing NLP: extract risk factors, forward-looking statements
- Options flow: unusual activity detection
- Insider activity: cluster buys/sells
- Output: sentiment_score (0-1) per stock, fed into factor composite

---

## Phase 4: Multi-Agent Architecture (Month 3)
**Goal:** Specialist agents coordinated by orchestrator.

### 4.1 Orchestrator Agent
- Receives routine trigger (pre-market, midday, close)
- Dispatches tasks to specialists
- Resolves conflicts (e.g., macro says Risk-On, micro says sell)
- Makes final trade decisions
- Based on FinAgent (NeurIPS 2025) pattern

### 4.2 Macro Analyst Agent
- Regime detection (multi-signal)
- Macro research (Fed, GDP, CPI, employment)
- News analysis (geopolitics, earnings calendar)
- Output: regime + confidence + macro thesis

### 4.3 Micro Analyst Agent
- Ticker deep-dives (factor scoring, valuation)
- Earnings analysis
- Technical analysis (support/resistance, volume)
- Output: buy/sell/hold per ticker with score

### 4.4 Risk Manager Agent
- Drawdown guard (5%/10%/15%/20% thresholds)
- Position limits (max per sector, max per stock)
- Correlation monitoring (pairwise >0.7 trigger)
- **VETO POWER**: can override any trade decision
- Output: approved trades + risk parameters

### 4.5 Execution Agent
- Order placement (market, limit, stop, trailing)
- Fill verification
- Stop management
- Slippage monitoring
- Output: fill confirmations + execution quality metrics

---

## Phase 5: Continuous Improvement (Month 4+)
**Goal:** System improves itself without human intervention.

### 5.1 ATLAS-Pattern Autoresearch Loop
- Weekly self-evaluation: run backtest, compute metrics, compare to baseline
- Prompt/weight mutations: randomly perturb strategy parameters
- Keep improvements, revert regressions
- Based on ATLAS GIC: +22% improvement in 173 days

### 5.2 Strategy Decay Detection
Three independent tests, alert when 2/3 agree:
1. Rolling 60-day Sharpe vs. baseline
2. CUSUM on excess returns (detects sudden breaks)
3. PSI (Population Stability Index) on return distribution (>0.25 = significant shift)

Alert levels:
- GREEN: Sharpe > 0.5 — normal operations
- YELLOW: Sharpe 0.0-0.5 — reduce position sizes 50%
- ORANGE: Sharpe -0.5-0.0 — no new trades, paper-trade variants
- RED: Sharpe < -0.5 — close all, enter diagnostic mode

### 5.3 Correlation Monitoring
- Compute pairwise correlation between positions weekly
- If any pair >0.7, flag diversification alarm
- In stress, correlations converge to 1 — reduce concentration
- Monitor sector concentration (max 30% in any sector)

### 5.4 Drawdown Guard (Tiered)
| Drawdown | Action |
|----------|--------|
| >5% | Reduce all new positions to 50% of computed size |
| >10% | No new positions; tighten stops to -4% |
| >15% | Close 50% of all positions at next open |
| >20% | Close ALL positions; cash-only for 5 days |

Recovery from >20% drawdown requires:
- 5 consecutive trading days in cash
- Regime confidence > 0.7
- Manual override (email confirmation)

---

## Key Targets (Realistic)
- **Sharpe 1.0-2.0** (not 100% win rate)
- **Win rate 55-60%** with positive R:R (superior to 97% win rate with tiny R:R)
- **Information edge:** Alternative data, SEC filings NLP, options flow, insider activity
- **Maximum drawdown:** <15% (with drawdown guard)

**Why "100% accuracy" is impossible:**
- Markets are adversarial — other participants exploit patterns
- Black swan events create losses regardless of signal quality
- The goal is EDGE (consistently positive EV), not perfection
- Sharpe 2.0 over 252 days = elite performance (top 1% of funds)
- Balea (2025): 97% win rate strategy earned $0.027/trade vs 73% win rate strategy earning real returns

---

## Critical Architecture Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trade storage | SQLite | SQL analytics, factor attribution, ML training data |
| Weight optimization | Bayesian (Optuna) | 10x fewer evaluations than grid search |
| Regime detection | Multi-signal + XGBoost | VIX alone documented failure (LESSONS_LEARNED #11) |
| Position sizing | Half-Kelly + uncertainty shrinkage, then RL | Interpretable; RL learns what Kelly cannot |
| Self-correction | CUSUM + Sharpe + PSI (2/3 vote) | Reduces false alarms |
| Agent architecture | Orchestrator + 4 specialists | FinAgent (NeurIPS 2025) pattern; risk agent has veto |
| Improvement mechanism | ATLAS autoresearch loop | +22% in 173 days from prompt/weight mutations |
| ML models | XGBoost first, LSTM second, RL third | Tree models need less data; LSTM needs sequences; RL needs episodes |
| Correlation monitoring | Pairwise >0.7 trigger | Correlations converge to 1 in stress; diversification benefit evaporates |
| Regime hysteresis | 10pp band + 14-day cooldown | Hermoso (2026): reduces transitions 132→36, turns -12% to +28% |
| Accuracy target | Sharpe 1.0-2.0, not high win rate | Balea (2025): 97% win rate with $0.027/trade < 73% win rate with real R:R |

---

## Research Sources
- [ATLAS GIC - Self-Improving Multi-Agent Trading](https://github.com/chrisworrey55/atlas-gic)
- [AlphaLoop - Self-Improving Trading with RL Feedback](https://github.com/Mithil-hub/AlphaLoop-Self-Improving-Multi-Agent-Trading-System-with-RL-Feedback)
- [FinAgent Orchestration Framework (NeurIPS 2025)](https://arxiv.org/html/2512.02227v1)
- [TradingAgents - Multi-Agent LLM Framework (AAAI 2025)](https://openreview.net/pdf/bf4d31f6b4162b5b1618ab5db04a32aec0bcbc25.pdf)
- [AlphaQuanter - Agentic RL Framework](https://arxiv.org/html/2510.14264v1)
- [MRA-AGRU - Dynamic Factor Gating with Regime Awareness (2026)](https://www.preprints.org/manuscript/202603.2262/v1)
- [Allocation-Focused Regime Detection with XGBoost](https://github.com/nxd914/allocation-focused-regime)
- [ML Stock Trading Engine (Full Pipeline)](https://github.com/earosenfeld/ml-stock-trading-engine)
- [Basket Trading with Bayesian Optimization](https://github.com/digantk31/Basket-Trading)
- [Bayesian Optimization of Trading Strategies - Practical Guide](https://xglamdring.com/optimizing-trading-strategies-with-bayesian-algorithms-a-practical-guide/)
- [RL Kelly Strategy (Jiang et al. 2022)](https://uwspace.uwaterloo.ca/items/32729fb4-fa94-4185-86fb-45de19d0e590)
- [Kelly Criterion in Portfolio Management](https://stockalpha.ai/alpha-learning/kelly-criterion-in-portfolio-management-growth-optimal-sizing-of-investments)
- [Kelly Criterion for Autonomous Agents](https://agentbets.ai/guides/kelly-criterion-bet-sizing/)
- [Regime Change Detection - StratBase](https://stratbase.ai/en/blog/regime-change-detection)
- [CUSUM, Bayes, and Knowing When to Quit](https://kniyer.substack.com/p/detecting-decay-in-real-time-when)
- [Concept Drift Alarms for Quant Signals](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-when-alpha-decays)
- [Trading Edge Decay Playbook](https://finaur.com/blog/en/education/trading-edge-decay-playbook/)
- [Adaptive Regime-Detecting Grid Bot (Hermoso 2026)](https://medium.com/@leoohermoso/from-static-to-adaptive-building-a-regime-detecting-grid-liquidity-bot-that-earned-28-over-2-39369dd73b19)
- [Maximal Attainable Sharpe Ratio (Chen and Poti 2024)](https://www.sciencedirect.com/science/article/pii/S0165176524000156)
- [Sharpe Is About Discipline (Salvato)](https://www.alessandrosalvato.com/post/sharpe-is-about-discipline)
- [QuanterSwarm - Multi-Agent with Routed Activation](https://github.com/supremewen666/QuanterSwarm-demo)