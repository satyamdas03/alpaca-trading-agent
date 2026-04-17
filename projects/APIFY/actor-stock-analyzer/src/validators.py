"""Input validation for NeuralQuant Stock Analyzer."""
from __future__ import annotations
import re

_TICKER_RE = re.compile(r"^[A-Z0-9.\-]{1,20}$")
VALID_MODES = frozenset(["quant", "full_ai"])
MAX_TICKERS = 50


class ValidationError(ValueError):
    pass


def validate_input(raw: dict) -> dict:
    """Validate and sanitize actor input. Returns clean dict or raises ValidationError."""
    # --- tickers ---
    tickers_raw = raw.get("tickers")
    if not tickers_raw or not isinstance(tickers_raw, list):
        raise ValidationError("tickers is required and must be a non-empty list.")
    tickers = []
    seen = set()
    for t in tickers_raw:
        if not isinstance(t, str):
            continue
        t = t.strip().upper()
        if not t:
            continue
        if not _TICKER_RE.match(t):
            raise ValidationError(
                f"Invalid ticker {t!r}. Allowed: A-Z, 0-9, '.', '-', max 20 chars."
            )
        if t not in seen:
            seen.add(t)
            tickers.append(t)
    if not tickers:
        raise ValidationError("tickers list is empty after sanitization.")
    if len(tickers) > MAX_TICKERS:
        raise ValidationError(f"Max {MAX_TICKERS} tickers per run, got {len(tickers)}.")

    # --- mode ---
    mode = raw.get("mode", "quant")
    if not isinstance(mode, str) or mode not in VALID_MODES:
        raise ValidationError(f"mode must be one of {sorted(VALID_MODES)}, got: {mode!r}")

    # --- max_spend_usd ---
    max_spend = raw.get("max_spend_usd", 2.0)
    try:
        max_spend = float(max_spend)
    except (TypeError, ValueError):
        raise ValidationError("max_spend_usd must be a number.")
    if max_spend < 0:
        raise ValidationError("max_spend_usd must be >= 0.")

    return {"tickers": tickers, "mode": mode, "max_spend_usd": max_spend}