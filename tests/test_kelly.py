import numpy as np
from src.sizing.kelly import half_kelly_size

def test_half_kelly_positive_sharpe():
    size = half_kelly_size(sharpe=1.5, volatility=0.20, max_fraction=0.20)
    assert size > 0
    assert size <= 0.20

def test_half_kelly_zero_sharpe():
    size = half_kelly_size(sharpe=0.0, volatility=0.20, max_fraction=0.20)
    assert size == 0.0

def test_half_kelly_negative_sharpe():
    size = half_kelly_size(sharpe=-1.0, volatility=0.20, max_fraction=0.20)
    assert size == 0.0

def test_half_kelly_respects_max():
    size = half_kelly_size(sharpe=5.0, volatility=0.10, max_fraction=0.20)
    assert size <= 0.20

def test_half_kelly_default_max():
    size = half_kelly_size(sharpe=2.0, volatility=0.15)
    assert size <= 0.10