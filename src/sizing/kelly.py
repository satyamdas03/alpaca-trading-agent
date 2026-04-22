import numpy as np


def half_kelly_size(
    sharpe: float,
    volatility: float,
    max_fraction: float = 0.10,
    risk_free: float = 0.045,
) -> float:
    """Compute half-Kelly optimal fraction for a single asset.

    Kelly fraction = (mu - rf) / sigma^2
    Half-Kelly = Kelly / 2 (safety buffer)

    We approximate mu from Sharpe: mu = rf + sharpe * sigma
    """
    if sharpe <= 0 or volatility <= 0:
        return 0.0
    mu = risk_free + sharpe * volatility
    kelly = (mu - risk_free) / (volatility ** 2)
    half_k = kelly / 2.0
    return min(half_k, max_fraction)