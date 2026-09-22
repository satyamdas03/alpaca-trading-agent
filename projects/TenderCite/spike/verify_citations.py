"""Spot-check that cited pages contain the candidate requirement text."""
from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from pathlib import Path

from pypdf import PdfReader


def _normalize(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.lower().strip())
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if t]


def _coverage(cand_tokens: list[str], page_tokens: list[str]) -> float:
    if not cand_tokens:
        return 0.0
    page_set = set(page_tokens)
    found = sum(1 for t in cand_tokens if t in page_set)
    return found / len(cand_tokens)


def verify_candidates(
    candidates: list[dict],
    pdf_path: Path,
    n: int = 5,
    seed: int = 42,
    min_coverage: float = 0.6,
) -> list[dict]:
    """Verify n candidates have page citations that contain the requirement text."""
    reader = PdfReader(str(pdf_path))

    rng = random.Random(seed)
    sample = rng.sample(candidates, min(n, len(candidates))) if len(candidates) > n else candidates

    results = []
    for cand in sample:
        page_num = int(cand.get("page", 0))
        cand_text = cand.get("requirement_text", "")
        cand_tokens = _normalize(cand_text)

        if page_num < 1 or page_num > len(reader.pages):
            results.append({
                "requirement_text": cand_text,
                "page": page_num,
                "ok": False,
                "coverage": 0.0,
                "note": "page out of range",
            })
            continue

        page_text = reader.pages[page_num - 1].extract_text() or ""
        page_tokens = _normalize(page_text)
        coverage = _coverage(cand_tokens, page_tokens)

        results.append({
            "requirement_text": cand_text,
            "page": page_num,
            "ok": coverage >= min_coverage,
            "coverage": coverage,
            "note": f"token coverage {coverage:.2%}",
        })

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Spot-check candidate page citations")
    parser.add_argument(
        "--candidates",
        type=Path,
        default=Path("spike/candidates.csv"),
        help="Candidate requirements CSV",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=Path("packs/nsw-asc-002-rfq-001/sources/rft.pdf"),
        help="Source PDF path",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=5,
        help="Number of candidates to verify",
    )
    args = parser.parse_args(argv)

    if not args.candidates.exists():
        print(f"VERIFY_FAIL: candidates file not found: {args.candidates}", file=sys.stderr)
        return 1

    with args.candidates.open(encoding="utf-8", newline="") as fh:
        candidates = list(csv.DictReader(fh))

    results = verify_candidates(candidates, args.pdf, n=args.n)

    all_ok = True
    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        if not r["ok"]:
            all_ok = False
        print(f"[{status}] page {r['page']} coverage={r['coverage']:.2%} | {r['requirement_text'][:100]}")
        print(f"       note: {r['note']}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
