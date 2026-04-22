import pandas as pd


def momentum_score(prices: pd.DataFrame, lookback: int = 252, skip: int = 21) -> float:
    """12-1 momentum: return over lookback period skipping last `skip` days."""
    if len(prices) < lookback:
        return 0.0
    close = prices["close"].values
    current = close[-1 - skip]
    past = close[-1 - skip - lookback] if len(close) > lookback + skip else close[0]
    if past == 0:
        return 0.0
    return (current - past) / past


def rank_momentum(
    ticker_prices: dict[str, pd.DataFrame],
    lookback: int = 252,
    skip: int = 21,
    top_n: int = 15,
) -> list[tuple[str, float]]:
    scores = {}
    for ticker, prices in ticker_prices.items():
        scores[ticker] = momentum_score(prices, lookback, skip)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]