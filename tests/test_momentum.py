import pandas as pd
from src.signals.momentum import momentum_score, rank_momentum

def test_momentum_score_positive():
    prices = pd.DataFrame({"close": [100 + i for i in range(252)]})
    score = momentum_score(prices, lookback=252, skip=21)
    assert score > 0

def test_momentum_score_negative():
    prices = pd.DataFrame({"close": [300 - i for i in range(252)]})
    score = momentum_score(prices, lookback=252, skip=21)
    assert score < 0

def test_momentum_score_short_data():
    prices = pd.DataFrame({"close": [100, 101, 102]})
    score = momentum_score(prices, lookback=252, skip=21)
    assert score == 0.0

def test_rank_momentum():
    tickers = {
        "AAPL": pd.DataFrame({"close": [100 + i for i in range(252)]}),
        "TSLA": pd.DataFrame({"close": [200 - i * 0.5 for i in range(252)]}),
        "MSFT": pd.DataFrame({"close": [150 + i * 0.3 for i in range(252)]}),
    }
    ranked = rank_momentum(tickers, top_n=2)
    assert len(ranked) == 2
    assert ranked[0][1] >= ranked[1][1]