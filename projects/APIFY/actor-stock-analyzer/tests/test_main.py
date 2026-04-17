import pytest
import pandas as pd
from unittest.mock import AsyncMock, patch, MagicMock
from src.main import build_output_row, detect_market

class TestDetectMarket:
    def test_ns_suffix_is_india(self):
        assert detect_market("RELIANCE.NS") == "IN"

    def test_no_suffix_is_us(self):
        assert detect_market("NVDA") == "US"

    def test_bse_suffix_is_india(self):
        assert detect_market("INFY.BO") == "IN"


class TestBuildOutputRow:
    def _make_row(self):
        return pd.Series({
            "ticker": "NVDA",
            "composite_score": 0.71,
            "score_1_10": 8,
            "quality_percentile": 0.85,
            "momentum_percentile": 0.80,
            "value_percentile": 0.60,
            "low_vol_percentile": 0.55,
            "short_interest_percentile": 0.70,
        })

    def test_contains_required_keys(self):
        fund = {"current_price": 900.0, "long_name": "NVIDIA", "_is_real": True}
        from src.signal_engine import MacroSnapshot
        row = build_output_row(self._make_row(), fund, "US", MacroSnapshot(), debate=None)
        for key in ["ticker", "market", "ai_score", "score_components", "recommendation"]:
            assert key in row

    def test_no_private_keys_in_output(self):
        fund = {"current_price": 900.0, "long_name": "NVIDIA", "_is_real": True}
        from src.signal_engine import MacroSnapshot
        row = build_output_row(self._make_row(), fund, "US", MacroSnapshot(), debate=None)
        for key in row:
            assert not key.startswith("_"), f"Private key leaked: {key}"

    def test_debate_fields_absent_when_none(self):
        fund = {"_is_real": True}
        from src.signal_engine import MacroSnapshot
        row = build_output_row(self._make_row(), fund, "US", MacroSnapshot(), debate=None)
        assert "debate_verdict" not in row
        assert "agent_outputs" not in row