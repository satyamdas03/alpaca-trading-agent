import pytest
from src.validators import validate_input, ValidationError

class TestComponentType:
    def test_valid_resistor(self):
        result = validate_input({"component_type": "resistor"})
        assert result["component_type"] == "resistor"

    def test_valid_all_types(self):
        for t in ["resistor", "capacitor", "inductor", "led", "mosfet", "ic"]:
            result = validate_input({"component_type": t})
            assert result["component_type"] == t

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError, match="component_type"):
            validate_input({"component_type": "transistor"})

    def test_missing_type_raises(self):
        with pytest.raises(ValidationError, match="component_type"):
            validate_input({})

    def test_injection_attempt_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"component_type": "resistor; DROP TABLE parts--"})


class TestFilters:
    def test_empty_filters_allowed(self):
        result = validate_input({"component_type": "resistor"})
        assert result["filters"] == {}

    def test_valid_resistor_filters_flat(self):
        result = validate_input({
            "component_type": "resistor",
            "resistance": "1k",
            "package": "0402",
            "tolerance": "1%"
        })
        assert result["filters"]["resistance"] == "1k"
        assert result["filters"]["package"] == "0402"

    def test_unknown_filter_field_stripped(self):
        result = validate_input({
            "component_type": "resistor",
            "resistance": "1k",
            "capacitance": "100n"  # not valid for resistors
        })
        assert "capacitance" not in result["filters"]
        assert "resistance" in result["filters"]

    def test_empty_string_fields_ignored(self):
        result = validate_input({
            "component_type": "resistor",
            "resistance": "1k",
            "package": ""  # empty = no filter
        })
        assert "package" not in result["filters"]

    def test_filter_value_too_long_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"component_type": "resistor", "resistance": "A" * 100})

    def test_filter_value_with_special_chars_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"component_type": "resistor", "resistance": "1k&foo=bar"})

    def test_capacitor_filters(self):
        result = validate_input({
            "component_type": "capacitor",
            "capacitance": "100n",
            "voltage": "50V"
        })
        assert result["filters"]["capacitance"] == "100n"
        assert result["filters"]["voltage"] == "50V"


class TestMaxResults:
    def test_default_max_results(self):
        result = validate_input({"component_type": "resistor"})
        assert result["max_results"] == 50

    def test_custom_max_results(self):
        result = validate_input({"component_type": "resistor", "max_results": 200})
        assert result["max_results"] == 200

    def test_max_results_exceeding_cap_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"component_type": "resistor", "max_results": 501})

    def test_max_results_zero_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"component_type": "resistor", "max_results": 0})