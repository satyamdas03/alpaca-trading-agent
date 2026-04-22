from src.signals.value import value_score, _ratio_to_score


def test_value_score_with_earnings():
    fundamentals = {
        "net_income": 10_000_000,
        "total_assets": 100_000_000,
        "total_liabilities": 40_000_000,
        "shares_outstanding": 5_000_000,
        "revenue": 50_000_000,
        "gross_profit": 30_000_000,
    }
    # P/E = 100 / (10M/5M) = 50 → expensive vs sector avg 20
    # P/B = 100 / ((100M-40M)/5M) = 100/12 = 8.33 → expensive vs sector avg 2
    score = value_score(fundamentals, current_price=100.0, sector_pe=20.0, sector_pb=2.0)
    assert 0.0 <= score <= 1.0
    assert score < 0.5  # expensive → low score


def test_value_score_cheap_stock():
    fundamentals = {
        "net_income": 50_000_000,
        "total_assets": 500_000_000,
        "total_liabilities": 200_000_000,
        "shares_outstanding": 100_000_000,
        "revenue": 200_000_000,
        "gross_profit": 120_000_000,
    }
    # P/E = 50 / (50M/100M) = 100 → expensive, but this tests the path
    score = value_score(fundamentals, current_price=50.0)
    assert 0.0 <= score <= 1.0


def test_value_score_no_price():
    fundamentals = {"net_income": 10_000_000}
    score = value_score(fundamentals, current_price=None)
    assert score == 0.5  # neutral


def test_value_score_empty_fundamentals():
    score = value_score({}, current_price=100.0)
    assert score == 0.5


def test_ratio_to_score():
    assert _ratio_to_score(0.5) == 1.0   # very cheap
    assert _ratio_to_score(1.0) == 0.5   # fair value
    assert _ratio_to_score(2.0) == 0.0   # expensive
    assert 0.0 <= _ratio_to_score(1.5) <= 0.5