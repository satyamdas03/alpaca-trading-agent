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
        result = validate_input({"component_type": "resistor", "filters": {}})
        assert result["filters"] == {}

    def test_valid_resistor_filters(self):
        result = validate_input({
            "component_type": "resistor",
            "filters": {"resistance": "1k", "package": "0402", "tolerance": "1%"}
        })
        assert result["filters"]["resistance"] == "1k"

    def test_unknown_filter_key_stripped(self):
        result = validate_input({
            "component_type": "resistor",
            "filters": {"resistance": "1k", "__proto__": "bad", "constructor": "evil"}
        })
        assert "__proto__" not in result["filters"]
        assert "constructor" not in result["filters"]

    def test_filter_value_too_long_raises(self):
        with pytest.raises(ValidationError):
            validate_input({
                "component_type": "resistor",
                "filters": {"resistance": "A" * 100}
            })

    def test_filter_value_with_special_chars_raises(self):
        with pytest.raises(ValidationError):
            validate_input({
                "component_type": "resistor",
                "filters": {"resistance": "1k&foo=bar"}
            })


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
