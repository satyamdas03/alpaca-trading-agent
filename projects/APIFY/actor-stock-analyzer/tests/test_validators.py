import pytest
from src.validators import validate_input, ValidationError

class TestTickers:
    def test_valid_us_ticker(self):
        r = validate_input({"tickers": ["NVDA"]})
        assert r["tickers"] == ["NVDA"]

    def test_valid_india_ticker(self):
        r = validate_input({"tickers": ["RELIANCE.NS"]})
        assert r["tickers"] == ["RELIANCE.NS"]

    def test_tickers_uppercased(self):
        r = validate_input({"tickers": ["nvda", "tcs.ns"]})
        assert r["tickers"] == ["NVDA", "TCS.NS"]

    def test_whitespace_stripped(self):
        r = validate_input({"tickers": ["  NVDA  "]})
        assert r["tickers"] == ["NVDA"]

    def test_deduplication(self):
        r = validate_input({"tickers": ["NVDA", "NVDA", "AAPL"]})
        assert r["tickers"].count("NVDA") == 1

    def test_empty_list_raises(self):
        with pytest.raises(ValidationError, match="tickers"):
            validate_input({"tickers": []})

    def test_missing_tickers_raises(self):
        with pytest.raises(ValidationError):
            validate_input({})

    def test_too_many_tickers_raises(self):
        with pytest.raises(ValidationError, match="50"):
            validate_input({"tickers": [f"T{i}" for i in range(51)]})

    def test_invalid_ticker_chars_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"tickers": ["NVDA; DROP TABLE--"]})

    def test_ticker_too_long_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"tickers": ["A" * 21]})


class TestMode:
    def test_default_mode_is_quant(self):
        r = validate_input({"tickers": ["NVDA"]})
        assert r["mode"] == "quant"

    def test_full_ai_mode_accepted(self):
        r = validate_input({"tickers": ["NVDA"], "mode": "full_ai"})
        assert r["mode"] == "full_ai"

    def test_invalid_mode_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"tickers": ["NVDA"], "mode": "turbo"})


class TestMaxSpend:
    def test_default_max_spend(self):
        r = validate_input({"tickers": ["NVDA"]})
        assert r["max_spend_usd"] == 2.0

    def test_custom_spend(self):
        r = validate_input({"tickers": ["NVDA"], "max_spend_usd": 5.0})
        assert r["max_spend_usd"] == 5.0

    def test_negative_spend_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"tickers": ["NVDA"], "max_spend_usd": -1})