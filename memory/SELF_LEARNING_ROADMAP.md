# Self-Learning Architecture Roadmap

**Created:** 2026-04-23

## Phase 1: Feedback Loop (Week 1-2)
- Replace markdown trade log with SQLite (`data/bull_trades.db`)
- Schema: trades, portfolio_snapshots, factor_performance, strategy_variants, regime_history
- Auto post-mortem on every closed trade: factor attribution, regime correctness, max favorable/adverse
- Rolling factor performance tracking (30-day Sharpe, win rate by factor × regime)

## Phase 2: Strategy Evolution (Week 3-4)
- Bayesian optimization of factor weights (Optuna)
- A/B testing framework: champion vs challenger strategy variants
- Regime hysteresis (10pp band + 14-day cooldown) — proven to improve returns
- Regime detector upgrade: multi-signal (VIX + HY spreads + PMI + yield curve) → XGBoost

## Phase 3: ML Enhancement (Month 2)
- XGBoost for factor scoring (needs ~100 trades minimum)
- LSTM for regime detection (needs ~200 days of data)
- Reinforcement learning for position sizing (DQN with portfolio environment)
- Sentiment pipeline: news NLP → sentiment score → factor input

## Phase 4: Multi-Agent Architecture (Month 3)
- Orchestrator agent: coordinates specialists, resolves conflicts
- Macro analyst: regime detection, macro research, news analysis
- Micro analyst: ticker deep-dives, factor scoring, valuation
- Risk manager: drawdown guards, position limits, correlation monitoring, VETO power
- Execution agent: order placement, stop management, fill verification

## Phase 5: Continuous Improvement (Month 4+)
- ATLAS-pattern autoresearch loop: weekly self-evaluation, prompt/weight mutations
- Strategy decay detection: CUSUM + rolling Sharpe + PSI (2/3 vote)
- Correlation monitoring: pairwise >0.7 triggers diversification alarm
- Drawdown guard: 5%/10%/15%/20% thresholds with escalating restrictions

## Key Targets
- **Realistic:** Sharpe 1.0-2.0 (not 100% win rate)
- **Win rate:** 55-60% with positive R:R is superior to 97% win rate with tiny R:R
- **Information edge:** Alternative data, SEC filings NLP, options flow, insider activity

## Critical Architecture Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trade storage | SQLite | SQL analytics, factor attribution, ML training data |
| Weight optimization | Bayesian (Optuna) | 10x fewer evaluations than grid search |
| Regime detection | Multi-signal + XGBoost | VIX alone documented failure |
| Position sizing | Half-Kelly + uncertainty shrinkage | Interpretable; RL learns what Kelly cannot |
| Self-correction | CUSUM + Sharpe + PSI (2/3) | Reduces false alarms |
| Agent architecture | Orchestrator + 4 specialists | FinAgent (NeurIPS 2025) pattern |