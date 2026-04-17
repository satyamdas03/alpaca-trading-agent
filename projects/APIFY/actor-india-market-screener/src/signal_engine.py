"""
Self-contained signal engine ported from NeuralQuant nq_signals package.
Computes 5-factor composite scores cross-sectionally. No external package dependency.
"""
from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

SHORT_INT_WEIGHT = 0.15
REGIME_BUDGET = 1.0 - SHORT_INT_WEIGHT  # 0.85


@dataclass
class MacroSnapshot:
    vix: float = 18.0
    spx_vs_200ma: float = 0.02
    spx_return_1m: float = 0.01
    yield_spread_2y10y: float = 0.10
    hy_spread_oas: float = 350.0
    ism_pmi: float = 51.0
    cpi_yoy: float = 3.0
    fed_funds_rate: float = 5.25
    yield_10y: float = 4.2
    yield_2y: float = 4.1
    fred_sourced: bool = False


def _regime_weights(macro: MacroSnapshot) -> dict[str, float]:
    """Simplified regime detection — returns factor weights without fitted HMM."""
    bear = (
        macro.vix > 30
        or macro.spx_return_1m < -0.10
        or macro.hy_spread_oas > 600
        or macro.spx_vs_200ma < -0.05
    )
    recovery = macro.spx_vs_200ma < -0.02 and macro.spx_return_1m > 0.02
    late_cycle = macro.yield_spread_2y10y < 0 and macro.hy_spread_oas > 400

    if bear:
        return {"quality": 0.40, "momentum": 0.10, "value": 0.25, "low_vol": 0.25}
    if recovery:
        return {"quality": 0.20, "momentum": 0.35, "value": 0.25, "low_vol": 0.20}
    if late_cycle:
        return {"quality": 0.35, "momentum": 0.20, "value": 0.25, "low_vol": 0.20}
    # Risk-On (default)
    return {"quality": 0.25, "momentum": 0.30, "value": 0.20, "low_vol": 0.25}


def _rank(series: pd.Series, ascending: bool = True) -> pd.Series:
    return series.rank(pct=True, ascending=ascending, na_option="keep").fillna(0.5)


def compute_composite_scores(fundamentals: pd.DataFrame, macro: MacroSnapshot) -> pd.DataFrame:
    """
    Full signal pipeline. Input df must have columns:
    ticker, gross_profit_margin, accruals_ratio, piotroski,
    momentum_raw, short_interest_pct, pe_ttm, pb_ratio, realized_vol_1y
    Returns df sorted by composite_score desc, with added signal columns.
    """
    df = fundamentals.copy()
    crash_flag = macro.spx_return_1m < -0.10 or macro.spx_vs_200ma < -0.05
    w = _regime_weights(macro)

    # Quality: gross margin (40%) + accruals inverse (35%) + piotroski (25%)
    df["quality_percentile"] = (
        _rank(df["gross_profit_margin"]) * 0.40
        + _rank(df["accruals_ratio"], ascending=False) * 0.35
        + _rank(df["piotroski"]) * 0.25
    )

    # Momentum: crash-protected 12-1 month return percentile
    df["momentum_percentile"] = (
        pd.Series(0.5, index=df.index)
        if crash_flag
        else _rank(df["momentum_raw"])
    )

    # Value: inverse of (PE rank 50% + PB rank 50%) — cheaper is better
    df["value_percentile"] = 1.0 - (
        _rank(df["pe_ttm"]) * 0.50 + _rank(df["pb_ratio"]) * 0.50
    )

    # Low-Vol: inverse realized vol rank
    df["low_vol_percentile"] = 1.0 - _rank(df["realized_vol_1y"])

    # Short Interest: inverse rank — lower SI is better
    df["short_interest_percentile"] = 1.0 - _rank(df["short_interest_pct"])

    # Composite (weights sum to 1.0)
    df["composite_score"] = (
        df["quality_percentile"]       * w["quality"]   * REGIME_BUDGET
        + df["momentum_percentile"]    * w["momentum"]  * REGIME_BUDGET
        + df["short_interest_percentile"] * SHORT_INT_WEIGHT
        + df["value_percentile"]       * w["value"]     * REGIME_BUDGET
        + df["low_vol_percentile"]     * w["low_vol"]   * REGIME_BUDGET
    )

    # Rank-based 1-10 score
    if len(df) == 1:
        df["score_1_10"] = 5  # single ticker → neutral
    else:
        pct = df["composite_score"].rank(pct=True, method="average")
        df["score_1_10"] = (pct * 9 + 1).round().clip(1, 10).astype(int)

    return df.sort_values("composite_score", ascending=False).reset_index(drop=True)


def recommendation_from_score(score_1_10: int) -> str:
    if score_1_10 >= 8:
        return "STRONG BUY"
    if score_1_10 >= 6:
        return "BUY"
    if score_1_10 >= 4:
        return "HOLD"
    if score_1_10 >= 2:
        return "SELL"
    return "STRONG SELL"