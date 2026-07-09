#!/usr/bin/env python3
"""Merge Kaggle-downloaded real-LLM result files into the local repo.

Usage:
    uv run python scripts/merge_kaggle_outputs.py /path/to/kaggle/downloads

Copies *_llm_attack_results.{json,md} files into docs/paper/, then runs
aggregate_llm_results.py to rebuild the combined table and figure.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "paper"
AGGREGATE = ROOT / "scripts" / "aggregate_llm_results.py"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: uv run python scripts/merge_kaggle_outputs.py /path/to/kaggle/downloads")

    src = Path(sys.argv[1]).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"Source directory does not exist: {src}")

    files = list(src.glob("*_llm_attack_results.*"))
    if not files:
        raise SystemExit(f"No *_llm_attack_results.* files found in {src}")

    copied = 0
    for f in files:
        dst = DOCS / f.name
        shutil.copy2(f, dst)
        copied += 1
        print(f"copied {f.name}")

    print(f"\nMerged {copied} files into {DOCS}")

    # Rebuild aggregate.
    import subprocess
    print("\nRebuilding aggregate...")
    res = subprocess.run(
        ["uv", "run", "python", str(AGGREGATE)],
        cwd=ROOT,
        check=False,
    )
    if res.returncode != 0:
        raise SystemExit("aggregate_llm_results.py failed")

    # Print current table preview.
    agg = json.loads((DOCS / "llm_attack_results.json").read_text(encoding="utf-8"))
    print("\nCurrent combined table:")
    print(f"{'Defense':20s} {'Model':15s} {'Trials':7s} {'Reps':5s} {'Mean':>6s} {'Any%':>6s}")
    for r in agg["records"]:
        s = r["result"]
        print(
            f"{s['defense']:20s} {s['model']:15s} {s['trials']!s:>7s} {s['reps']!s:>5s} "
            f"{s['mean_false_certs']:>6.2f} {s['any_false_cert_rate']:>6.0%}"
        )


if __name__ == "__main__":
    main()
