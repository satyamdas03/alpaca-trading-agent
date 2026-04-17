"""Input validation for JLCPCB Parts Finder. All user input validated here before any external call."""
from __future__ import annotations
import re

VALID_COMPONENT_TYPES = frozenset(["resistor", "capacitor", "inductor", "led", "mosfet", "ic"])

# Per-component allowed filter keys — strict allowlist, nothing else passes
ALLOWED_FILTER_KEYS: dict[str, frozenset] = {
    "resistor":  frozenset(["resistance", "package", "tolerance", "power"]),
    "capacitor": frozenset(["capacitance", "package", "voltage", "tolerance"]),
    "inductor":  frozenset(["inductance", "package", "current", "tolerance"]),
    "led":       frozenset(["color", "package", "voltage", "current"]),
    "mosfet":    frozenset(["package", "voltage", "current", "channel_type"]),
    "ic":        frozenset(["package", "manufacturer", "category"]),
}

# All possible flat filter field names from input schema
_ALL_FILTER_FIELDS = frozenset(
    ["resistance", "capacitance", "inductance", "package", "tolerance", "voltage",
     "power", "current", "color", "channel_type", "manufacturer", "category"]
)

# Filter values: alphanumeric + a handful of safe unit chars only
_FILTER_VALUE_RE = re.compile(r"^[A-Za-z0-9\s%.µΩ/\-]{1,40}$")
_MAX_FILTER_VALUE_LEN = 40


class ValidationError(ValueError):
    pass


def validate_input(raw: dict) -> dict:
    """Validate and sanitize actor input. Returns clean dict or raises ValidationError."""
    # --- component_type ---
    ct = raw.get("component_type")
    if not ct or not isinstance(ct, str):
        raise ValidationError("component_type is required and must be a string.")
    ct = ct.strip().lower()
    if ct not in VALID_COMPONENT_TYPES:
        raise ValidationError(
            f"component_type must be one of {sorted(VALID_COMPONENT_TYPES)}, got: {ct!r}"
        )

    # --- filters (flat fields from input schema) ---
    allowed_keys = ALLOWED_FILTER_KEYS[ct]
    clean_filters: dict[str, str] = {}
    for key in _ALL_FILTER_FIELDS:
        value = raw.get(key, "")
        if not value:
            continue
        if not isinstance(value, str):
            value = str(value)
        value = value.strip()
        if not value:
            continue
        if key not in allowed_keys:
            continue  # silently ignore fields not relevant to this component type
        if len(value) > _MAX_FILTER_VALUE_LEN:
            raise ValidationError(
                f"Filter value for '{key}' too long (max {_MAX_FILTER_VALUE_LEN} chars)."
            )
        if not _FILTER_VALUE_RE.match(value):
            raise ValidationError(
                f"Filter value for '{key}' contains invalid characters: {value!r}"
            )
        clean_filters[key] = value

    # --- max_results ---
    max_results = raw.get("max_results", 50)
    if isinstance(max_results, bool):
        raise ValidationError("max_results must be an integer.")
    if not isinstance(max_results, int):
        try:
            max_results = int(max_results)
        except (ValueError, TypeError):
            raise ValidationError("max_results must be an integer.")
    if max_results < 1 or max_results > 500:
        raise ValidationError("max_results must be between 1 and 500.")

    return {"component_type": ct, "filters": clean_filters, "max_results": max_results}