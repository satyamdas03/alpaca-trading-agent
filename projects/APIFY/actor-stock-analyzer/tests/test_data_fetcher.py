import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data_fetcher import (
    build_fundamentals_row, _piotroski_from_info,
    _safe, _yf_symbol
)

class TestSafe:
    def test_valid_float(self):
        assert _safe(3.14) == pytest.approx(3.14)

    def test_none_returns_default(self):
        assert _safe(None) == 0.0

    def test_inf_returns_default(self):
        assert _safe(float("inf")) == 0.0

    def test_nan_returns_default(self):
        import math
        assert _safe(float("nan")) == 0.0

    def test_string_number(self):
        assert _safe("2.5") == pytest.approx(2.5)

    def test_custom_default(self):
        assert _safe(None, default=99.0) == 99.0


class TestYfSymbol:
    def test_india_ticker_gets_ns_suffix(self):
        assert _yf_symbol("RELIANCE", "IN") == "RELIANCE.NS"

    def test_india_ticker_with_suffix_unchanged(self):
        assert _yf_symbol("RELIANCE.NS", "IN") == "RELIANCE.NS"

    def test_us_ticker_unchanged(self):
        assert _yf_symbol("NVDA", "US") == "NVDA"


class TestPiotroski:
    def test_full_score_9(self):
        info = {
            "netIncomeToCommon": 1000, "totalAssets": 5000,
            "operatingCashflow": 1200, "grossMargins": 0.7,
            "revenueGrowth": 0.1, "debtToEquity": 50,
            "currentRatio": 1.5, "returnOnEquity": 0.15,
            "freeCashflow": 500,
        }
        assert _piotroski_from_info(info) == 9

    def test_zero_score_bad_fundamentals(self):
        info = {
            "netIncomeToCommon": -100, "totalAssets": 5000,
            "operatingCashflow": -200, "grossMargins": -0.1,
            "revenueGrowth": -0.2, "debtToEquity": 200,
            "currentRatio": 0.5, "returnOnEquity": -0.1,
            "freeCashflow": -300,
        }
        assert _piotroski_from_info(info) == 0


class TestBuildFundamentalsRow:
    def test_returns_required_keys(self):
        mock_info = {
            "grossMargins": 0.5, "shortPercentOfFloat": 0.05,
            "netIncomeToCommon": 1000, "operatingCashflow": 800,
            "totalAssets": 10000, "trailingPE": 25, "priceToBook": 3,
            "beta": 1.1, "symbol": "NVDA",
        }
        with patch("src.data_fetcher.yf.Ticker") as mock_ticker:
            mock_t = MagicMock()
            mock_t.info = mock_info
            mock_t.history.return_value = pd.DataFrame()
            mock_ticker.return_value = mock_t
            row = build_fundamentals_row("NVDA", "US")
        required = {"gross_profit_margin", "accruals_ratio", "piotroski",
                    "momentum_raw", "short_interest_pct", "pe_ttm", "pb_ratio",
                    "beta", "realized_vol_1y"}
        assert required.issubset(set(row.keys()))

    def test_fallback_on_empty_yfinance(self):
        with patch("src.data_fetcher.yf.Ticker") as mock_ticker:
            mock_t = MagicMock()
            mock_t.info = {}
            mock_t.history.return_value = pd.DataFrame()
            mock_ticker.return_value = mock_t
            row = build_fundamentals_row("FAKE", "US")
        # Should not raise; should return synthetic row
        assert "gross_profit_margin" in row
        assert row.get("_is_real") is False