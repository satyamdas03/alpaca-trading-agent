: "# AQRA: Autonomous Quant Research Agent — Dual-Lane Conformal Strategy Discovery"
description: "Research paper skeleton for AQRA, a theorem-backed autonomous quant research system with dual-lane architecture, conformal certification, and adversarial review."

---

# AQRA: Autonomous Quant Research Agent
## Dual-Lane Conformal Strategy Discovery with Adversarial Review

**Authors:** Satyam Das
**Date:** 2026-06-24

---

## Abstract

We introduce AQRA, an autonomous quantitative-research agent that discovers, certifies, and deploys equity-trading strategies under explicit non-spuriousness guarantees. AQRA separates structural alpha (Lane S) from informational alpha (Lane I), calibrates conformal prediction intervals per lane, controls false-discovery rate via the Benjamini–Yekutieli procedure, and subjects every candidate to an adversarial BEAR (Bias, Edge, Adversarial Review) chamber. The system runs live on Alpaca paper trading. Phase 1 focuses on the S&P 500 using free data sources. We report preliminary backtest metrics and outline a 90-day live validation experiment.

---

## 1. Introduction

Quantitative strategy research is plagued by three failure modes:
1. **Human bias** — researchers favor signals that confirm prior beliefs.
2. **Multiple-testing abuse** — hundreds of candidates are tested and the best are reported as if they were pre-specified.
3. **Look-ahead leakage** — point-in-time availability of fundamentals, insider filings, and news is routinely ignored.

AQRA addresses these by automating the research loop and wrapping each candidate in statistical safeguards:
- **Dual-lane architecture** separates slow-moving structural factors from fast informational signals.
- **Conformal validation** provides finite-sample coverage guarantees for predicted returns.
- **BEAR chamber** is an adversarial LLM/human-in-the-loop reviewer that hunts for bias, mining, and misclassification.
- **Live deployment gate** enforces paper-only trading, drawdown limits, and daily loss controls.

---

## 2. Related Work

- **PARA-DEBATE** and multi-agent critique loops for AI research.
- **Conformal prediction** (Vovk, Gammerman, Shafer; Angelopoulos et al.) for distribution-free uncertainty quantification.
- **False discovery rate control** (Benjamini & Yekutieli 2001) under arbitrary dependence.
- **Backtesting best practices** (Lopez de Prado 2018) — purged cross-validation, embargo periods, turnover accounting.
- **Known equity factors** — Jegadeesh & Titman momentum, Fama-French value, Piotroski quality.

---

## 3. Methodology

### 3.1 Dual-Lane Architecture

| Lane | Sources | Holding horizon | Examples |
|------|---------|-----------------|----------|
| Lane S — Structural | Prices, fundamentals, macro | 1–3 months | 12-1 momentum, value composite, quality score |
| Lane I — Informational | Prices, news, earnings, insider | 1 day–1 week | overnight gap, volume spike, sentiment shock |

Each lane has independent feature tables, independent conformal calibration, and independent backtest engines.

### 3.2 Signal Generation

Signal candidates are human-readable formulas with lane tags and parameter sets. The initial libraries contain:
- Lane S: S_MOM_12_1, S_VALUE, S_QUALITY
- Lane I: I_GAP, I_VOLUME, I_SENTIMENT

### 3.3 Conformal Certification

For each candidate we:
1. Run a walk-forward backtest with purged k-fold splits.
2. Compute predicted and realized returns on a hold-out calibration set.
3. Build conformal prediction intervals and compute p-values for the null of zero edge.
4. Apply BY FDR control across all candidates within the lane.

### 3.4 BEAR Adversarial Chamber

BEAR critiques each surviving candidate on:
1. Look-ahead bias
2. Data mining / spurious fit
3. Lane misclassification
4. Economic rationale
5. Robustness to excluding the last two years

Only candidates that pass BEAR receive a `CERTIFIED` dossier.

### 3.5 Allocation and Risk Governor

Capital is split between Lane S and Lane I. A regime-aware allocator adjusts the split:
- Risk-On: 55% / 45%
- Risk-Off: 75% / 25%
- Bear: 85% / 15%

Within each lane, capital is allocated by risk parity (proportional to Sharpe, capped at 50% of lane budget). The deployment gate blocks live trading if Alpaca keys are missing or if the daily loss limit / max drawdown is breached.

---

## 4. Data

Phase 1 uses free-tier data:
- Prices: yfinance
- Macro: FRED (VIX, yield spreads)
- Fundamentals / insider: EDGAR Form 4, XBRL, FMP
- News / sentiment: RSS + FinBERT, Finnhub
- Aggregates: Polygon

Universe: current S&P 500 constituents (acknowledged survivorship bias; Phase 2 will use historical constituent lists).

---

## 5. Empirical Results (Placeholder)

### 5.1 Known-Factor Reproduction

| Signal | Mean IC | Sharpe | Max Drawdown |
|--------|---------|--------|--------------|
| S_MOM_12_1 | TBD | TBD | TBD |
| S_VALUE | TBD | TBD | TBD |
| S_QUALITY | TBD | TBD | TBD |
| I_GAP | TBD | TBD | TBD |
| I_VOLUME | TBD | TBD | TBD |
| I_SENTIMENT | TBD | TBD | TBD |

### 5.2 Conformal Coverage

Coverage of 90% prediction intervals on the test set: **TBD**.

### 5.3 FDR Selection

Number of candidates tested per lane, number selected by BY procedure, number certified after BEAR: **TBD**.

---

## 6. Live Trading Experiment

AQRA will be run on Alpaca paper trading for 90 days. Metrics recorded daily:
- Portfolio value and day P&L
- Per-strategy P&L and turnover
- Conformal coverage over rolling 30-day window
- Number of strategies retired by the monitor

---

## 7. Limitations and Future Work

1. Phase 1 uses the current S&P 500 universe, inducing survivorship bias.
2. Fundamental data in Phase 1 is placeholder-only; full integration is Phase 2.
3. BEAR LLM review depends on Anthropic API availability and prompt robustness.
4. Transaction-cost model is a flat bps assumption; execution slippage is not modeled.
5. Regime detection is manual in Phase 1; Phase 2 will use an HMM-based detector.

---

## 8. Conclusion

AQRA demonstrates a principled, automated pipeline for quantitative strategy discovery that combines conformal non-spuriousness guarantees, adversarial review, and live paper-trading validation. The dual-lane design explicitly addresses market non-stationarity by certifying fixed strategy families per lane and adaptively allocating capital between them. We will report full live-trading results after the 90-day experiment.

---

## References

- Benjamini, Y., & Yekutieli, D. (2001). The control of the false discovery rate in multiple testing under dependency. *Annals of Statistics*.
- Angelopoulos, A. N., & Bates, S. (2021). A gentle introduction to conformal prediction and distribution-free uncertainty quantification. *arXiv*.
- Lopez de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.
- Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*.

---

## Appendix: AQRA Commands

```bash
uv sync --extra dev
aqra ingest --start 2020-01-01 --end 2024-12-31
aqra certify
aqra deploy --dry-run
aqra monitor
```
