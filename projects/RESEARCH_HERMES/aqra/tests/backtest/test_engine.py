import pandas as pd
from aqra.backtest.engine import BacktestEngine


def test_backtest_produces_metrics():
    engine = BacktestEngine()
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=60, freq="B"),
        "ticker": ["AAPL"] * 60,
        "signal": [0.0] * 30 + [1.0] * 30,
        "forward_return": [0.0] * 60,
    })
    result = engine.run_single_signal(df, holding_period=5)
    assert "sharpe" in result
    assert "ic" in result
    assert "max_drawdown" in result
