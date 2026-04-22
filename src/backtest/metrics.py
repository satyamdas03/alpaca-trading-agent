import numpy as np


def sharpe_ratio(returns: np.ndarray, risk_free: float = 0.045 / 252) -> float:
    if len(returns) == 0:
        return 0.0
    excess = returns - risk_free
    if np.std(excess) == 0:
        return 0.0
    return float(np.mean(excess) / np.std(excess) * np.sqrt(252))


def max_drawdown(equity: np.ndarray) -> float:
    if len(equity) == 0:
        return 0.0
    peak = np.maximum.accumulate(equity)
    dd = (peak - equity) / peak
    return float(np.max(dd))


def cap_outlier_year(yearly_returns: dict[int, np.ndarray],
                     max_annual: float = 0.60) -> dict[int, np.ndarray]:
    capped = {}
    for year, returns in yearly_returns.items():
        total = float(np.prod(1 + returns) - 1)
        if total > max_annual:
            scale = max_annual / total
            capped[year] = returns * scale
        else:
            capped[year] = returns.copy()
    return capped


def regime_sharpe(returns: np.ndarray, regimes: np.ndarray) -> dict[str, float]:
    result = {}
    for regime in np.unique(regimes):
        mask = regimes == regime
        regime_returns = returns[mask]
        if len(regime_returns) > 0:
            result[regime] = sharpe_ratio(regime_returns)
    return result


def validate_strategy(regime_sharpes: dict[str, float],
                      min_regimes: int = 2) -> bool:
    positive = sum(1 for s in regime_sharpes.values() if s > 0)
    return positive >= min_regimes


def bootstrap_ci(returns: np.ndarray, n_samples: int = 1000,
                 ci: float = 0.95) -> tuple[float, float]:
    """Bootstrap confidence interval for Sharpe ratio."""
    sharpes = []
    n = len(returns)
    for _ in range(n_samples):
        sample = np.random.choice(returns, size=n, replace=True)
        sharpes.append(sharpe_ratio(sample))
    alpha = (1 - ci) / 2
    lo = float(np.percentile(sharpes, alpha * 100))
    hi = float(np.percentile(sharpes, (1 - alpha) * 100))
    return lo, hi