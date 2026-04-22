import numpy as np
import pandas as pd
from src.signals.low_vol import low_vol_score, realized_volatility, _vol_to_score


def test_low_vol_score_low_volatility():
    # Stable prices → low vol → high score
    n = 100
    close = np.linspace(100, 105, n)
    prices = pd.DataFrame({"close": close})
    score = low_vol_score(prices, lookback=60)
    assert score > 0.5  # low vol should score high


def test_low_vol_score_high_volatility():
    # Noisy prices → high vol → low score
    n = 100
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(n) * 3)
    prices = pd.DataFrame({"close": close})
    score = low_vol_score(prices, lookback=60)
    assert score < 0.5  # high vol should score low


def test_low_vol_score_insufficient_data():
    prices = pd.DataFrame({"close": [100, 101]})
    score = low_vol_score(prices, lookback=60)
    assert score == 0.5  # neutral


def test_realized_volatility():
    n = 100
    close = np.linspace(100, 105, n)
    prices = pd.DataFrame({"close": close})
    vol = realized_volatility(prices, lookback=60)
    assert vol > 0
    assert vol < 0.5  # gentle slope → low vol


def test_vol_to_score():
    assert _vol_to_score(0.05) == 1.0   # very low vol
    assert _vol_to_score(0.20) == pytest.approx(0.667, abs=0.01)
    assert _vol_to_score(0.40) == 0.0   # very high vol


import pytest