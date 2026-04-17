import pytest
import pandas as pd
from src.signal_engine import (
    MacroSnapshot, compute_composite_scores, recommendation_from_score
)

def _make_df(n=5) -> pd.DataFrame:
    """Minimal valid fundamentals DataFrame."""
    import numpy as np
    rng = np.random.RandomState(42)
    return pd.DataFrame({
        "ticker": [f"T{i}" for i in range(n)],
        "gross_profit_margin": rng.uniform(0.1, 0.9, n),
        "accruals_ratio":       rng.uniform(-0.2, 0.2, n),
        "piotroski":            rng.randint(1, 9, n),
        "momentum_raw":         rng.uniform(-0.3, 0.5, n),
        "short_interest_pct":   rng.uniform(0.01, 0.15, n),
        "pe_ttm":               rng.uniform(10, 50, n),
        "pb_ratio":             rng.uniform(1, 8, n),
        "realized_vol_1y":      rng.uniform(0.1, 0.5, n),
    })


class TestCompositeScores:
    def test_returns_dataframe(self):
        df = compute_composite_scores(_make_df(), MacroSnapshot())
        assert isinstance(df, pd.DataFrame)

    def test_adds_composite_score_column(self):
        df = compute_composite_scores(_make_df(), MacroSnapshot())
        assert "composite_score" in df.columns

    def test_composite_score_between_0_and_1(self):
        df = compute_composite_scores(_make_df(20), MacroSnapshot())
        assert df["composite_score"].between(0, 1).all()

    def test_score_1_10_in_range(self):
        df = compute_composite_scores(_make_df(20), MacroSnapshot())
        assert df["score_1_10"].between(1, 10).all()

    def test_sorted_descending(self):
        df = compute_composite_scores(_make_df(10), MacroSnapshot())
        assert list(df["composite_score"]) == sorted(df["composite_score"], reverse=True)

    def test_crash_protection_neutralises_momentum(self):
        macro_crash = MacroSnapshot(spx_return_1m=-0.15, spx_vs_200ma=-0.08)
        df = compute_composite_scores(_make_df(10), macro_crash)
        assert (df["momentum_percentile"] == 0.5).all()

    def test_single_ticker_works(self):
        df = compute_composite_scores(_make_df(1), MacroSnapshot())
        assert len(df) == 1
        assert df["score_1_10"].iloc[0] == 5  # single ticker → median rank → 5


class TestRecommendation:
    def test_strong_buy_at_8_plus(self):
        assert recommendation_from_score(8) == "STRONG BUY"
        assert recommendation_from_score(10) == "STRONG BUY"

    def test_buy_at_6_to_7(self):
        assert recommendation_from_score(6) == "BUY"
        assert recommendation_from_score(7) == "BUY"

    def test_hold_at_4_to_5(self):
        assert recommendation_from_score(4) == "HOLD"
        assert recommendation_from_score(5) == "HOLD"

    def test_sell_at_2_to_3(self):
        assert recommendation_from_score(2) == "SELL"
        assert recommendation_from_score(3) == "SELL"

    def test_strong_sell_at_1(self):
        assert recommendation_from_score(1) == "STRONG SELL"