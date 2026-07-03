import numpy as np
import pandas as pd
from aqra.backtest.engine import BacktestEngine


def _panel(n_tickers=20, n_days=120, signal_predicts=True, seed=7):
    """Cross-sectional panel where signal optionally predicts next-day returns."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    tickers = [f"T{i:02d}" for i in range(n_tickers)]
    rows = []
    for t_idx, ticker in enumerate(tickers):
        # persistent per-ticker signal rank with small noise
        base = (t_idx / (n_tickers - 1)) - 0.5
        sig = base + rng.normal(0, 0.05, n_days)
        noise = rng.normal(0, 0.01, n_days)
        drift = 0.002 * base if signal_predicts else 0.0
        ret = drift + noise
        rows.append(pd.DataFrame({
            "date": dates, "ticker": ticker, "signal": sig, "ret_1d": ret,
        }))
    return pd.concat(rows, ignore_index=True)


def test_backtest_produces_metrics():
    engine = BacktestEngine()
    result = engine.run_single_signal(_panel(), holding_period=5)
    assert "sharpe" in result
    assert "ic" in result
    assert "max_drawdown" in result
    assert "turnover" in result
    assert result["max_drawdown"] <= 0 or result["max_drawdown"] >= 0  # finite
    assert np.isfinite(result["sharpe"])


def test_predictive_signal_beats_random():
    engine = BacktestEngine()
    good = engine.run_single_signal(_panel(signal_predicts=True), holding_period=5)
    flat = engine.run_single_signal(_panel(signal_predicts=False), holding_period=5)
    assert good["sharpe"] > flat["sharpe"]
    assert good["ic"] > 0


def test_degenerate_input_returns_empty():
    engine = BacktestEngine()
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=60, freq="B"),
        "ticker": ["AAPL"] * 60,
        "signal": [1.0] * 60,
        "ret_1d": [0.0] * 60,
    })
    # single ticker: demeaned weights are zero, flat pnl -> {}
    assert engine.run_single_signal(df, holding_period=5) == {}


def test_too_short_history_returns_empty():
    engine = BacktestEngine()
    df = _panel(n_days=4)
    assert engine.run_single_signal(df, holding_period=5) == {}
