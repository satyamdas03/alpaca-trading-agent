import numpy as np
from src.backtest.metrics import (
    sharpe_ratio, max_drawdown, cap_outlier_year,
    regime_sharpe, bootstrap_ci, validate_strategy,
)

def test_sharpe_positive():
    returns = np.array([0.01, 0.02, -0.01, 0.03, 0.005])
    s = sharpe_ratio(returns)
    assert s > 0

def test_max_drawdown():
    equity = np.array([100, 110, 105, 95, 100])
    dd = max_drawdown(equity)
    assert abs(dd - 0.1364) < 0.01

def test_cap_outlier_year():
    returns_2023 = np.full(252, 0.003)
    returns_2024 = np.full(252, 0.004)
    returns_2025 = np.full(252, 0.0025)
    years = {
        2023: returns_2023,
        2024: returns_2024,
        2025: returns_2025,
    }
    capped = cap_outlier_year(years, max_annual=0.60)
    assert capped[2024].mean() * 252 <= 0.61

def test_regime_sharpe():
    rng = np.random.default_rng(42)
    returns = np.concatenate([rng.normal(0.01, 0.005, 50), rng.normal(-0.02, 0.005, 50)])
    regimes = np.array(["risk_on"] * 50 + ["stress"] * 50)
    result = regime_sharpe(returns, regimes)
    assert "risk_on" in result
    assert "stress" in result
    assert result["risk_on"] > 0
    assert result["stress"] < 0

def test_validate_strategy_passes():
    regime_results = {"risk_on": 1.5, "late_cycle": 0.8, "stress": -0.5}
    assert validate_strategy(regime_results, min_regimes=2) is True

def test_validate_strategy_fails():
    regime_results = {"risk_on": 1.5, "late_cycle": -0.3, "stress": -1.0}
    assert validate_strategy(regime_results, min_regimes=2) is False

def test_bootstrap_ci():
    returns = np.random.normal(0.001, 0.02, 1000)
    lo, hi = bootstrap_ci(returns, n_samples=100)
    assert lo < hi