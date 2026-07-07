#!/usr/bin/env python3
"""Sequential runner for Honest Agent Protocol Step 4/10: sparse_metered.

Runs sparse_metered with llama3:8b m=50 reps=5, 4 concurrent LLM workers,
using the .venv python directly. Prints progress per rep and appends to a log.
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
SCRIPT = ROOT / "scripts" / "llm_adaptive_experiment.py"
LOG = ROOT / "docs" / "paper" / "step4_sparse_metered.log"

ENV = os.environ.copy()
ENV["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:11434"


def main() -> None:
    header = f"=== STEP 4/10 START: {datetime.now()} ===\n"
    LOG.write_text(header, encoding="utf-8")
    print(header, end="")

    cmd = [
        str(PYTHON), "-u", str(SCRIPT),
        "--defenses", "sparse_metered",
        "--model", "llama3:8b",
        "--trials", "50",
        "--reps", "5",
        "--workers", "4",
    ]
    with LOG.open("a", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, cwd=ROOT, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            fh.write(line)
            fh.flush()
            print(line, end="", flush=True)
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"sparse_metered failed with exit code {proc.returncode}")

    end = f"\n=== STEP 4/10 DONE: {datetime.now()} ===\n"
    LOG.write_text(LOG.read_text() + end, encoding="utf-8")
    print(end)


if __name__ == "__main__":
    main()
