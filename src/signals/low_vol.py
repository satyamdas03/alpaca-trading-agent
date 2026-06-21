"""Low volatility signal: ranks stocks by realized volatility.

Lower volatility = higher score (0-1 scale). Based on the low-vol anomaly
where low-vol stocks tend to outperform on a risk-adjusted basis.
"""

import numpy as np
import pandas as pd


def low_vol_score(prices: pd.DataFrame, lookback: int = 60) -> float:
    """Compute low volatility score from price data.

    Args:
        prices: DataFrame with 'close' column.
        lookback: Number of trading days for volatility calculation.

    Returns:
        Float 0-1, where higher = lower volatility (better for low-vol factor).
        Returns 0.5 (neutral) if insufficient data.
    """
    if len(prices) < lookback or "close" not in prices.columns:
        return 0.5

    close = prices["close"].values[-lookback:]
    returns = np.diff(close) / close[:-1]
    returns = returns[~np.isnan(returns) & np.isfinite(returns)]

    if len(returns) < 10:
        return 0.5

    realized_vol = float(np.std(returns) * np.sqrt(252))

    # Map volatility to score:
    # vol < 10% → score 1.0 (very low vol)
    # vol = 20% → score 0.5 (market average)
    # vol > 40% → score 0.0 (very high vol)
    return _vol_to_score(realized_vol)


def rank_low_vol(ticker_prices: dict[str, pd.DataFrame],
                 lookback: int = 60, top_n: int = 15) -> list[tuple[str, float]]:
    """Rank tickers by low volatility (lowest vol first).

    Args:
        ticker_prices: Dict of {ticker: price DataFrame}.
        lookback: Days for vol calculation.
        top_n: Number of top low-vol tickers to return.

    Returns:
        List of (ticker, score) tuples sorted by score descending.
    """
    scores = {}
    for ticker, prices in ticker_prices.items():
        scores[ticker] = low_vol_score(prices, lookback)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def realized_volatility(prices: pd.DataFrame, lookback: int = 60) -> float:
    """Return annualized realized volatility."""
    if len(prices) < lookback or "close" not in prices.columns:
        return 0.0
    close = prices["close"].values[-lookback:]
    returns = np.diff(close) / close[:-1]
    returns = returns[~np.isnan(returns) & np.isfinite(returns)]
    if len(returns) < 10:
        return 0.0
    return float(np.std(returns) * np.sqrt(252))


def _vol_to_score(vol: float) -> float:
    """Convert annualized volatility to 0-1 score (lower vol = higher score).

    vol < 0.10 → 1.0
    vol = 0.20 → 0.5
    vol > 0.40 → 0.0
    """
    if vol <= 0:
        return 0.5
    return max(0.0, min(1.0, (0.40 - vol) / 0.30))