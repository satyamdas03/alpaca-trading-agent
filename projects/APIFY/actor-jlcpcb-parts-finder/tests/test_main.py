import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.main import fetch_parts, build_url, parse_response

class TestBuildUrl:
    def test_resistor_no_filters(self):
        url = build_url("resistor", {})
        assert url == "https://jlcsearch.tscircuit.com/resistors/list.json"

    def test_resistor_with_filters(self):
        url = build_url("resistor", {"resistance": "1k", "package": "0402"})
        assert "resistance=1k" in url
        assert "package=0402" in url
        assert url.startswith("https://jlcsearch.tscircuit.com/resistors/list.json?")

    def test_component_type_pluralised(self):
        assert "capacitors" in build_url("capacitor", {})
        assert "inductors" in build_url("inductor", {})
        assert "leds" in build_url("led", {})
        assert "mosfets" in build_url("mosfet", {})
        assert "ics" in build_url("ic", {})

    def test_no_raw_user_input_in_url_path(self):
        url = build_url("resistor", {"resistance": "1k"})
        path = url.split("?")[0]
        assert "1k" not in path


class TestParseResponse:
    def test_parses_resistors_key(self):
        raw = {"resistors": [{"lcsc": 123, "mfr": "ABC", "package": "0402",
                              "resistance": 1000, "stock": 5000, "price1": 0.001}]}
        items = parse_response(raw, "resistor", max_results=10)
        assert len(items) == 1
        assert items[0]["lcsc"] == 123

    def test_respects_max_results(self):
        raw = {"resistors": [{"lcsc": i} for i in range(100)]}
        items = parse_response(raw, "resistor", max_results=10)
        assert len(items) == 10

    def test_empty_response_returns_empty_list(self):
        items = parse_response({}, "resistor", max_results=50)
        assert items == []

    def test_output_contains_no_internal_keys(self):
        raw = {"resistors": [{"lcsc": 1, "_internal": "secret", "stock": 100}]}
        items = parse_response(raw, "resistor", max_results=10)
        assert "_internal" not in items[0]
