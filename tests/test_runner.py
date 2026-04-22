import numpy as np
import pandas as pd
from src.backtest.runner import WalkForwardConfig, run_backtest, BacktestResult
from src.strategy.bull_strategy import BullStrategy


def test_walkforward_config_defaults():
    config = WalkForwardConfig()
    assert config.train_bars == 504
    assert config.test_bars == 63
    assert config.embargo_bars == 5


def test_walkforward_config_custom():
    config = WalkForwardConfig(train_bars=252, test_bars=21, embargo_bars=3)
    assert config.train_bars == 252
    assert config.test_bars == 21


def test_count_windows():
    config = WalkForwardConfig(train_bars=504, test_bars=63, embargo_bars=5)
    total_bars = 504 + 63 + 5 + 63 + 5 + 63
    windows = config.count_windows(total_bars)
    assert windows == 3


def test_count_windows_insufficient():
    config = WalkForwardConfig(train_bars=504, test_bars=63, embargo_bars=5)
    windows = config.count_windows(500)
    assert windows == 0


def test_window_ranges():
    config = WalkForwardConfig(train_bars=10, test_bars=5, embargo_bars=1)
    ranges = config.window_ranges(25)
    assert len(ranges) >= 1
    # First window: train [0,10), test [10,15)
    assert ranges[0][0] == 0
    assert ranges[0][1] == 10
    assert ranges[0][2] == 15


def test_run_backtest_empty():
    result = run_backtest(
        strategy_factory=lambda vix: BullStrategy(vix=vix),
        price_data={},
    )
    assert result.total_return == 0.0
    assert result.num_trades == 0


def test_run_backtest_returns_result_type():
    n = 700
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    prices = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=n, freq="B"),
        "close": close,
        "open": close - 0.2,
        "high": close + 0.5,
        "low": close - 0.5,
        "volume": np.full(n, 1_000_000),
    })
    result = run_backtest(
        strategy_factory=lambda vix: BullStrategy(vix=vix),
        price_data={"SPY": prices},
        config=WalkForwardConfig(train_bars=252, test_bars=63, embargo_bars=5),
        initial_capital=100_000,
    )
    assert isinstance(result, BacktestResult)
    assert isinstance(result.total_return, float)
    assert isinstance(result.sharpe, float)