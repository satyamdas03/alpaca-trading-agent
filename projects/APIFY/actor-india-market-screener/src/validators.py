"""Input validation for India Market Screener."""
from __future__ import annotations

VALID_MARKETS = frozenset(["India", "US", "both"])
VALID_SORT_BY = frozenset(["score", "momentum", "quality", "value"])


class ValidationError(ValueError):
    pass


def validate_input(raw: dict) -> dict:
    """Validate and sanitize actor input. Returns clean dict or raises ValidationError."""
    market = raw.get("market", "India")
    if market not in VALID_MARKETS:
        raise ValidationError(f"market must be one of {sorted(VALID_MARKETS)}, got: {market!r}")

    min_score = float(raw.get("min_score", 6.0))
    if min_score < 1 or min_score > 10:
        raise ValidationError("min_score must be between 1 and 10.")

    sort_by = raw.get("sort_by", "score")
    if sort_by not in VALID_SORT_BY:
        raise ValidationError(f"sort_by must be one of {sorted(VALID_SORT_BY)}, got: {sort_by!r}")

    top_n = int(raw.get("top_n", 20))
    if top_n < 1 or top_n > 100:
        raise ValidationError("top_n must be between 1 and 100.")

    return {"market": market, "min_score": min_score, "sort_by": sort_by, "top_n": top_n}