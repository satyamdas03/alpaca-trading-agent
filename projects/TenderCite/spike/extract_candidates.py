"""Slice B: extract candidate mandatory requirements with page citations via Ollama."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import threading
from pathlib import Path
from typing import Any

import requests
from pypdf import PdfReader

from text_gate import gate_pack

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:latest")

# Candidate text must contain at least one of these obligation cues (case-insensitive).
_OBLIGATION_CUES = (
    "must", "shall", "required", "mandatory", "will only be accepted",
    "may be excluded", "agrees to indemnify", "agrees to", "is required",
    "are required", "will not be accepted", "must not", "shall not",
)


def _cache_key(page_text: str, model: str) -> str:
    return hashlib.sha256(f"{model}:{page_text}".encode("utf-8")).hexdigest()


def _cache_dir() -> Path:
    return Path(__file__).with_name(".cache")


def _load_cache(key: str) -> list[dict] | None:
    cache_path = _cache_dir() / f"{key}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _save_cache(key: str, data: list[dict]) -> None:
    cd = _cache_dir()
    cd.mkdir(parents=True, exist_ok=True)
    cache_path = cd / f"{key}.json"
    cache_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _extract_json(text: str) -> list[dict]:
    """Best-effort extraction of a JSON array from model output."""
    text = text.strip()
    if not text:
        return []

    # Pull JSON out of a markdown fence if present.
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    # Try the whole thing as JSON first.
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    # Look for the first JSON array in the text.
    array_match = re.search(r"\[[\s\S]*\]", text)
    if array_match:
        try:
            parsed = json.loads(array_match.group(0))
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

    return []


def _has_obligation_cue(text: str) -> bool:
    lowered = text.lower()
    return any(cue in lowered for cue in _OBLIGATION_CUES)


def _rule_fallback_candidates(page_text: str, page_num: int) -> list[dict]:
    """If Ollama returns nothing, use sentence/fragment-level regex on obligation cues."""
    # Normalize bullets and line breaks so each bullet/line becomes its own fragment.
    normalized = page_text.replace("\n", " ").replace("•", ". ").replace("◦", ". ")
    # Split on sentence terminators and bullet-like "o " markers.
    fragments = re.split(r"(?<=[.!?])\s+|\s+o\s+|\s+\-\s+", normalized)
    results: list[dict] = []
    for frag in fragments:
        frag = frag.strip()
        if len(frag) < 20 or len(frag) > 600:
            continue
        if not _has_obligation_cue(frag):
            continue
        # Skip obvious headings/TOC lines.
        if re.match(r"^[0-9.]+\s+[A-Z]", frag):
            continue
        # Skip fragments that are mostly URLs/email addresses.
        if frag.count("@") > 2 and " " not in frag:
            continue
        results.append({
            "requirement_text": frag,
            "reason": "rule-based fallback (Ollama returned empty)",
            "confidence": 0.5,
            "page": page_num,
        })
    return results



def _ollama_extract_page(page_text: str, model: str) -> list[dict]:
    """Call local Ollama for one page and return parsed candidates (may be empty)."""
    prompt = (
        "Extract candidate mandatory requirements from this RFx document page. "
        "Return a JSON array of objects with keys: requirement_text, reason, confidence (0-1). "
        "If none, return []."
    )

    ollama_result: list[dict] | None = None
    ollama_exc: Exception | None = None

    def _call() -> None:
        nonlocal ollama_result, ollama_exc
        try:
            resp = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": f"{prompt}\n\nPAGE TEXT:\n{page_text}",
                    "stream": False,
                    "options": {"temperature": 0.0},
                },
                timeout=(10, 600),
            )
            resp.raise_for_status()
            data = resp.json()
            raw = data.get("response", "")
            parsed = _extract_json(raw)
            parsed = [it for it in parsed if _has_obligation_cue(it.get("requirement_text", ""))]
            ollama_result = parsed
        except Exception as exc:
            ollama_exc = exc

    # Cap wall-clock wait at 90s; the daemon thread may continue in the background.
    t = threading.Thread(target=_call, daemon=True)
    t.start()
    t.join(timeout=90)

    if ollama_result is not None:
        return ollama_result
    if ollama_exc is not None and isinstance(ollama_exc, requests.exceptions.ConnectionError):
        raise RuntimeError(
            f"Cannot connect to Ollama at {OLLAMA_HOST}. Is Ollama running?"
        ) from ollama_exc
    return []


def extract_page_requirements(page_text: str, page_num: int, model: str = MODEL, use_ollama: bool = False) -> list[dict]:
    """Extract candidate mandatory requirements for one page.

    By default uses fast deterministic rules. Pass use_ollama=True to attempt
    local inference; if it hangs or returns empty, rules are used as fallback.
    """
    key = _cache_key(page_text, model)
    cached = _load_cache(key)
    if cached is not None:
        return cached

    # Fast path: a page with no obligation cue cannot contain a mandatory requirement.
    if not _has_obligation_cue(page_text):
        _save_cache(key, [])
        return []

    items: list[dict] = []
    if use_ollama:
        items = _ollama_extract_page(page_text, model)
        if not items:
            items = _rule_fallback_candidates(page_text, page_num)
    else:
        items = _rule_fallback_candidates(page_text, page_num)

    # Tag each item with the page number.
    for it in items:
        it["page"] = page_num

    _save_cache(key, items)
    return items


def extract_pack(pack_dir: Path, model: str = MODEL, use_ollama: bool = False) -> list[dict]:
    """Run text gate then extract candidate requirements from every page."""
    gate = gate_pack(pack_dir)
    if not gate["ok"]:
        raise RuntimeError("Text gate failed; refusing extraction.")

    reader = PdfReader(str(gate["pdf_path"]))
    candidates: list[dict] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        page_items = extract_page_requirements(text, i, model=model, use_ollama=use_ollama)
        candidates.extend(page_items)

    return candidates


def write_candidates_csv(candidates: list[dict], out_path: Path, source_file: str) -> None:
    fieldnames = ["requirement_text", "source_file", "page", "status"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for it in candidates:
            writer.writerow({
                "requirement_text": it.get("requirement_text", "").strip(),
                "source_file": source_file,
                "page": it.get("page", ""),
                "status": "pending",
            })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract candidate mandatory requirements")
    parser.add_argument(
        "--pack",
        type=Path,
        default=Path("packs/nsw-asc-002-rfq-001"),
        help="Path to pack directory containing sources/*.pdf and gold-rows.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("spike/candidates.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--model",
        default=MODEL,
        help="Ollama model tag to use",
    )
    parser.add_argument(
        "--use-ollama",
        action="store_true",
        help="Attempt local Ollama inference (slower; falls back to rules on timeout)",
    )
    args = parser.parse_args(argv)

    if args.use_ollama:
        print(f"Using Ollama model: {args.model}")
        print("This may take a few minutes (per-page local inference).")
    else:
        print("Using deterministic rule-based extraction (default for this spike).")
        print("Pass --use-ollama to attempt local inference (qwen3.5:latest).")

    try:
        gate = gate_pack(args.pack)
        candidates = extract_pack(args.pack, model=args.model, use_ollama=args.use_ollama)
    except Exception as exc:
        print(f"EXTRACT_FAIL: {exc}", file=sys.stderr)
        return 1

    write_candidates_csv(candidates, args.out, gate["source_file"])
    print(f"Extracted {len(candidates)} candidates to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
