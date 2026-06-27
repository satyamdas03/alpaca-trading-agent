import numpy as np
import pandas as pd


def sharpe(returns: pd.Series, periods: int = 252) -> float:
    if returns.std() == 0 or returns.empty:
        return np.nan
    return returns.mean() / returns.std() * np.sqrt(periods)


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return ((equity - peak) / peak).min()


def information_coefficient(signal: pd.Series, forward_return: pd.Series) -> float:
    valid = signal.notna() & forward_return.notna()
    if valid.sum() < 10:
        return np.nan
    return signal[valid].corr(forward_return[valid], method="spearman")


def turnover(weights: pd.DataFrame) -> float:
    # Annualized turnover from daily weight changes
    deltas = weights.diff().abs().sum(axis=1)
    return deltas.mean() * 252
