import numpy as np
import pandas as pd
import pytest

from aqra.signals.dsl import (
    LANE_S_FEATURES, evaluate, formula, validate,
)


def _frame(n_tickers=6, n_days=40, seed=3):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    rows = []
    for i in range(n_tickers):
        rows.append(pd.DataFrame({
            "ticker": f"T{i}",
            "date": dates,
            "mom_12_1": rng.normal(0, 1, n_days),
            "quality_score": rng.uniform(0, 1, n_days),
        }))
    return pd.concat(rows, ignore_index=True)


VALID = {"op": "rank", "arg": {"feature": "mom_12_1"}}


def test_valid_ast_passes():
    assert validate(VALID, LANE_S_FEATURES) == []


def test_rejects_non_whitelisted_feature():
    ast = {"op": "rank", "arg": {"feature": "next_day_return"}}
    assert any("not whitelisted" in e for e in validate(ast, LANE_S_FEATURES))


def test_rejects_unknown_op():
    ast = {"op": "eval", "arg": {"feature": "mom_12_1"}}
    assert any("not whitelisted" in e for e in validate(ast, LANE_S_FEATURES))


def test_rejects_excess_depth():
    ast = {"feature": "mom_12_1"}
    for _ in range(10):
        ast = {"op": "abs", "arg": ast}
    assert any("depth" in e for e in validate(ast, LANE_S_FEATURES))


def test_rejects_bad_window():
    ast = {"op": "lag", "arg": {"feature": "mom_12_1"}, "window": 0}
    assert any("window" in e for e in validate(ast, LANE_S_FEATURES))
    ast = {"op": "lag", "arg": {"feature": "mom_12_1"}, "window": 9999}
    assert any("window" in e for e in validate(ast, LANE_S_FEATURES))


def test_rejects_non_dict_node():
    assert validate({"op": "rank", "arg": "mom_12_1"}, LANE_S_FEATURES)


def test_formula_rendering():
    ast = {"op": "sub",
           "left": {"op": "rank", "arg": {"feature": "mom_12_1"}},
           "right": {"op": "ts_mean", "arg": {"feature": "quality_score"}, "window": 5}}
    assert formula(ast) == "sub(rank(mom_12_1), ts_mean(quality_score, 5))"


def test_evaluate_rank_matches_manual():
    df = _frame()
    sig = evaluate(VALID, df, LANE_S_FEATURES)
    manual = (df.assign(sig=sig)
                .groupby("date")
                .apply(lambda g: g["mom_12_1"].rank(pct=True).equals(
                    g["sig"].rank(pct=True)), include_groups=False))
    assert manual.all()


def test_evaluate_invalid_raises():
    df = _frame()
    with pytest.raises(ValueError):
        evaluate({"feature": "nope"}, df, LANE_S_FEATURES)


def test_no_lookahead_property():
    """Signal at date t must not change when future feature values change."""
    df = _frame()
    ast = {"op": "zscore",
           "arg": {"op": "ts_mean", "arg": {"feature": "mom_12_1"}, "window": 5}}
    sig_full = evaluate(ast, df, LANE_S_FEATURES)

    cutoff = df["date"].sort_values().unique()[25]
    mutated = df.copy()
    future = mutated["date"] > cutoff
    mutated.loc[future, "mom_12_1"] = 999.0
    sig_mut = evaluate(ast, mutated, LANE_S_FEATURES)

    past = df["date"] <= cutoff
    a = pd.Series(sig_full[past].to_numpy())
    b = pd.Series(sig_mut[past.to_numpy()].to_numpy())
    pd.testing.assert_series_equal(a, b)


def test_determinism():
    df = _frame()
    ast = {"op": "mul",
           "left": {"op": "rank", "arg": {"feature": "mom_12_1"}},
           "right": {"op": "rank", "arg": {"feature": "quality_score"}}}
    s1 = evaluate(ast, df, LANE_S_FEATURES)
    s2 = evaluate(ast, df, LANE_S_FEATURES)
    pd.testing.assert_series_equal(s1, s2)
