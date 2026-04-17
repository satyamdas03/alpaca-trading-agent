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
    client = httpx.AsyncClient(timeout=_TIMEOUT)
    try:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = await client.get(url, headers={"Accept": "application/json"})
                resp.raise_for_status()
                try:
                    data = resp.json()
                except ValueError as exc:
                    raise RuntimeError(f"Invalid JSON response from jlcsearch: {exc}") from exc
                return parse_response(data, component_type, max_results)
            except httpx.HTTPError as exc:
                last_exc = exc
                log.warning("Attempt %d/%d failed: %s", attempt, _MAX_RETRIES, exc)
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(2 ** attempt)
    finally:
        await client.aclose()
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
            # Zero results is a valid outcome (e.g. no parts match the filters).
            # We succeed with an empty dataset rather than failing the run.
            log.info("No matching parts found for component_type=%s filters=%s.", component_type, filters)
        else:
            await Actor.push_data(parts)
            # PPE billing: charge per result returned
            await Actor.charge(event_name="result_returned", count=len(parts))
            log.info("Pushed %d parts to dataset.", len(parts))


if __name__ == "__main__":
    asyncio.run(main())
