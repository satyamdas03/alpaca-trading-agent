import pandas as pd
import numpy as np
from src.strategy.bull_strategy import BullStrategy

def test_strategy_generates_signals():
    strategy = BullStrategy(vix=18.0)
    n = 300
    prices = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n, freq="B"),
        "open": np.random.uniform(95, 105, n),
        "high": np.random.uniform(100, 110, n),
        "low": np.random.uniform(90, 100, n),
        "close": np.cumsum(np.random.randn(n)) + 100,
        "volume": np.random.randint(1000000, 5000000, n),
    })
    signals = strategy.generate_signals(prices)
    assert "quality" in signals
    assert "momentum" in signals
    assert "regime" in signals
    assert "composite" in signals

def test_strategy_risk_on_high_momentum():
    strategy = BullStrategy(vix=15.0)
    n = 300
    close = np.array([100 + i * 0.5 for i in range(n)])
    prices = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n, freq="B"),
        "open": close - 0.5,
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": np.full(n, 2000000),
    })
    signals = strategy.generate_signals(prices)
    assert signals["momentum"] > 0

def test_pybroker_exec_fn_callable():
    strategy = BullStrategy(vix=18.0)
    fn = strategy.pybroker_exec_fn()
    assert callable(fn)