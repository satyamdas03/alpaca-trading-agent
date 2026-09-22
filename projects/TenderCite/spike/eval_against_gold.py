"""Compare extracted candidates against the gold set and print counts only."""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


def _normalize(text: str) -> set[str]:
    """Lowercase, drop punctuation/symbols, collapse whitespace, return word token set."""
    text = re.sub(r"\s+", " ", text.lower().strip())
    text = re.sub(r"[^\w\s]", " ", text)
    return set(text.split())


def _token_jaccard(a: str, b: str) -> float:
    ta = _normalize(a)
    tb = _normalize(b)
    if not ta and not tb:
        return 1.0
    inter = ta & tb
    union = ta | tb
    if not union:
        return 0.0
    return len(inter) / len(union)


def load_candidates(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_gold(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def evaluate(candidates: list[dict], gold_rows: list[dict], threshold: float = 0.55) -> dict:
    """Return hit / miss / false-mandatory counts."""
    mandatory_gold = [
        row for row in gold_rows
        if row.get("expected_status", "").strip().lower() == "mandatory"
    ]

    matched_gold_idx: set[int] = set()
    matched_candidate_idx: set[int] = set()

    for c_idx, cand in enumerate(candidates):
        cand_text = cand.get("requirement_text", "").strip()
        if not cand_text:
            continue

        best_sim = 0.0
        best_g_idx = -1
        for g_idx, gold in enumerate(mandatory_gold):
            gold_text = gold.get("mandatory_requirement", "").strip()
            if not gold_text:
                continue
            sim = _token_jaccard(cand_text, gold_text)
            if sim > best_sim:
                best_sim = sim
                best_g_idx = g_idx

        if best_sim >= threshold:
            matched_candidate_idx.add(c_idx)
            matched_gold_idx.add(best_g_idx)

    hits = len(matched_gold_idx)
    misses = len(mandatory_gold) - hits
    false_mandatory = len(candidates) - len(matched_candidate_idx)

    return {
        "hits": hits,
        "misses": misses,
        "false_mandatory": false_mandatory,
        "threshold": threshold,
        "total_candidates": len(candidates),
        "total_mandatory_gold": len(mandatory_gold),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate candidates against the gold set"
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=Path("spike/candidates.csv"),
        help="Candidate requirements CSV",
    )
    parser.add_argument(
        "--gold",
        type=Path,
        default=Path("packs/nsw-asc-002-rfq-001/gold-rows.csv"),
        help="Gold rows CSV",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.55,
        help="Token-Jaccard similarity threshold for a match",
    )
    args = parser.parse_args(argv)

    if not args.candidates.exists():
        print(f"EVAL_FAIL: candidates file not found: {args.candidates}", file=sys.stderr)
        return 1
    if not args.gold.exists():
        print(f"EVAL_FAIL: gold file not found: {args.gold}", file=sys.stderr)
        return 1

    candidates = load_candidates(args.candidates)
    gold_rows = load_gold(args.gold)
    result = evaluate(candidates, gold_rows, threshold=args.threshold)

    print(f"threshold: {result['threshold']}")
    print(f"total_candidates: {result['total_candidates']}")
    print(f"total_mandatory_gold: {result['total_mandatory_gold']}")
    print(f"hits: {result['hits']}")
    print(f"misses: {result['misses']}")
    print(f"false_mandatory: {result['false_mandatory']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
