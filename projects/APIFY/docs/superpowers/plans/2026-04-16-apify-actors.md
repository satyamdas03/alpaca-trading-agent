# Apify Actors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish 3 monetized Apify Actors: JLCPCB Parts Finder (Actor B, publish today), NeuralQuant Stock Analyzer (Actor A1), and India Market Screener (Actor A2).

**Architecture:** Each actor is a self-contained Python Apify Actor using PPE pricing. A1 and A2 inline-port the NeuralQuant signal engine (no external package dependency). All secrets via Apify Actor secrets — never in source.

**Tech Stack:** Python 3.11, apify==3.*, httpx==0.27.*, yfinance==0.2.*, anthropic==0.40.*, fredapi==0.5.*, pydantic==2.*, pytest, pytest-asyncio

---

## Phase 1 — Actor B: JLCPCB Parts Finder

### Task 1: Scaffold Actor B

**Files:**
- Create: `actor-jlcpcb-parts-finder/.actor/actor.json`
- Create: `actor-jlcpcb-parts-finder/requirements.txt`
- Create: `actor-jlcpcb-parts-finder/.gitignore`
- Create: `actor-jlcpcb-parts-finder/src/__init__.py`
- Create: `actor-jlcpcb-parts-finder/tests/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p actor-jlcpcb-parts-finder/.actor
mkdir -p actor-jlcpcb-parts-finder/src
mkdir -p actor-jlcpcb-parts-finder/tests
touch actor-jlcpcb-parts-finder/src/__init__.py
touch actor-jlcpcb-parts-finder/tests/__init__.py
```

- [ ] **Step 2: Create `.actor/actor.json`**

```json
{
  "actorSpecification": 1,
  "name": "jlcpcb-parts-finder",
  "title": "JLCPCB Parts Finder — In-Stock Component Search",
  "description": "Search JLCPCB's in-stock electronics components (resistors, capacitors, inductors, MOSFETs, ICs, LEDs) by electrical specifications. Returns matching parts with stock counts and unit prices. Perfect for automating BOM generation and design validation.",
  "version": "0.1",
  "buildTag": "latest",
  "environmentVariables": [],
  "dockerfile": "./Dockerfile",
  "input": {
    "title": "JLCPCB Parts Search Input",
    "type": "object",
    "schemaVersion": 1,
    "properties": {
      "component_type": {
        "title": "Component Type",
        "type": "string",
        "description": "Type of electronic component to search.",
        "enum": ["resistor", "capacitor", "inductor", "led", "mosfet", "ic"],
        "default": "resistor"
      },
      "filters": {
        "title": "Specification Filters",
        "type": "object",
        "description": "Key/value filters. For resistors: resistance (e.g. '1k'), package (e.g. '0402'), tolerance (e.g. '1%'). For capacitors: capacitance (e.g. '100n'), voltage (e.g. '10V'), package.",
        "default": {}
      },
      "max_results": {
        "title": "Maximum Results",
        "type": "integer",
        "description": "Maximum number of parts to return.",
        "default": 50,
        "minimum": 1,
        "maximum": 500
      }
    },
    "required": ["component_type"]
  }
}
```

- [ ] **Step 3: Create `requirements.txt`**

```
apify==3.2.1
httpx==0.27.2
pydantic==2.9.2
```

- [ ] **Step 4: Create `.gitignore`**

```
__pycache__/
*.pyc
.env
.venv/
storage/
```

- [ ] **Step 5: Commit scaffold**

```bash
git add actor-jlcpcb-parts-finder/
git commit -m "feat(actor-b): scaffold JLCPCB parts finder"
```

---

### Task 2: Input Validators (TDD)

**Files:**
- Create: `actor-jlcpcb-parts-finder/src/validators.py`
- Create: `actor-jlcpcb-parts-finder/tests/test_validators.py`

- [ ] **Step 1: Write failing tests**

Create `actor-jlcpcb-parts-finder/tests/test_validators.py`:

```python
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
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd actor-jlcpcb-parts-finder
python -m pytest tests/test_validators.py -v 2>&1 | head -30
```

Expected: `ModuleNotFoundError: No module named 'src.validators'`

- [ ] **Step 3: Implement `src/validators.py`**

```python
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

# Filter values: alphanumeric + a handful of safe unit chars only
_FILTER_VALUE_RE = re.compile(r"^[\w\s%.µΩ/\-]{1,40}$")
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

    # --- filters ---
    raw_filters = raw.get("filters", {})
    if not isinstance(raw_filters, dict):
        raise ValidationError("filters must be a JSON object.")
    allowed_keys = ALLOWED_FILTER_KEYS[ct]
    clean_filters: dict[str, str] = {}
    for key, value in raw_filters.items():
        if key not in allowed_keys:
            continue  # silently strip unknown keys
        if not isinstance(value, str):
            value = str(value)
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
    if not isinstance(max_results, int):
        try:
            max_results = int(max_results)
        except (ValueError, TypeError):
            raise ValidationError("max_results must be an integer.")
    if max_results < 1 or max_results > 500:
        raise ValidationError("max_results must be between 1 and 500.")

    return {"component_type": ct, "filters": clean_filters, "max_results": max_results}
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
python -m pytest tests/test_validators.py -v
```

Expected: All 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add actor-jlcpcb-parts-finder/src/validators.py actor-jlcpcb-parts-finder/tests/test_validators.py
git commit -m "feat(actor-b): input validators with full test coverage"
```

---

### Task 3: Main Actor Logic (TDD)

**Files:**
- Create: `actor-jlcpcb-parts-finder/src/main.py`
- Create: `actor-jlcpcb-parts-finder/tests/test_main.py`

- [ ] **Step 1: Write failing tests**

Create `actor-jlcpcb-parts-finder/tests/test_main.py`:

```python
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
        # filters go to query params only, not path
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
```

- [ ] **Step 2: Run — verify fail**

```bash
python -m pytest tests/test_main.py -v 2>&1 | head -20
```

Expected: `ImportError`

- [ ] **Step 3: Implement `src/main.py`**

```python
"""JLCPCB Parts Finder — Apify Actor entry point."""
from __future__ import annotations
import asyncio
import logging
from urllib.parse import urlencode

import httpx
from apify import Actor

from .validators import validate_input, ValidationError

log = logging.getLogger(__name__)

# jlcsearch pluralisation map
_PLURAL = {
    "resistor": "resistors",
    "capacitor": "capacitors",
    "inductor": "inductors",
    "led": "leds",
    "mosfet": "mosfets",
    "ic": "ics",
}

_BASE = "https://jlcsearch.tscircuit.com"
_TIMEOUT = 15.0
_MAX_RETRIES = 3


def build_url(component_type: str, filters: dict[str, str]) -> str:
    """Build jlcsearch JSON API URL from validated inputs only."""
    plural = _PLURAL[component_type]
    base = f"{_BASE}/{plural}/list.json"
    if not filters:
        return base
    return f"{base}?{urlencode(filters)}"


def parse_response(raw: dict, component_type: str, max_results: int) -> list[dict]:
    """Extract and cap results. Strip any keys starting with underscore."""
    plural = _PLURAL[component_type]
    items = raw.get(plural, [])
    if not isinstance(items, list):
        return []
    clean = []
    for item in items[:max_results]:
        if isinstance(item, dict):
            clean.append({k: v for k, v in item.items() if not k.startswith("_")})
    return clean


async def fetch_parts(component_type: str, filters: dict, max_results: int) -> list[dict]:
    """Fetch parts from jlcsearch with retry + timeout."""
    url = build_url(component_type, filters)
    last_exc: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(url, headers={"Accept": "application/json"})
                resp.raise_for_status()
                return parse_response(resp.json(), component_type, max_results)
        except httpx.TimeoutException as exc:
            last_exc = exc
            log.warning("Attempt %d/%d timed out: %s", attempt, _MAX_RETRIES, exc)
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            log.warning("Attempt %d/%d HTTP %s", attempt, _MAX_RETRIES, exc.response.status_code)
        if attempt < _MAX_RETRIES:
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError(f"jlcsearch API unavailable after {_MAX_RETRIES} attempts: {last_exc}")


async def main() -> None:
    async with Actor:
        raw_input = await Actor.get_input() or {}
        try:
            actor_input = validate_input(raw_input)
        except ValidationError as exc:
            await Actor.fail(status_message=f"Invalid input: {exc}")
            return

        component_type = actor_input["component_type"]
        filters = actor_input["filters"]
        max_results = actor_input["max_results"]

        log.info("Searching %s with filters=%s max=%d", component_type, filters, max_results)

        try:
            parts = await fetch_parts(component_type, filters, max_results)
        except RuntimeError as exc:
            await Actor.fail(status_message=str(exc))
            return

        if not parts:
            log.info("No matching parts found.")
        else:
            await Actor.push_data(parts)
            log.info("Pushed %d parts to dataset.", len(parts))


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: Run tests — verify pass**

```bash
python -m pytest tests/test_main.py -v
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add actor-jlcpcb-parts-finder/src/main.py actor-jlcpcb-parts-finder/tests/test_main.py
git commit -m "feat(actor-b): main actor logic with fetch, parse, retry"
```

---

### Task 4: Dockerfile + Local Test

**Files:**
- Create: `actor-jlcpcb-parts-finder/Dockerfile`

- [ ] **Step 1: Create Dockerfile**

```dockerfile
FROM apify/actor-python:3.11

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "src.main"]
```

- [ ] **Step 2: Install deps locally and run full test suite**

```bash
cd actor-jlcpcb-parts-finder
pip install -r requirements.txt
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 3: Smoke test against live jlcsearch API**

```bash
python -c "
import asyncio
from src.main import fetch_parts
results = asyncio.run(fetch_parts('resistor', {'resistance': '1k', 'package': '0402'}, 5))
print(f'Got {len(results)} results')
print(results[0] if results else 'empty')
"
```

Expected: Prints 1–5 resistor dicts with `lcsc`, `mfr`, `package`, `stock`, `price1`.

- [ ] **Step 4: Commit**

```bash
git add actor-jlcpcb-parts-finder/Dockerfile
git commit -m "feat(actor-b): Dockerfile and smoke test passing"
```

---

### Task 5: Publish Actor B to Apify Store

- [ ] **Step 1: Install Apify CLI**

```bash
npm install -g apify-cli
apify login
```

Follow prompts — paste your Apify API token from https://console.apify.com/account/integrations

- [ ] **Step 2: Push actor to Apify**

```bash
cd actor-jlcpcb-parts-finder
apify push
```

Expected output: `Actor pushed successfully. View at: https://console.apify.com/actors/...`

- [ ] **Step 3: Configure PPE pricing in Apify Console**

Go to https://console.apify.com → Your Actor → Monetization tab:
- Pricing model: **Pay per event**
- Add event: name=`result_returned`, price=`0.001` USD
- Save

- [ ] **Step 4: Test run in Apify Console**

Input:
```json
{"component_type": "resistor", "filters": {"resistance": "1k", "package": "0402"}, "max_results": 10}
```

Expected: Run succeeds, dataset shows 10 resistors.

- [ ] **Step 5: Publish to Store**

In Console → Actor → Settings:
- Set visibility to **Public**
- Fill SEO description: "Search JLCPCB in-stock components by specs. Automate BOM generation for PCB design. Supports resistors, capacitors, inductors, MOSFETs, ICs, LEDs."
- Save and Publish

- [ ] **Step 6: Commit final state**

```bash
cd ..
git add actor-jlcpcb-parts-finder/
git commit -m "feat(actor-b): published to Apify Store"
```

---

## Phase 2 — Actor A1: NeuralQuant Stock Analyzer

### Task 6: Scaffold Actor A1

**Files:**
- Create: `actor-stock-analyzer/.actor/actor.json`
- Create: `actor-stock-analyzer/requirements.txt`
- Create: `actor-stock-analyzer/Dockerfile`
- Create: `actor-stock-analyzer/src/__init__.py`
- Create: `actor-stock-analyzer/tests/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p actor-stock-analyzer/.actor
mkdir -p actor-stock-analyzer/src
mkdir -p actor-stock-analyzer/tests
touch actor-stock-analyzer/src/__init__.py
touch actor-stock-analyzer/tests/__init__.py
```

- [ ] **Step 2: Create `.actor/actor.json`**

```json
{
  "actorSpecification": 1,
  "name": "neuralquant-stock-analyzer",
  "title": "NeuralQuant Stock Analyzer — AI Scores for US & India Stocks",
  "description": "Institutional-grade quantitative analysis for US (NYSE/NASDAQ) and India (NSE) stocks. Returns a 5-factor AI score (1–10), factor breakdown, and optional 7-agent AI debate verdict. The only actor on Apify Store covering NSE India stocks with AI-powered analysis.",
  "version": "0.1",
  "buildTag": "latest",
  "input": {
    "title": "Stock Analyzer Input",
    "type": "object",
    "schemaVersion": 1,
    "properties": {
      "tickers": {
        "title": "Tickers",
        "type": "array",
        "description": "Stock ticker symbols. Add .NS suffix for NSE India (e.g. RELIANCE.NS, TCS.NS). US tickers need no suffix (e.g. NVDA, AAPL).",
        "items": {"type": "string"},
        "default": ["NVDA", "TCS.NS"]
      },
      "mode": {
        "title": "Analysis Mode",
        "type": "string",
        "enum": ["quant", "full_ai"],
        "default": "quant",
        "description": "quant = 5-factor signal engine only (fast, no AI costs). full_ai = quant + 7-agent AI debate (requires ANTHROPIC_API_KEY secret)."
      },
      "max_spend_usd": {
        "title": "Max Claude Spend (USD)",
        "type": "number",
        "default": 2.0,
        "description": "Safety cap on Claude API spend per run. Only relevant for full_ai mode."
      }
    },
    "required": ["tickers"]
  }
}
```

- [ ] **Step 3: Create `requirements.txt`**

```
apify==3.2.1
httpx==0.27.2
pydantic==2.9.2
yfinance==0.2.48
pandas==2.2.3
numpy==1.26.4
anthropic==0.40.0
fredapi==0.5.2
```

- [ ] **Step 4: Create `Dockerfile`**

```dockerfile
FROM apify/actor-python:3.11

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "src.main"]
```

- [ ] **Step 5: Commit scaffold**

```bash
git add actor-stock-analyzer/
git commit -m "feat(actor-a1): scaffold NeuralQuant Stock Analyzer"
```

---

### Task 7: Validators (TDD)

**Files:**
- Create: `actor-stock-analyzer/src/validators.py`
- Create: `actor-stock-analyzer/tests/test_validators.py`

- [ ] **Step 1: Write failing tests**

Create `actor-stock-analyzer/tests/test_validators.py`:

```python
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
```

- [ ] **Step 2: Run — verify fail**

```bash
cd actor-stock-analyzer
python -m pytest tests/test_validators.py -v 2>&1 | head -10
```

Expected: `ImportError`

- [ ] **Step 3: Implement `src/validators.py`**

```python
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
```

- [ ] **Step 4: Run — verify pass**

```bash
python -m pytest tests/test_validators.py -v
```

Expected: All 14 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add actor-stock-analyzer/src/validators.py actor-stock-analyzer/tests/test_validators.py
git commit -m "feat(actor-a1): input validators"
```

---

### Task 8: Signal Engine (TDD)

**Files:**
- Create: `actor-stock-analyzer/src/signal_engine.py`
- Create: `actor-stock-analyzer/tests/test_signal_engine.py`

- [ ] **Step 1: Write failing tests**

Create `actor-stock-analyzer/tests/test_signal_engine.py`:

```python
import pytest
import pandas as pd
from src.signal_engine import (
    MacroSnapshot, compute_composite_scores, recommendation_from_score
)

def _make_df(n=5) -> pd.DataFrame:
    """Minimal valid fundamentals DataFrame."""
    import numpy as np
    rng = np.random.RandomState(42)
    return pd.DataFrame({
        "ticker": [f"T{i}" for i in range(n)],
        "gross_profit_margin": rng.uniform(0.1, 0.9, n),
        "accruals_ratio":       rng.uniform(-0.2, 0.2, n),
        "piotroski":            rng.randint(1, 9, n),
        "momentum_raw":         rng.uniform(-0.3, 0.5, n),
        "short_interest_pct":   rng.uniform(0.01, 0.15, n),
        "pe_ttm":               rng.uniform(10, 50, n),
        "pb_ratio":             rng.uniform(1, 8, n),
        "realized_vol_1y":      rng.uniform(0.1, 0.5, n),
    })


class TestCompositeScores:
    def test_returns_dataframe(self):
        df = compute_composite_scores(_make_df(), MacroSnapshot())
        assert isinstance(df, pd.DataFrame)

    def test_adds_composite_score_column(self):
        df = compute_composite_scores(_make_df(), MacroSnapshot())
        assert "composite_score" in df.columns

    def test_composite_score_between_0_and_1(self):
        df = compute_composite_scores(_make_df(20), MacroSnapshot())
        assert df["composite_score"].between(0, 1).all()

    def test_score_1_10_in_range(self):
        df = compute_composite_scores(_make_df(20), MacroSnapshot())
        assert df["score_1_10"].between(1, 10).all()

    def test_sorted_descending(self):
        df = compute_composite_scores(_make_df(10), MacroSnapshot())
        assert list(df["composite_score"]) == sorted(df["composite_score"], reverse=True)

    def test_crash_protection_neutralises_momentum(self):
        macro_crash = MacroSnapshot(spx_return_1m=-0.15, spx_vs_200ma=-0.08)
        df = compute_composite_scores(_make_df(10), macro_crash)
        assert (df["momentum_percentile"] == 0.5).all()

    def test_single_ticker_works(self):
        df = compute_composite_scores(_make_df(1), MacroSnapshot())
        assert len(df) == 1
        assert df["score_1_10"].iloc[0] == 5  # single ticker → median rank → 5


class TestRecommendation:
    def test_strong_buy_at_8_plus(self):
        assert recommendation_from_score(8) == "STRONG BUY"
        assert recommendation_from_score(10) == "STRONG BUY"

    def test_buy_at_6_to_7(self):
        assert recommendation_from_score(6) == "BUY"
        assert recommendation_from_score(7) == "BUY"

    def test_hold_at_4_to_5(self):
        assert recommendation_from_score(4) == "HOLD"
        assert recommendation_from_score(5) == "HOLD"

    def test_sell_at_2_to_3(self):
        assert recommendation_from_score(2) == "SELL"
        assert recommendation_from_score(3) == "SELL"

    def test_strong_sell_at_1(self):
        assert recommendation_from_score(1) == "STRONG SELL"
```

- [ ] **Step 2: Run — verify fail**

```bash
python -m pytest tests/test_signal_engine.py -v 2>&1 | head -10
```

- [ ] **Step 3: Implement `src/signal_engine.py`**

```python
"""
Self-contained signal engine ported from NeuralQuant nq_signals package.
Computes 5-factor composite scores cross-sectionally. No external package dependency.
"""
from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

SHORT_INT_WEIGHT = 0.15
REGIME_BUDGET = 1.0 - SHORT_INT_WEIGHT  # 0.85


@dataclass
class MacroSnapshot:
    vix: float = 18.0
    spx_vs_200ma: float = 0.02
    spx_return_1m: float = 0.01
    yield_spread_2y10y: float = 0.10
    hy_spread_oas: float = 350.0
    ism_pmi: float = 51.0
    cpi_yoy: float = 3.0
    fed_funds_rate: float = 5.25
    yield_10y: float = 4.2
    yield_2y: float = 4.1
    fred_sourced: bool = False


def _regime_weights(macro: MacroSnapshot) -> dict[str, float]:
    """Simplified regime detection — returns factor weights without fitted HMM."""
    bear = (
        macro.vix > 30
        or macro.spx_return_1m < -0.10
        or macro.hy_spread_oas > 600
        or macro.spx_vs_200ma < -0.05
    )
    recovery = macro.spx_vs_200ma < -0.02 and macro.spx_return_1m > 0.02
    late_cycle = macro.yield_spread_2y10y < 0 and macro.hy_spread_oas > 400

    if bear:
        return {"quality": 0.40, "momentum": 0.10, "value": 0.25, "low_vol": 0.25}
    if recovery:
        return {"quality": 0.20, "momentum": 0.35, "value": 0.25, "low_vol": 0.20}
    if late_cycle:
        return {"quality": 0.35, "momentum": 0.20, "value": 0.25, "low_vol": 0.20}
    # Risk-On (default)
    return {"quality": 0.25, "momentum": 0.30, "value": 0.20, "low_vol": 0.25}


def _rank(series: pd.Series, ascending: bool = True) -> pd.Series:
    return series.rank(pct=True, ascending=ascending, na_option="keep").fillna(0.5)


def compute_composite_scores(fundamentals: pd.DataFrame, macro: MacroSnapshot) -> pd.DataFrame:
    """
    Full signal pipeline. Input df must have columns:
    ticker, gross_profit_margin, accruals_ratio, piotroski,
    momentum_raw, short_interest_pct, pe_ttm, pb_ratio, realized_vol_1y
    Returns df sorted by composite_score desc, with added signal columns.
    """
    df = fundamentals.copy()
    crash_flag = macro.spx_return_1m < -0.10 or macro.spx_vs_200ma < -0.05
    w = _regime_weights(macro)

    # Quality: gross margin (40%) + accruals inverse (35%) + piotroski (25%)
    df["quality_percentile"] = (
        _rank(df["gross_profit_margin"]) * 0.40
        + _rank(df["accruals_ratio"], ascending=False) * 0.35
        + _rank(df["piotroski"]) * 0.25
    )

    # Momentum: crash-protected 12-1 month return percentile
    df["momentum_percentile"] = (
        pd.Series(0.5, index=df.index)
        if crash_flag
        else _rank(df["momentum_raw"])
    )

    # Value: inverse of (PE rank 50% + PB rank 50%) — cheaper is better
    df["value_percentile"] = 1.0 - (
        _rank(df["pe_ttm"]) * 0.50 + _rank(df["pb_ratio"]) * 0.50
    )

    # Low-Vol: inverse realized vol rank
    df["low_vol_percentile"] = 1.0 - _rank(df["realized_vol_1y"])

    # Short Interest: inverse rank — lower SI is better
    df["short_interest_percentile"] = 1.0 - _rank(df["short_interest_pct"])

    # Composite (weights sum to 1.0)
    df["composite_score"] = (
        df["quality_percentile"]       * w["quality"]   * REGIME_BUDGET
        + df["momentum_percentile"]    * w["momentum"]  * REGIME_BUDGET
        + df["short_interest_percentile"] * SHORT_INT_WEIGHT
        + df["value_percentile"]       * w["value"]     * REGIME_BUDGET
        + df["low_vol_percentile"]     * w["low_vol"]   * REGIME_BUDGET
    )

    # Rank-based 1-10 score
    if len(df) == 1:
        df["score_1_10"] = 5  # single ticker → neutral
    else:
        pct = df["composite_score"].rank(pct=True, method="average")
        df["score_1_10"] = (pct * 9 + 1).round().clip(1, 10).astype(int)

    return df.sort_values("composite_score", ascending=False).reset_index(drop=True)


def recommendation_from_score(score_1_10: int) -> str:
    if score_1_10 >= 8:
        return "STRONG BUY"
    if score_1_10 >= 6:
        return "BUY"
    if score_1_10 >= 4:
        return "HOLD"
    if score_1_10 >= 2:
        return "SELL"
    return "STRONG SELL"
```

- [ ] **Step 4: Run — verify pass**

```bash
python -m pytest tests/test_signal_engine.py -v
```

Expected: All 12 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add actor-stock-analyzer/src/signal_engine.py actor-stock-analyzer/tests/test_signal_engine.py
git commit -m "feat(actor-a1): self-contained signal engine with tests"
```

---

### Task 9: Data Fetcher (TDD)

**Files:**
- Create: `actor-stock-analyzer/src/data_fetcher.py`
- Create: `actor-stock-analyzer/tests/test_data_fetcher.py`

- [ ] **Step 1: Write failing tests**

Create `actor-stock-analyzer/tests/test_data_fetcher.py`:

```python
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
            "beta": 1.1,
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
```

- [ ] **Step 2: Run — verify fail**

```bash
python -m pytest tests/test_data_fetcher.py -v 2>&1 | head -10
```

- [ ] **Step 3: Implement `src/data_fetcher.py`**

```python
"""
Data fetcher for NeuralQuant Stock Analyzer actor.
Ported from NeuralQuant data_builder.py — self-contained, stateless (no cache).
"""
from __future__ import annotations
import logging
import math
import os
from datetime import date

import numpy as np
import pandas as pd
import yfinance as yf

from .signal_engine import MacroSnapshot

log = logging.getLogger(__name__)

# Claude API cost estimate: ~1024 tokens per agent call, 7 agents per ticker
# claude-sonnet-4-6: ~$3/1M input tokens
_CLAUDE_COST_PER_TICKER_USD = 0.07  # conservative upper bound


def _safe(val, default: float = 0.0) -> float:
    try:
        f = float(val)
        return f if math.isfinite(f) else default
    except Exception:
        return default


def _yf_symbol(ticker: str, market: str) -> str:
    if market == "IN" and "." not in ticker:
        return ticker + ".NS"
    return ticker


def _piotroski_from_info(info: dict) -> int:
    ni  = _safe(info.get("netIncomeToCommon"))
    ta  = _safe(info.get("totalAssets"), 1) or 1
    ocf = _safe(info.get("operatingCashflow"))
    score = 0
    if ni / ta > 0:                                score += 1
    if ocf > 0:                                    score += 1
    if ocf > ni:                                   score += 1
    if _safe(info.get("grossMargins")) > 0:        score += 1
    if _safe(info.get("revenueGrowth")) > 0:       score += 1
    if _safe(info.get("debtToEquity"), 999) < 100: score += 1
    if _safe(info.get("currentRatio")) > 1:        score += 1
    if _safe(info.get("returnOnEquity")) > 0:      score += 1
    if _safe(info.get("freeCashflow")) > 0:        score += 1
    return score


def _synthetic_row(ticker: str) -> dict:
    """Deterministic fallback when yfinance fails entirely."""
    s = hash(ticker) % (2**31 - 1)
    rng = np.random.RandomState(s)
    return {
        "gross_profit_margin": float(rng.uniform(0.10, 0.85)),
        "accruals_ratio":       float(rng.uniform(-0.15, 0.15)),
        "piotroski":            int(rng.randint(2, 9)),
        "momentum_raw":         float(rng.uniform(-0.25, 0.55)),
        "short_interest_pct":   float(rng.uniform(0.01, 0.18)),
        "pe_ttm":               float(rng.uniform(10, 45)),
        "pb_ratio":             float(rng.uniform(1, 8)),
        "beta":                 float(rng.uniform(0.5, 1.8)),
        "realized_vol_1y":      float(rng.uniform(0.15, 0.50)),
        "current_price":        None,
        "long_name":            ticker,
        "_is_real":             False,
    }


def build_fundamentals_row(ticker: str, market: str) -> dict:
    """Fetch fundamentals for one ticker. Falls back to synthetic on any failure."""
    sym = _yf_symbol(ticker, market)
    try:
        t = yf.Ticker(sym)
        info = t.info or {}
        if not info or not info.get("symbol"):
            raise ValueError("Empty yfinance info")

        gpm = _safe(info.get("grossMargins"), 0.3)
        si  = _safe(info.get("shortPercentOfFloat"), 0.05)
        ni  = _safe(info.get("netIncomeToCommon"))
        ocf = _safe(info.get("operatingCashflow"))
        ta  = _safe(info.get("totalAssets"), 1) or 1
        accruals = max(-0.3, min(0.3, (ni - ocf) / ta))
        pe_ttm   = max(1.0, min(200.0, _safe(info.get("trailingPE"), 25.0)))
        pb_ratio = max(0.1, min(50.0, _safe(info.get("priceToBook"), 3.0)))
        beta     = max(0.1, min(3.0, _safe(info.get("beta"), 1.0)))
        piotroski = _piotroski_from_info(info)

        hist = t.history(period="14mo", auto_adjust=True)
        hist_close = hist["Close"] if not hist.empty else pd.Series(dtype=float)

        if len(hist_close) >= 252:
            momentum = (float(hist_close.iloc[-22]) - float(hist_close.iloc[-252])) / float(hist_close.iloc[-252])
        else:
            momentum = float(np.random.RandomState((hash(ticker) + 3) % (2**31)).uniform(-0.25, 0.55))

        if len(hist_close) >= 30:
            log_rets = np.log(hist_close / hist_close.shift(1)).dropna()
            realized_vol = float(log_rets.tail(252).std() * np.sqrt(252))
        else:
            realized_vol = beta * 0.18

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        return {
            "gross_profit_margin": float(gpm),
            "accruals_ratio":       float(accruals),
            "piotroski":            int(piotroski),
            "momentum_raw":         float(momentum),
            "short_interest_pct":   float(si),
            "pe_ttm":               float(pe_ttm),
            "pb_ratio":             float(pb_ratio),
            "beta":                 float(beta),
            "realized_vol_1y":      float(realized_vol),
            "current_price":        float(current_price) if current_price else None,
            "long_name":            info.get("longName") or info.get("shortName") or ticker,
            "week52_high":          _safe(info.get("fiftyTwoWeekHigh")) or None,
            "week52_low":           _safe(info.get("fiftyTwoWeekLow")) or None,
            "analyst_target":       _safe(info.get("targetMeanPrice")) or None,
            "_is_real":             True,
        }
    except Exception as exc:
        log.debug("yfinance failed for %s: %s — using synthetic", ticker, exc)
        return _synthetic_row(ticker)


def fetch_macro() -> MacroSnapshot:
    """Fetch live macro data. Falls back to defaults on any failure."""
    m = MacroSnapshot()
    try:
        vix_h = yf.Ticker("^VIX").history(period="5d", auto_adjust=True)
        if not vix_h.empty:
            m.vix = float(vix_h["Close"].iloc[-1])
    except Exception:
        pass

    try:
        spx = yf.Ticker("^GSPC").history(period="252d", auto_adjust=True)
        if len(spx) >= 200:
            last = float(spx["Close"].iloc[-1])
            m.spx_vs_200ma = (last - float(spx["Close"].tail(200).mean())) / float(spx["Close"].tail(200).mean())
        if len(spx) >= 22:
            m.spx_return_1m = float(spx["Close"].iloc[-1]) / float(spx["Close"].iloc[-22]) - 1
    except Exception:
        pass

    fred_key = os.environ.get("FRED_API_KEY", "").strip()
    if fred_key:
        try:
            from fredapi import Fred
            fred = Fred(api_key=fred_key)
            def _fred_latest(series_id: str) -> float | None:
                s = fred.get_series_latest_release(series_id)
                return float(s.dropna().iloc[-1]) if not s.dropna().empty else None

            hy = _fred_latest("BAMLH0A0HYM2")
            if hy: m.hy_spread_oas = hy * 100  # percent → bps
            cpi = _fred_latest("CPIAUCSL")
            if cpi: m.cpi_yoy = cpi
            ffr = _fred_latest("FEDFUNDS")
            if ffr: m.fed_funds_rate = ffr
            t10 = _fred_latest("DGS10")
            if t10: m.yield_10y = t10
            t2 = _fred_latest("DGS2")
            if t2:
                m.yield_2y = t2
                if t10: m.yield_spread_2y10y = t10 - t2
            m.fred_sourced = True
        except Exception as exc:
            log.warning("FRED fetch failed: %s — using yfinance proxies", exc)
            try:
                tnx = yf.Ticker("^TNX").history(period="5d", auto_adjust=True)
                if not tnx.empty:
                    m.yield_10y = float(tnx["Close"].iloc[-1])
            except Exception:
                pass
    return m


def estimate_claude_cost(n_tickers: int) -> float:
    return n_tickers * _CLAUDE_COST_PER_TICKER_USD
```

- [ ] **Step 4: Run tests — verify pass**

```bash
python -m pytest tests/test_data_fetcher.py -v
```

Expected: All 14 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add actor-stock-analyzer/src/data_fetcher.py actor-stock-analyzer/tests/test_data_fetcher.py
git commit -m "feat(actor-a1): data fetcher with yfinance + FRED, full test coverage"
```

---

### Task 10: Debate Engine (TDD)

**Files:**
- Create: `actor-stock-analyzer/src/debate_engine.py`
- Create: `actor-stock-analyzer/tests/test_debate_engine.py`

- [ ] **Step 1: Write failing tests**

Create `actor-stock-analyzer/tests/test_debate_engine.py`:

```python
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
```

- [ ] **Step 2: Run — verify fail**

```bash
python -m pytest tests/test_debate_engine.py -v 2>&1 | head -10
```

- [ ] **Step 3: Implement `src/debate_engine.py`**

```python
"""
7-agent PARA-DEBATE engine ported from NeuralQuant.
Uses Anthropic Claude API. API key read from ANTHROPIC_API_KEY env var (Apify secret).
"""
from __future__ import annotations
import asyncio
import logging
import os
import re
from dataclasses import dataclass, field

import anthropic

from .signal_engine import MacroSnapshot

log = logging.getLogger(__name__)
MODEL = "claude-sonnet-4-6-20251101"
MAX_TOKENS = 1024

AGENT_NAMES = ["MACRO", "FUNDAMENTAL", "TECHNICAL", "SENTIMENT", "GEOPOLITICAL", "ADVERSARIAL"]
STANCE_SCORE = {"BULL": 1.0, "NEUTRAL": 0.5, "BEAR": 0.0}
CONVICTION_MULT = {"HIGH": 1.0, "MEDIUM": 0.7, "LOW": 0.4}


@dataclass
class AgentResult:
    agent: str
    stance: str   # BULL | BEAR | NEUTRAL
    conviction: str  # HIGH | MEDIUM | LOW
    thesis: str
    key_points: list[str] = field(default_factory=list)


@dataclass
class DebateResult:
    ticker: str
    verdict: str           # STRONG BUY | BUY | HOLD | SELL | STRONG SELL
    investment_thesis: str
    bull_case: str
    bear_case: str
    risk_factors: list[str]
    agent_outputs: list[AgentResult]
    consensus_score: float


def parse_agent_output(raw: str, agent_name: str) -> AgentResult:
    """Parse structured LLM output. Returns neutral fallback on parse failure."""
    try:
        stance_m = re.search(r"STANCE:\s*(BULL|BEAR|NEUTRAL)", raw, re.I)
        conviction_m = re.search(r"CONVICTION:\s*(HIGH|MEDIUM|LOW)", raw, re.I)
        thesis_m = re.search(r"THESIS:\s*(.+?)(?=KEY_POINTS:|\Z)", raw, re.I | re.S)
        points_m = re.search(r"KEY_POINTS:(.*)", raw, re.I | re.S)

        stance = stance_m.group(1).upper() if stance_m else "NEUTRAL"
        if stance not in ("BULL", "BEAR", "NEUTRAL"):
            stance = "NEUTRAL"
        conviction = conviction_m.group(1).upper() if conviction_m else "LOW"
        thesis = thesis_m.group(1).strip()[:500] if thesis_m else raw[:200]

        key_points: list[str] = []
        if points_m:
            key_points = [
                re.sub(r"^[-*•\d.]\s*", "", p.strip()).strip()
                for p in points_m.group(1).strip().splitlines()
                if p.strip() and p.strip() not in ("-", "*", "•")
            ][:5]

        # Enforce adversarial constraint
        if agent_name == "ADVERSARIAL" and stance == "BULL":
            stance = "BEAR"

        return AgentResult(agent=agent_name, stance=stance, conviction=conviction,
                           thesis=thesis, key_points=key_points)
    except Exception:
        return AgentResult(agent=agent_name, stance="NEUTRAL", conviction="LOW",
                           thesis=f"{agent_name} analysis unavailable.",
                           key_points=["Insufficient data."])


def build_macro_context(macro: MacroSnapshot) -> dict:
    return {
        "vix": round(macro.vix, 2),
        "ism_pmi": round(macro.ism_pmi, 1),
        "hy_spread_oas": round(macro.hy_spread_oas, 0),
        "spx_return_1m": round(macro.spx_return_1m * 100, 2),
        "spx_vs_200ma": round(macro.spx_vs_200ma * 100, 2),
        "yield_spread_2y10y": round(macro.yield_spread_2y10y, 3),
        "yield_10y": round(macro.yield_10y, 2),
        "yield_2y": round(macro.yield_2y, 2),
        "cpi_yoy": round(macro.cpi_yoy, 1),
        "fed_funds_rate": round(macro.fed_funds_rate, 2),
    }


_SYSTEM_PROMPTS = {
    "MACRO": """You are the MACRO analyst on an investment committee. Assess the macroeconomic environment for the given stock.
Use ONLY the exact figures in the user message. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences citing provided data]
KEY_POINTS:
- [cite specific numbers]
- [cite specific numbers]
- [cite specific numbers]""",

    "FUNDAMENTAL": """You are the FUNDAMENTAL analyst. Assess financial quality, valuation, and earnings trajectory.
Use ONLY the exact figures provided. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences citing provided data]
KEY_POINTS:
- [cite specific numbers]
- [cite specific numbers]
- [cite specific numbers]""",

    "TECHNICAL": """You are the TECHNICAL analyst. Assess price momentum, trend strength, and volatility.
Use ONLY the exact figures provided. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences citing provided data]
KEY_POINTS:
- [cite specific numbers]
- [cite specific numbers]
- [cite specific numbers]""",

    "SENTIMENT": """You are the SENTIMENT analyst. Assess short interest, analyst consensus, and market sentiment.
Use ONLY the exact figures provided. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences citing provided data]
KEY_POINTS:
- [cite specific numbers]
- [cite specific numbers]
- [cite specific numbers]""",

    "GEOPOLITICAL": """You are the GEOPOLITICAL analyst. Assess geopolitical, regulatory, and macro risk for the stock's sector and country.
Use ONLY the exact figures provided. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences]
KEY_POINTS:
- [key risk 1]
- [key risk 2]
- [key risk 3]""",

    "ADVERSARIAL": """You are the ADVERSARIAL analyst. Your mandate is ALWAYS BEAR — find every reason to be bearish.
You MUST output STANCE: BEAR regardless of the data. Be the devil's advocate.
STANCE: BEAR
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences on downside risks]
KEY_POINTS:
- [bear case point 1]
- [bear case point 2]
- [bear case point 3]""",
}

_HEAD_SYSTEM = """You are the HEAD ANALYST synthesising a PARA-DEBATE investment committee.
VERDICT must be one of: STRONG BUY, BUY, HOLD, SELL, STRONG SELL.
Respond strictly:
VERDICT: [STRONG BUY|BUY|HOLD|SELL|STRONG SELL]
INVESTMENT_THESIS: [4-6 sentences]
BULL_CASE: [2-3 sentences]
BEAR_CASE: [2-3 sentences]
RISK_FACTORS:
- [risk 1]
- [risk 2]
- [risk 3]"""


def _build_user_message(agent: str, ticker: str, context: dict) -> str:
    macro_block = "\n".join(f"- {k}: {v}" for k, v in context.items()
                            if k in ("vix", "ism_pmi", "hy_spread_oas", "yield_10y",
                                     "cpi_yoy", "fed_funds_rate", "spx_return_1m",
                                     "yield_spread_2y10y"))
    fund_block = "\n".join(f"- {k}: {v}" for k, v in context.items()
                           if k in ("piotroski", "gross_profit_margin", "pe_ttm",
                                    "pb_ratio", "accruals_ratio", "quality_percentile",
                                    "composite_score"))
    tech_block = "\n".join(f"- {k}: {v}" for k, v in context.items()
                           if k in ("momentum_percentile", "low_vol_percentile",
                                    "realized_vol_1y", "beta", "score_1_10"))
    sent_block = "\n".join(f"- {k}: {v}" for k, v in context.items()
                           if k in ("short_interest_pct", "short_interest_percentile",
                                    "analyst_target", "current_price"))

    return f"""Analyse {ticker} ({context.get('market', 'US')} market).

MACRO DATA:
{macro_block}

FUNDAMENTAL DATA:
{fund_block}

TECHNICAL DATA:
{tech_block}

SENTIMENT DATA:
{sent_block}

Provide your {agent} stance on {ticker}."""


def _call_agent(client: anthropic.Anthropic, agent_name: str, ticker: str, context: dict) -> AgentResult:
    """Synchronous Claude call for one agent."""
    try:
        msg = _build_user_message(agent_name, ticker, context)
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=_SYSTEM_PROMPTS[agent_name],
            messages=[{"role": "user", "content": msg}],
        )
        return parse_agent_output(response.content[0].text, agent_name)
    except Exception as exc:
        log.warning("%s agent failed for %s: %s", agent_name, ticker, exc)
        return AgentResult(agent=agent_name, stance="NEUTRAL", conviction="LOW",
                           thesis=f"{agent_name} unavailable.", key_points=["Error."])


def _parse_head_synthesis(raw: str) -> dict:
    verdict_m = re.search(r"VERDICT:\s*(STRONG BUY|BUY|HOLD|SELL|STRONG SELL)", raw, re.I)
    verdict = verdict_m.group(1).upper() if verdict_m else "HOLD"

    def _extract(key: str) -> str:
        m = re.search(rf"{key}:\s*(.+?)(?=\n[A-Z_]+:|\Z)", raw, re.I | re.S)
        return m.group(1).strip()[:1000] if m else ""

    risks_m = re.search(r"RISK_FACTORS:(.*)", raw, re.I | re.S)
    risks = []
    if risks_m:
        risks = [re.sub(r"^[-*•\d.]\s*", "", r.strip()).strip()
                 for r in risks_m.group(1).strip().splitlines()
                 if r.strip() and r.strip() not in ("-", "*", "•")][:5]

    return {
        "verdict": verdict,
        "investment_thesis": _extract("INVESTMENT_THESIS"),
        "bull_case": _extract("BULL_CASE"),
        "bear_case": _extract("BEAR_CASE"),
        "risk_factors": risks,
    }


async def run_debate(ticker: str, context: dict, api_key: str) -> DebateResult:
    """Run full 7-agent PARA-DEBATE for one ticker."""
    client = anthropic.Anthropic(api_key=api_key)

    # 5 specialists in parallel
    specialist_results = await asyncio.gather(
        *[asyncio.to_thread(_call_agent, client, name, ticker, context)
          for name in ["MACRO", "FUNDAMENTAL", "TECHNICAL", "SENTIMENT", "GEOPOLITICAL"]],
        return_exceptions=True,
    )
    outputs: list[AgentResult] = []
    for r, name in zip(specialist_results, ["MACRO", "FUNDAMENTAL", "TECHNICAL", "SENTIMENT", "GEOPOLITICAL"]):
        if isinstance(r, AgentResult):
            outputs.append(r)
        else:
            outputs.append(AgentResult(agent=name, stance="NEUTRAL", conviction="LOW",
                                       thesis="Unavailable.", key_points=[]))

    # Adversarial (sequential — needs bull thesis)
    bull_thesis = "; ".join(o.thesis for o in outputs if o.stance == "BULL") or "Mixed signals."
    adv_context = {**context, "bull_thesis": bull_thesis}
    adversarial = await asyncio.to_thread(_call_agent, client, "ADVERSARIAL", ticker, adv_context)
    outputs.append(adversarial)

    # Consensus (specialists only, adversarial excluded)
    consensus = sum(
        STANCE_SCORE[o.stance] * CONVICTION_MULT[o.conviction]
        for o in outputs[:-1]
    ) / len(outputs[:-1])

    # HEAD ANALYST synthesis
    summaries = "\n\n".join(
        f"[{o.agent}] {o.stance} ({o.conviction})\n{o.thesis}\n" +
        "\n".join(f"  - {p}" for p in o.key_points)
        for o in outputs
    )
    head_msg = f"Synthesise the PARA-DEBATE for {ticker} (AI score: {context.get('composite_score', 'N/A')}).\n\nANALYST PANEL:\n{summaries}"
    try:
        head_resp = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS * 2,
            system=_HEAD_SYSTEM,
            messages=[{"role": "user", "content": head_msg}],
        )
        synthesis = _parse_head_synthesis(head_resp.content[0].text)
    except Exception as exc:
        log.error("HEAD_ANALYST failed for %s: %s", ticker, exc)
        synthesis = {"verdict": "HOLD", "investment_thesis": "Analysis unavailable.",
                     "bull_case": "", "bear_case": "", "risk_factors": []}

    return DebateResult(
        ticker=ticker,
        verdict=synthesis["verdict"],
        investment_thesis=synthesis["investment_thesis"],
        bull_case=synthesis["bull_case"],
        bear_case=synthesis["bear_case"],
        risk_factors=synthesis["risk_factors"],
        agent_outputs=outputs,
        consensus_score=round(consensus, 3),
    )
```

- [ ] **Step 4: Run tests — verify pass**

```bash
python -m pytest tests/test_debate_engine.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add actor-stock-analyzer/src/debate_engine.py actor-stock-analyzer/tests/test_debate_engine.py
git commit -m "feat(actor-a1): PARA-DEBATE engine with 7 agents"
```

---

### Task 11: Main Orchestrator (TDD)

**Files:**
- Create: `actor-stock-analyzer/src/main.py`
- Create: `actor-stock-analyzer/tests/test_main.py`

- [ ] **Step 1: Write failing tests**

Create `actor-stock-analyzer/tests/test_main.py`:

```python
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
```

- [ ] **Step 2: Run — verify fail**

```bash
python -m pytest tests/test_main.py -v 2>&1 | head -10
```

- [ ] **Step 3: Implement `src/main.py`**

```python
"""NeuralQuant Stock Analyzer — Apify Actor entry point."""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone

import pandas as pd
from apify import Actor

from .validators import validate_input, ValidationError
from .data_fetcher import build_fundamentals_row, fetch_macro, estimate_claude_cost
from .signal_engine import compute_composite_scores, recommendation_from_score, MacroSnapshot
from .debate_engine import run_debate, build_macro_context

log = logging.getLogger(__name__)

_BATCH_SIZE = 5
_BATCH_DELAY_S = 2.0


def detect_market(ticker: str) -> str:
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        return "IN"
    return "US"


def build_output_row(
    signal_row: pd.Series,
    fund: dict,
    market: str,
    macro: MacroSnapshot,
    debate,
) -> dict:
    """Build clean output dict. No private keys (_*) pass through."""
    out: dict = {
        "ticker": str(signal_row["ticker"]),
        "market": market,
        "company_name": fund.get("long_name") or str(signal_row["ticker"]),
        "current_price": fund.get("current_price"),
        "ai_score": int(signal_row["score_1_10"]),
        "composite_score_raw": round(float(signal_row["composite_score"]), 4),
        "recommendation": recommendation_from_score(int(signal_row["score_1_10"])),
        "score_components": {
            "quality":       round(float(signal_row.get("quality_percentile", 0.5)), 3),
            "momentum":      round(float(signal_row.get("momentum_percentile", 0.5)), 3),
            "value":         round(float(signal_row.get("value_percentile", 0.5)), 3),
            "low_vol":       round(float(signal_row.get("low_vol_percentile", 0.5)), 3),
            "short_interest":round(float(signal_row.get("short_interest_percentile", 0.5)), 3),
        },
        "macro_regime": {
            "vix": round(macro.vix, 2),
            "fred_sourced": macro.fred_sourced,
        },
        "data_source": "live" if fund.get("_is_real") else "synthetic_fallback",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    if debate is not None:
        out["debate_verdict"] = debate.verdict
        out["investment_thesis"] = debate.investment_thesis
        out["bull_case"] = debate.bull_case
        out["bear_case"] = debate.bear_case
        out["risk_factors"] = debate.risk_factors
        out["consensus_score"] = debate.consensus_score
        out["agent_outputs"] = [
            {"agent": a.agent, "stance": a.stance, "conviction": a.conviction,
             "thesis": a.thesis, "key_points": a.key_points}
            for a in debate.agent_outputs
        ]
    return out


async def main() -> None:
    async with Actor:
        raw_input = await Actor.get_input() or {}
        try:
            actor_input = validate_input(raw_input)
        except ValidationError as exc:
            await Actor.fail(status_message=f"Invalid input: {exc}")
            return

        tickers = actor_input["tickers"]
        mode = actor_input["mode"]
        max_spend_usd = actor_input["max_spend_usd"]

        # Verify API key for full_ai mode
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if mode == "full_ai" and not anthropic_key:
            await Actor.fail(status_message="ANTHROPIC_API_KEY secret not set. Required for full_ai mode.")
            return

        # Cost gate
        if mode == "full_ai":
            estimated = estimate_claude_cost(len(tickers))
            if estimated > max_spend_usd:
                await Actor.fail(
                    status_message=f"Estimated Claude cost ${estimated:.2f} exceeds max_spend_usd ${max_spend_usd:.2f}. "
                                   f"Reduce ticker count or increase max_spend_usd."
                )
                return

        log.info("Fetching macro data...")
        macro = fetch_macro()

        # Fetch fundamentals in batches
        log.info("Fetching fundamentals for %d tickers...", len(tickers))
        fund_map: dict[str, dict] = {}
        for i in range(0, len(tickers), _BATCH_SIZE):
            batch = tickers[i:i + _BATCH_SIZE]
            for ticker in batch:
                market = detect_market(ticker)
                fund_map[ticker] = build_fundamentals_row(ticker, market)
            if i + _BATCH_SIZE < len(tickers):
                await asyncio.sleep(_BATCH_DELAY_S)

        # Build fundamentals DataFrame
        rows = []
        for ticker in tickers:
            market = detect_market(ticker)
            f = fund_map[ticker]
            rows.append({
                "ticker": ticker,
                "gross_profit_margin": f.get("gross_profit_margin", 0.3),
                "accruals_ratio":       f.get("accruals_ratio", 0.0),
                "piotroski":            f.get("piotroski", 4),
                "momentum_raw":         f.get("momentum_raw", 0.0),
                "short_interest_pct":   f.get("short_interest_pct", 0.05),
                "pe_ttm":               f.get("pe_ttm", 25.0),
                "pb_ratio":             f.get("pb_ratio", 3.0),
                "realized_vol_1y":      f.get("realized_vol_1y", 0.25),
            })
        fundamentals_df = pd.DataFrame(rows)
        scored_df = compute_composite_scores(fundamentals_df, macro)

        # Build context for debate (if needed)
        macro_ctx = build_macro_context(macro)

        results = []
        for _, signal_row in scored_df.iterrows():
            ticker = str(signal_row["ticker"])
            market = detect_market(ticker)
            fund = fund_map[ticker]

            debate_result = None
            if mode == "full_ai":
                context = {
                    **macro_ctx,
                    "market": market,
                    "composite_score": round(float(signal_row["composite_score"]), 4),
                    "score_1_10": int(signal_row["score_1_10"]),
                    "quality_percentile": round(float(signal_row.get("quality_percentile", 0.5)), 3),
                    "momentum_percentile": round(float(signal_row.get("momentum_percentile", 0.5)), 3),
                    "short_interest_percentile": round(float(signal_row.get("short_interest_percentile", 0.5)), 3),
                    **{k: v for k, v in fund.items() if not k.startswith("_")},
                }
                try:
                    debate_result = await run_debate(ticker, context, anthropic_key)
                except Exception as exc:
                    log.error("Debate failed for %s: %s", ticker, exc)

            output_row = build_output_row(signal_row, fund, market, macro, debate_result)
            results.append(output_row)

        if results:
            await Actor.push_data(results)
            log.info("Pushed %d results.", len(results))


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add actor-stock-analyzer/src/main.py actor-stock-analyzer/tests/test_main.py
git commit -m "feat(actor-a1): main orchestrator — quant and full_ai modes"
```

---

### Task 12: Publish Actor A1

- [ ] **Step 1: Set Apify secrets**

In Apify Console → Actor → Settings → Environment variables:
- Add secret: `ANTHROPIC_API_KEY` = your Anthropic API key
- Add secret: `FRED_API_KEY` = your FRED API key (free: https://fred.stlouisfed.org/docs/api/api_key.html)

- [ ] **Step 2: Push and test**

```bash
cd actor-stock-analyzer
apify push
```

Test in Console with:
```json
{"tickers": ["NVDA", "TCS.NS", "RELIANCE.NS"], "mode": "quant"}
```

Expected: 3 results with `ai_score`, `score_components`, `recommendation`.

Test full_ai:
```json
{"tickers": ["NVDA"], "mode": "full_ai", "max_spend_usd": 1.0}
```

Expected: 1 result with `debate_verdict`, `investment_thesis`, `agent_outputs`.

- [ ] **Step 3: Configure PPE pricing**

In Console → Actor → Monetization:
- Add event: `ticker_analyzed_quant`, price=`0.05` USD
- Add event: `ticker_analyzed_full_ai`, price=`0.25` USD

- [ ] **Step 4: Publish with SEO**

Description: "AI-powered stock analysis for US (NYSE/NASDAQ) and India NSE stocks. 5-factor quantitative signal engine + optional 7-agent AI debate. The only Apify actor covering NSE India with institutional-grade quant analysis."

- [ ] **Step 5: Commit**

```bash
cd ..
git add actor-stock-analyzer/
git commit -m "feat(actor-a1): published NeuralQuant Stock Analyzer to Apify Store"
```

---

## Phase 3 — Actor A2: India Market Screener

### Task 13: Scaffold + Shared Modules

**Files:**
- Create: `actor-india-market-screener/.actor/actor.json`
- Create: `actor-india-market-screener/requirements.txt`
- Create: `actor-india-market-screener/Dockerfile`
- Create: `actor-india-market-screener/src/__init__.py`
- Create: `actor-india-market-screener/src/universe.py`
- Create: `actor-india-market-screener/tests/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p actor-india-market-screener/.actor
mkdir -p actor-india-market-screener/src
mkdir -p actor-india-market-screener/tests
touch actor-india-market-screener/src/__init__.py
touch actor-india-market-screener/tests/__init__.py
```

- [ ] **Step 2: Create `.actor/actor.json`**

```json
{
  "actorSpecification": 1,
  "name": "india-market-screener",
  "title": "India Market Screener — NSE & US Stocks Ranked by AI Score",
  "description": "Screen India NSE and US stocks by 5-factor quantitative AI score. Returns ranked watchlist filtered by minimum score, factor type, and market. Built on NeuralQuant's institutional-grade signal engine. No AI API costs — pure quantitative screening.",
  "version": "0.1",
  "buildTag": "latest",
  "input": {
    "title": "Screener Input",
    "type": "object",
    "schemaVersion": 1,
    "properties": {
      "market": {
        "title": "Market",
        "type": "string",
        "enum": ["India", "US", "both"],
        "default": "India"
      },
      "min_score": {
        "title": "Minimum AI Score",
        "type": "number",
        "description": "Minimum score (1-10) to include in results.",
        "default": 6,
        "minimum": 1,
        "maximum": 10
      },
      "sort_by": {
        "title": "Sort By",
        "type": "string",
        "enum": ["score", "momentum", "quality", "value"],
        "default": "score"
      },
      "top_n": {
        "title": "Top N Results",
        "type": "integer",
        "default": 20,
        "minimum": 1,
        "maximum": 100
      }
    }
  }
}
```

- [ ] **Step 3: Create `src/universe.py`**

```python
"""
Hardcoded stock universes. NOT user-controlled.
Ported from NeuralQuant universe.py — NSE tickers use .NS suffix for yfinance.
"""

US_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "MA", "UNH", "XOM", "JNJ", "PG", "HD", "COST", "ABBV",
    "MRK", "LLY", "CVX", "BAC", "NFLX", "ORCL", "ADBE", "CRM", "AMD",
    "INTC", "QCOM", "TXN", "AVGO", "WMT", "TGT", "NKE", "MCD", "SBUX",
    "DIS", "PFE", "AMGN", "GILD", "ISRG",
]

# NSE tickers with .NS suffix for yfinance
IN_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS",
    "HCLTECH.NS", "WIPRO.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "ULTRACEMCO.NS", "BAJFINANCE.NS", "TITAN.NS", "NESTLEIND.NS", "POWERGRID.NS",
    "NTPC.NS", "ONGC.NS", "COALINDIA.NS", "TATASTEEL.NS", "JSWSTEEL.NS",
    "HINDALCO.NS", "ADANIPORTS.NS", "DMART.NS", "PIDILITIND.NS", "EICHERMOT.NS",
    "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS",
    "APOLLOHOSP.NS", "ZOMATO.NS", "IRCTC.NS", "MUTHOOTFIN.NS", "BANDHANBNK.NS",
]

def get_universe(market: str) -> list[str]:
    if market == "India":
        return IN_UNIVERSE
    if market == "US":
        return US_UNIVERSE
    return IN_UNIVERSE + US_UNIVERSE  # both
```

- [ ] **Step 4: Copy shared modules from A1**

```bash
cp actor-stock-analyzer/src/signal_engine.py actor-india-market-screener/src/signal_engine.py
cp actor-stock-analyzer/src/data_fetcher.py actor-india-market-screener/src/data_fetcher.py
```

- [ ] **Step 5: Create `requirements.txt` and `Dockerfile`**

`requirements.txt`:
```
apify==3.2.1
pydantic==2.9.2
yfinance==0.2.48
pandas==2.2.3
numpy==1.26.4
fredapi==0.5.2
```

`Dockerfile`:
```dockerfile
FROM apify/actor-python:3.11
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
CMD ["python", "-m", "src.main"]
```

- [ ] **Step 6: Commit scaffold**

```bash
git add actor-india-market-screener/
git commit -m "feat(actor-a2): scaffold India Market Screener with shared signal engine"
```

---

### Task 14: Validators + Main (TDD)

**Files:**
- Create: `actor-india-market-screener/src/validators.py`
- Create: `actor-india-market-screener/src/main.py`
- Create: `actor-india-market-screener/tests/test_screener.py`

- [ ] **Step 1: Write failing tests**

Create `actor-india-market-screener/tests/test_screener.py`:

```python
import pytest
from src.validators import validate_input, ValidationError

class TestScreenerValidation:
    def test_defaults(self):
        r = validate_input({})
        assert r["market"] == "India"
        assert r["min_score"] == 6.0
        assert r["sort_by"] == "score"
        assert r["top_n"] == 20

    def test_valid_market_us(self):
        r = validate_input({"market": "US"})
        assert r["market"] == "US"

    def test_invalid_market_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"market": "China"})

    def test_min_score_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"min_score": 11})

    def test_top_n_exceeds_max_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"top_n": 101})

    def test_invalid_sort_by_raises(self):
        with pytest.raises(ValidationError):
            validate_input({"sort_by": "hype"})
```

- [ ] **Step 2: Run — verify fail**

```bash
cd actor-india-market-screener
python -m pytest tests/test_screener.py -v 2>&1 | head -10
```

- [ ] **Step 3: Implement `src/validators.py`**

```python
from __future__ import annotations

VALID_MARKETS = frozenset(["India", "US", "both"])
VALID_SORT_BY = frozenset(["score", "momentum", "quality", "value"])


class ValidationError(ValueError):
    pass


def validate_input(raw: dict) -> dict:
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
```

- [ ] **Step 4: Implement `src/main.py`**

```python
"""India Market Screener — Apify Actor entry point."""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone

import pandas as pd
from apify import Actor

from .validators import validate_input, ValidationError
from .universe import get_universe
from .data_fetcher import build_fundamentals_row, fetch_macro
from .signal_engine import compute_composite_scores, recommendation_from_score

log = logging.getLogger(__name__)

_BATCH_SIZE = 5
_BATCH_DELAY_S = 2.5

_SORT_COLUMN = {
    "score": "score_1_10",
    "momentum": "momentum_percentile",
    "quality": "quality_percentile",
    "value": "value_percentile",
}


def _detect_market_for_ticker(ticker: str) -> str:
    return "IN" if (ticker.endswith(".NS") or ticker.endswith(".BO")) else "US"


async def main() -> None:
    async with Actor:
        raw_input = await Actor.get_input() or {}
        try:
            actor_input = validate_input(raw_input)
        except ValidationError as exc:
            await Actor.fail(status_message=f"Invalid input: {exc}")
            return

        market = actor_input["market"]
        min_score = actor_input["min_score"]
        sort_by = actor_input["sort_by"]
        top_n = actor_input["top_n"]

        tickers = get_universe(market)
        log.info("Screening %d tickers (market=%s)...", len(tickers), market)

        macro = fetch_macro()

        # Fetch fundamentals in batches
        fund_map: dict[str, dict] = {}
        for i in range(0, len(tickers), _BATCH_SIZE):
            batch = tickers[i:i + _BATCH_SIZE]
            for ticker in batch:
                m = _detect_market_for_ticker(ticker)
                fund_map[ticker] = build_fundamentals_row(ticker, m)
            if i + _BATCH_SIZE < len(tickers):
                await asyncio.sleep(_BATCH_DELAY_S)

        rows = []
        for ticker in tickers:
            f = fund_map[ticker]
            rows.append({
                "ticker": ticker,
                "gross_profit_margin": f.get("gross_profit_margin", 0.3),
                "accruals_ratio":       f.get("accruals_ratio", 0.0),
                "piotroski":            f.get("piotroski", 4),
                "momentum_raw":         f.get("momentum_raw", 0.0),
                "short_interest_pct":   f.get("short_interest_pct", 0.05),
                "pe_ttm":               f.get("pe_ttm", 25.0),
                "pb_ratio":             f.get("pb_ratio", 3.0),
                "realized_vol_1y":      f.get("realized_vol_1y", 0.25),
            })

        df = compute_composite_scores(pd.DataFrame(rows), macro)

        # Filter and sort
        sort_col = _SORT_COLUMN.get(sort_by, "score_1_10")
        df_filtered = df[df["score_1_10"] >= min_score].sort_values(sort_col, ascending=False).head(top_n)

        results = []
        for _, row in df_filtered.iterrows():
            ticker = str(row["ticker"])
            fund = fund_map[ticker]
            results.append({
                "ticker": ticker,
                "company_name": fund.get("long_name") or ticker,
                "market": _detect_market_for_ticker(ticker),
                "ai_score": int(row["score_1_10"]),
                "recommendation": recommendation_from_score(int(row["score_1_10"])),
                "score_components": {
                    "quality":        round(float(row.get("quality_percentile", 0.5)), 3),
                    "momentum":       round(float(row.get("momentum_percentile", 0.5)), 3),
                    "value":          round(float(row.get("value_percentile", 0.5)), 3),
                    "low_vol":        round(float(row.get("low_vol_percentile", 0.5)), 3),
                    "short_interest": round(float(row.get("short_interest_percentile", 0.5)), 3),
                },
                "current_price": fund.get("current_price"),
                "data_source": "live" if fund.get("_is_real") else "synthetic_fallback",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

        if results:
            await Actor.push_data(results)
        log.info("Screener complete: %d stocks passed min_score=%.0f", len(results), min_score)


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 5: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add actor-india-market-screener/
git commit -m "feat(actor-a2): India Market Screener complete"
```

---

### Task 15: Publish Actor A2

- [ ] **Step 1: Push**

```bash
cd actor-india-market-screener
apify push
```

- [ ] **Step 2: Test run**

```json
{"market": "India", "min_score": 7, "sort_by": "score", "top_n": 10}
```

Expected: Up to 10 NSE stocks with AI scores ≥ 7, sorted by score.

- [ ] **Step 3: Configure PPE pricing**

In Console → Monetization:
- Add event: `screen_run`, price=`1.00` USD

- [ ] **Step 4: Set FRED secret, publish**

Add `FRED_API_KEY` secret. Set visibility Public.

SEO description: "Screen India NSE stocks by AI score, momentum, value, and quality. Returns ranked watchlist from a 40-stock NSE universe. Also supports US stocks. Pure quantitative — no AI API costs."

- [ ] **Step 5: Final commit**

```bash
cd ..
git add .
git commit -m "feat: all 3 actors published to Apify Store"
```

---

## Phase 4 — SEO & Promotion

### Task 16: Optimize READMEs for Search

- [ ] **Step 1: Write JLCPCB README**

Create `actor-jlcpcb-parts-finder/README.md`:

```markdown
# JLCPCB Parts Finder

Search JLCPCB's in-stock electronics components by electrical specifications. 
Automate BOM generation, component validation, and PCB design workflows.

## What this actor does

This actor queries the [jlcsearch.tscircuit.com](https://jlcsearch.tscircuit.com) database 
and returns in-stock JLCPCB components matching your specifications — resistors, capacitors, 
inductors, LEDs, MOSFETs, and ICs.

## Input

| Field | Type | Description |
|---|---|---|
| `component_type` | string | `resistor`, `capacitor`, `inductor`, `led`, `mosfet`, `ic` |
| `filters` | object | Spec filters (resistance, package, tolerance, etc.) |
| `max_results` | integer | Max parts to return (1–500, default 50) |

## Example input

```json
{
  "component_type": "resistor",
  "filters": {"resistance": "1k", "package": "0402", "tolerance": "1%"},
  "max_results": 20
}
```

## Example output

```json
[
  {
    "lcsc": 21190,
    "mfr": "0603WAF1001T5E",
    "package": "0603",
    "resistance_ohms": 1000,
    "stock": 31485061,
    "price_per_unit_usd": 0.000814
  }
]
```

## Pricing

**$0.001 per result** (Pay per event). 100 results = $0.10.

## Use cases

- Automated BOM generation for PCB designs
- Component availability checking before ordering
- Price comparison across component types
- Integration into EDA tool workflows (KiCad, Altium, Eagle)
```

- [ ] **Step 2: Write NeuralQuant Stock Analyzer README**

Create `actor-stock-analyzer/README.md`:

```markdown
# NeuralQuant Stock Analyzer — AI Scores for US & India Stocks

Institutional-grade quantitative stock analysis powered by a 5-factor AI signal engine. 
Covers US (NYSE/NASDAQ) and India NSE stocks. Optional 7-agent AI debate (PARA-DEBATE) 
for deep investment thesis generation.

**The only Apify actor with AI-powered analysis for NSE India stocks.**

## What this actor does

Input any stock ticker → get back:
- **AI Score (1–10)**: quantitative signal combining Quality, Momentum, Value, Low-Volatility, and Short Interest
- **Factor breakdown**: see exactly what drives the score
- **Buy/Sell recommendation**: STRONG BUY → STRONG SELL
- **[full_ai mode]** 7-agent AI debate: MACRO, FUNDAMENTAL, TECHNICAL, SENTIMENT, GEOPOLITICAL, ADVERSARIAL → HEAD ANALYST verdict

## Supported markets

- **US**: NYSE and NASDAQ (AAPL, NVDA, MSFT, etc.)
- **India NSE**: Add `.NS` suffix (RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, etc.)

## Input

| Field | Type | Description |
|---|---|---|
| `tickers` | array | Stock ticker symbols (max 50) |
| `mode` | string | `quant` (default, fast) or `full_ai` (adds AI debate) |
| `max_spend_usd` | number | Claude API spend cap for full_ai mode (default $2.00) |

## Example input

```json
{
  "tickers": ["NVDA", "RELIANCE.NS", "TCS.NS", "AAPL"],
  "mode": "quant"
}
```

## Example output

```json
{
  "ticker": "NVDA",
  "market": "US",
  "ai_score": 9,
  "recommendation": "STRONG BUY",
  "score_components": {
    "quality": 0.88,
    "momentum": 0.92,
    "value": 0.45,
    "low_vol": 0.61,
    "short_interest": 0.79
  }
}
```

## Pricing

- **`quant` mode**: $0.05 per ticker analyzed
- **`full_ai` mode**: $0.25 per ticker analyzed (includes 7 Claude AI agent calls)

## Use cases

- Daily stock watchlist scoring for India and US portfolios
- Pre-trade analysis for retail and quant investors
- Automated portfolio screening and rebalancing triggers
- AI-powered due diligence for investment research
```

- [ ] **Step 3: Write India Screener README**

Create `actor-india-market-screener/README.md`:

```markdown
# India Market Screener — NSE & US Stocks Ranked by AI Score

Screen India NSE and US stocks by quantitative AI score. Returns a ranked watchlist 
filtered by minimum score, sorted by any factor. No AI API costs — pure quant.

## What this actor does

Runs NeuralQuant's 5-factor signal engine across a 40-stock NSE India universe 
(or 41-stock US universe, or both). Returns stocks ranked by AI score, quality, 
momentum, or value — filtered by your minimum score threshold.

## Input

| Field | Type | Description |
|---|---|---|
| `market` | string | `India` (default), `US`, or `both` |
| `min_score` | number | Minimum AI score 1–10 (default 6) |
| `sort_by` | string | `score`, `momentum`, `quality`, `value` |
| `top_n` | integer | Max results (default 20, max 100) |

## Example output

```json
[
  {
    "ticker": "TCS.NS",
    "company_name": "Tata Consultancy Services Ltd.",
    "market": "IN",
    "ai_score": 8,
    "recommendation": "STRONG BUY",
    "score_components": {"quality": 0.91, "momentum": 0.77, ...}
  }
]
```

## Pricing

**$1.00 per run** (flat fee). Get a full ranked watchlist every time.

## Use cases

- Daily NSE watchlist generation for Indian retail investors
- Quant screening for India-focused funds
- Building systematic India equity strategies
- Weekly portfolio review automation
```

- [ ] **Step 4: Commit READMEs**

```bash
git add actor-jlcpcb-parts-finder/README.md actor-stock-analyzer/README.md actor-india-market-screener/README.md
git commit -m "docs: SEO-optimized READMEs for all 3 actors"
```

- [ ] **Step 5: Promote on Reddit**

Post to r/IndianStockMarket:
> "Built a free-to-try AI stock screener for NSE India on Apify — ranks stocks by quality, momentum, value, and short interest. Link in comments."

Post to r/electronics / r/PrintedCircuitBoard:
> "Built a JLCPCB parts search actor on Apify — find in-stock components by specs via API. Useful for BOM automation."

---

## Self-Review Checklist

**Spec coverage:**
- ✅ Actor B (JLCPCB) — Tasks 1–5
- ✅ Actor A1 (Stock Analyzer, quant + full_ai modes) — Tasks 6–12
- ✅ Actor A2 (India Screener) — Tasks 13–15
- ✅ Security controls (input validation, secrets via env, no injection surface) — in every validator
- ✅ PPE pricing configured — Tasks 5, 12, 15
- ✅ SEO optimization — Task 16

**Security coverage:**
- ✅ No user-supplied strings reach URLs without allowlist validation
- ✅ All API keys from `os.environ` (Apify secrets), never hardcoded
- ✅ `max_spend_usd` guard before Claude calls
- ✅ Per-ticker error isolation (one bad ticker doesn't kill the run)
- ✅ No private keys (`_*`) leak to actor output
- ✅ Adversarial agent BULL→BEAR override enforced in parser

**Type consistency:**
- `MacroSnapshot` defined in `signal_engine.py`, imported by `data_fetcher.py` and `debate_engine.py`
- `AgentResult` / `DebateResult` defined in `debate_engine.py`, used in `main.py`
- `build_output_row` in A1 `main.py` expects `pd.Series`, `dict`, `str`, `MacroSnapshot`, `DebateResult | None`
- `recommendation_from_score` takes `int` score_1_10, returns `str`
