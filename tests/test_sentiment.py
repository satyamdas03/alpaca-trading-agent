from datetime import date, timedelta
from src.signals.sentiment import sentiment_score, _ats_ratio_to_score, _compute_staleness


def test_sentiment_score_high_ats():
    data = {
        "ats_ratio": 0.25,
        "as_of_date": date.today().isoformat(),
        "ats_volume": 500000,
        "total_volume": 2000000,
    }
    score = sentiment_score(data)
    assert 0.5 < score <= 1.0  # high ATS → bullish bias


def test_sentiment_score_low_ats():
    data = {
        "ats_ratio": 0.02,
        "as_of_date": date.today().isoformat(),
        "ats_volume": 10000,
        "total_volume": 5000000,
    }
    score = sentiment_score(data)
    assert 0.0 < score < 0.5  # low ATS → slightly bearish


def test_sentiment_score_stale_data():
    stale_date = (date.today() - timedelta(weeks=3)).isoformat()
    data = {
        "ats_ratio": 0.25,
        "as_of_date": stale_date,
        "ats_volume": 500000,
        "total_volume": 2000000,
    }
    fresh_data = {
        "ats_ratio": 0.25,
        "as_of_date": date.today().isoformat(),
        "ats_volume": 500000,
        "total_volume": 2000000,
    }
    stale_score = sentiment_score(data)
    fresh_score = sentiment_score(fresh_data)
    assert stale_score < fresh_score  # staleness reduces score


def test_sentiment_score_empty():
    score = sentiment_score({})
    assert score == 0.5  # neutral


def test_ats_ratio_to_score():
    assert _ats_ratio_to_score(0) < 0.4
    assert _ats_ratio_to_score(0.10) > 0.5
    assert _ats_ratio_to_score(0.25) > 0.7


def test_compute_staleness():
    today = date.today().isoformat()
    assert _compute_staleness(today, 4.0) == 1.0  # fresh data
    old = (date.today() - timedelta(weeks=4)).isoformat()
    assert _compute_staleness(old, 4.0) == 0.0  # fully stale