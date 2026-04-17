import pytest
from unittest.mock import MagicMock, patch
from src.debate_engine import parse_agent_output, build_macro_context, AgentResult

class TestParseAgentOutput:
    def test_parses_valid_output(self):
        raw = """STANCE: BULL
CONVICTION: HIGH
THESIS: Strong fundamentals support upside.
KEY_POINTS:
- P/E of 25x is below sector average
- Piotroski score of 8 indicates quality earnings
- Momentum percentile 0.82 shows strong trend"""
        result = parse_agent_output(raw, "MACRO")
        assert result.stance == "BULL"
        assert result.conviction == "HIGH"
        assert "Strong fundamentals" in result.thesis
        assert len(result.key_points) >= 1

    def test_invalid_stance_returns_neutral(self):
        result = parse_agent_output("STANCE: CONFUSED\nCONVICTION: HIGH\nTHESIS: x", "MACRO")
        assert result.stance == "NEUTRAL"

    def test_missing_fields_returns_neutral_fallback(self):
        result = parse_agent_output("completely garbled output", "FUNDAMENTAL")
        assert result.stance == "NEUTRAL"
        assert result.conviction == "LOW"
        assert result.agent == "FUNDAMENTAL"

    def test_adversarial_bull_overridden_to_bear(self):
        raw = "STANCE: BULL\nCONVICTION: HIGH\nTHESIS: x\nKEY_POINTS:\n- y"
        result = parse_agent_output(raw, "ADVERSARIAL")
        assert result.stance == "BEAR"

    def test_thesis_truncated_to_500_chars(self):
        raw = f"STANCE: NEUTRAL\nCONVICTION: LOW\nTHESIS: {'x' * 1000}\nKEY_POINTS:\n- y"
        result = parse_agent_output(raw, "MACRO")
        assert len(result.thesis) <= 500


class TestBuildMacroContext:
    def test_returns_dict_with_required_keys(self):
        from src.signal_engine import MacroSnapshot
        ctx = build_macro_context(MacroSnapshot())
        for key in ["vix", "ism_pmi", "hy_spread_oas", "yield_10y", "cpi_yoy", "fed_funds_rate"]:
            assert key in ctx

    def test_values_are_float_or_string(self):
        from src.signal_engine import MacroSnapshot
        ctx = build_macro_context(MacroSnapshot())
        for v in ctx.values():
            assert isinstance(v, (int, float, str))