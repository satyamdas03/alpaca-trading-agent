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
    assert "value" in signals
    assert "low_vol" in signals
    assert "sentiment" in signals
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


def test_strategy_with_fundamentals():
    strategy = BullStrategy(vix=22.0)
    n = 300
    close = np.array([100 + i * 0.3 for i in range(n)])
    prices = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n, freq="B"),
        "open": close - 0.5,
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": np.full(n, 2000000),
    })
    fundamentals = {
        "net_income": 5_000_000,
        "total_assets": 50_000_000,
        "total_liabilities": 20_000_000,
        "revenue": 30_000_000,
        "gross_profit": 15_000_000,
    }
    signals = strategy.generate_signals(
        prices, fundamentals=fundamentals, current_price=close[-1]
    )
    assert signals["quality"] > 0  # profitable company → positive quality
    assert signals["value"] != 0.5  # should not be neutral when fundamentals provided


def test_strategy_regime_weights():
    strategy_on = BullStrategy(vix=15.0)
    strategy_stress = BullStrategy(vix=35.0)
    # Stress regime should weight low_vol higher, momentum lower
    assert strategy_stress.weights["low_vol"] > strategy_on.weights["low_vol"]
    assert strategy_stress.weights["momentum"] < strategy_on.weights["momentum"]