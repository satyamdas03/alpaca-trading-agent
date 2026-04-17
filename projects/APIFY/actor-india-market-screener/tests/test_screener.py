"""Tests for India Market Screener validators and main logic."""
import pytest
from src.validators import validate_input, ValidationError
from src.universe import get_universe


class TestScreenerValidation:
    def test_defaults(self):
        r = validate_input({})
        assert r["market"] == "India"
        assert r["min_score"] == 6.0
        assert r["sort_by"] == "score"
        assert r["top_n"] == 20

    def test_valid_market_us(self):
        r = validate_input({"market": "US"})
        assert r["market"] == "US"

    def test_valid_market_both(self):
        r = validate_input({"market": "both"})
        assert r["market"] == "both"

    def test_invalid_market_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"market": "China"})

    def test_min_score_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"min_score": 11})

    def test_min_score_zero_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"min_score": 0})

    def test_top_n_exceeds_max_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"top_n": 101})

    def test_top_n_zero_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"top_n": 0})

    def test_invalid_sort_by_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"sort_by": "hype"})

    def test_valid_sort_by_options(self):
        for sort_by in ["score", "momentum", "quality", "value"]:
            r = validate_input({"sort_by": sort_by})
            assert r["sort_by"] == sort_by


class TestUniverse:
    def test_india_universe(self):
        india = get_universe("India")
        assert len(india) == 40
        assert "RELIANCE.NS" in india
        assert "TCS.NS" in india
        assert all(t.endswith(".NS") for t in india)

    def test_us_universe(self):
        us = get_universe("US")
        assert len(us) == 41
        assert "NVDA" in us
        assert "AAPL" in us
        assert all(not t.endswith(".NS") for t in us)

    def test_both_universe(self):
        both = get_universe("both")
        assert len(both) == 40 + 41