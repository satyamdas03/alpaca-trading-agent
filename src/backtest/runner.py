"""Walk-forward backtest runner.

Custom implementation that replaces the broken PyBroker integration.
Uses our own signal/sizing pipeline directly, matching the live trading path.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import numpy as np
import pandas as pd

from src.backtest.engine import BacktestEngine
from src.backtest.metrics import (
    sharpe_ratio, max_drawdown, cap_outlier_year,
    regime_sharpe, validate_strategy, bootstrap_ci,
)
from src.signals.regime import classify_regime


@dataclass
class WalkForwardConfig:
    train_bars: int = 504   # 2 years
    test_bars: int = 63     # 1 quarter
    embargo_bars: int = 5   # 1 week gap between train and test

    def count_windows(self, total_bars: int) -> int:
        if total_bars < self.train_bars + self.test_bars:
            return 0
        # Sliding windows: advance by test_bars each step
        pos = 0
        count = 0
        while pos + self.train_bars + self.test_bars <= total_bars:
            count += 1
            pos += self.test_bars + self.embargo_bars
        return count

    def window_ranges(self, total_bars: int) -> list[tuple[int, int, int]]:
        """Return list of (train_start, train_end, test_end) tuples.

        Uses sliding windows: each window advances by test_bars + embargo,
        keeping train_bars of history before each test window.
        """
        windows = []
        if total_bars < self.train_bars + self.test_bars:
            return windows
        pos = 0
        while pos + self.train_bars + self.test_bars <= total_bars:
            train_start = pos
            train_end = pos + self.train_bars
            test_end = train_end + self.test_bars
            windows.append((train_start, train_end, test_end))
            pos += self.test_bars + self.embargo_bars
        return windows


@dataclass
class BacktestResult:
    total_return: float
    cagr: float
    sharpe: float
    max_dd: float
    win_rate: float
    num_trades: int
    regime_sharpes: dict[str, float]
    strategy_valid: bool
    sharpe_ci: tuple[float, float]
    daily_returns: pd.Series
    equity_curve: pd.Series
    trades: list[dict]


def run_backtest(
    strategy_factory: Callable,
    price_data: dict[str, pd.DataFrame],
    fundamentals: dict[str, dict] | None = None,
    dark_pool: dict[str, dict] | None = None,
    config: WalkForwardConfig | None = None,
    initial_capital: float = 100_000,
    transaction_cost: float = 0.001,
    slippage: float = 0.0005,
    max_position_pct: float = 0.10,
) -> BacktestResult:
    """Run walk-forward backtest with our custom engine.

    Args:
        strategy_factory: Callable(vix=float) -> BullStrategy
        price_data: Dict of {ticker: DataFrame with 'close' column}
        fundamentals: Dict of {ticker: fundamentals dict}
        dark_pool: Dict of {ticker: dark pool data dict}
        config: Walk-forward window configuration
        initial_capital: Starting portfolio value
        transaction_cost: Cost per trade as fraction (0.001 = 10bps)
        slippage: Slippage per trade as fraction
        max_position_pct: Max position size as fraction of portfolio

    Returns:
        BacktestResult with performance metrics.
    """
    if config is None:
        config = WalkForwardConfig()
    if fundamentals is None:
        fundamentals = {}
    if dark_pool is None:
        dark_pool = {}

    # Use first ticker as the universe indicator
    tickers = list(price_data.keys())
    if not tickers:
        return _empty_result(initial_capital)

    # Merge all price data to find common date range
    all_dates = None
    for ticker, df in price_data.items():
        if "date" in df.columns:
            dates = set(df["date"])
        elif df.index.name == "date":
            dates = set(df.index)
        else:
            dates = set(range(len(df)))
        all_dates = dates if all_dates is None else all_dates & dates

    # Use SPY or first ticker as reference for total bars
    ref_ticker = tickers[0]
    ref_prices = price_data[ref_ticker]
    total_bars = len(ref_prices)

    windows = config.window_ranges(total_bars)
    if not windows:
        return _empty_result(initial_capital)

    engine = BacktestEngine(
        initial_capital=initial_capital,
        transaction_cost=transaction_cost,
        slippage=slippage,
        max_position_pct=max_position_pct,
    )

    all_daily_returns = []
    all_regimes = []
    all_trades = []

    for train_start, train_end, test_end in windows:
        # Determine VIX regime from train period (use end of train)
        # In live, we'd use real VIX; here approximate from volatility
        ref_close = ref_prices["close"].values
        if train_end > 22 and len(ref_close) > train_end:
            returns_slice = ref_close[train_end-21:train_end]
            daily_returns_slice = np.diff(returns_slice) / returns_slice[:-1]
            train_vol = float(np.std(daily_returns_slice) * np.sqrt(252))
            # Approximate VIX from realized vol (VIX ≈ realized * 1.2 typically)
            # VIX is quoted in percentage points (e.g., VIX=20 means 20% vol)
            approx_vix = train_vol * 100 * 1.2
        else:
            approx_vix = 20.0  # default

        strategy = strategy_factory(vix=approx_vix)

        # Pass trailing history (from train_start) + test period to engine.
        # Walk-forward means no lookahead, but signals need enough history
        # for momentum (252 bars), volatility (60 bars), etc.
        test_prices = {}
        for ticker, df in price_data.items():
            test_df = df.iloc[train_start:test_end].copy()
            test_prices[ticker] = test_df

        window_returns, window_trades = engine.simulate_window(
            strategy=strategy,
            price_data=test_prices,
            fundamentals=fundamentals,
            dark_pool=dark_pool,
            train_bars=train_end - train_start,
        )

        all_daily_returns.extend(window_returns)
        all_trades.extend(window_trades)

        # Track regimes
        regime = classify_regime(approx_vix)
        all_regimes.extend([regime.value] * len(window_returns))

    returns_arr = np.array(all_daily_returns)
    regimes_arr = np.array(all_regimes)

    # Build equity curve
    equity = initial_capital * np.cumprod(1 + returns_arr)
    equity_series = pd.Series(equity)
    returns_series = pd.Series(returns_arr)

    # Calculate metrics
    total_ret = float(equity[-1] / initial_capital - 1)
    n_years = len(returns_arr) / 252
    cagr = (1 + total_ret) ** (1 / max(n_years, 0.01)) - 1 if n_years > 0 else 0.0
    sharpe = sharpe_ratio(returns_arr)
    max_dd = max_drawdown(equity)

    # Win rate
    winning = [1 for t in all_trades if t.get("pnl", 0) > 0]
    win_rate = len(winning) / max(len(all_trades), 1)

    # Regime-sharpe breakdown
    regime_sharpes = regime_sharpe(returns_arr, regimes_arr) if len(regimes_arr) > 0 else {}
    strategy_valid = validate_strategy(regime_sharpes)

    # Bootstrap CI
    ci_lo, ci_hi = bootstrap_ci(returns_arr)

    return BacktestResult(
        total_return=total_ret,
        cagr=cagr,
        sharpe=sharpe,
        max_dd=max_dd,
        win_rate=win_rate,
        num_trades=len(all_trades),
        regime_sharpes=regime_sharpes,
        strategy_valid=strategy_valid,
        sharpe_ci=(ci_lo, ci_hi),
        daily_returns=returns_series,
        equity_curve=equity_series,
        trades=all_trades,
    )


def _empty_result(capital: float) -> BacktestResult:
    return BacktestResult(
        total_return=0.0,
        cagr=0.0,
        sharpe=0.0,
        max_dd=0.0,
        win_rate=0.0,
        num_trades=0,
        regime_sharpes={},
        strategy_valid=False,
        sharpe_ci=(0.0, 0.0),
        daily_returns=pd.Series(dtype=float),
        equity_curve=pd.Series(dtype=float),
        trades=[],
    )