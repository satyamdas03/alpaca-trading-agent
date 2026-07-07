#!/usr/bin/env python3
"""Sequential runner for Honest Agent Protocol Step 5/10: mistral cross-model.

Runs all five llama3-tested defenses (naive, protocol, metered, e_bh,
sparse_metered) with mistral m=30 reps=3, 4 concurrent LLM workers, using the
.venv python directly. Prints progress per defense and appends to a log.
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
SCRIPT = ROOT / "scripts" / "llm_adaptive_experiment.py"
LOG = ROOT / "docs" / "paper" / "step5_mistral.log"

ENV = os.environ.copy()
ENV["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:11434"

DEFENSES = ["naive", "protocol", "metered", "e_bh", "sparse_metered"]


def run_defense(defense: str) -> None:
    cmd = [
        str(PYTHON), "-u", str(SCRIPT),
        "--defenses", defense,
        "--model", "mistral",
        "--trials", "30",
        "--reps", "3",
        "--workers", "4",
    ]
    line = f"\n=== {datetime.now()}: running {defense} ===\n"
    print(line, end="")
    LOG.write_text(LOG.read_text() + line, encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, cwd=ROOT, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            fh.write(line)
            fh.flush()
            print(line, end="", flush=True)
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"{defense} failed with exit code {proc.returncode}")


def main() -> None:
    LOG.write_text(f"=== STEP 5/10 START: {datetime.now()} ===\n", encoding="utf-8")
    for defense in DEFENSES:
        run_defense(defense)
    end = f"\n=== STEP 5/10 DONE: {datetime.now()} ===\n"
    LOG.write_text(LOG.read_text() + end, encoding="utf-8")
    print(end)


if __name__ == "__main__":
    main()
