from src.signals.quality import quality_score, gross_margin_score

def test_high_quality_company():
    fundamentals = {
        "revenue": 100, "gross_profit": 60, "net_income": 20,
        "total_assets": 200, "total_liabilities": 80,
        "current_assets": 50, "current_liabilities": 30,
    }
    prev = {
        "revenue": 90, "gross_profit": 50, "net_income": 15,
        "total_assets": 180, "total_liabilities": 85,
        "current_assets": 40, "current_liabilities": 35,
    }
    score = quality_score(fundamentals, prev)
    assert score >= 5
    assert score <= 9

def test_low_quality_company():
    fundamentals = {
        "revenue": 100, "gross_profit": 10, "net_income": -5,
        "total_assets": 200, "total_liabilities": 150,
        "current_assets": 20, "current_liabilities": 60,
    }
    prev = {
        "revenue": 120, "gross_profit": 30, "net_income": 10,
        "total_assets": 180, "total_liabilities": 100,
        "current_assets": 50, "current_liabilities": 40,
    }
    score = quality_score(fundamentals, prev)
    assert score <= 4

def test_missing_data_returns_zero():
    score = quality_score({}, {})
    assert score == 0

def test_gross_margin_pass():
    fundamentals = {"gross_profit": 60, "revenue": 100}
    result = gross_margin_score(fundamentals, threshold=0.3)
    assert result == 1

def test_gross_margin_fail():
    fundamentals = {"gross_profit": 20, "revenue": 100}
    result = gross_margin_score(fundamentals, threshold=0.3)
    assert result == 0