#!/usr/bin/env python3
"""Sequential runner for Honest Agent Protocol Step 3/10 sweeps.

Runs metered then e_bh with llama3:8b m=50 reps=5, using the .venv python
directly to avoid uv parent/child duplication. Prints progress per rep and
appends to a log file.
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
SCRIPT = ROOT / "scripts" / "llm_adaptive_experiment.py"
LOG = ROOT / "docs" / "paper" / "step3_metered_ebh.log"

ENV = os.environ.copy()
ENV["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:11434"


def run_defense(defense: str) -> None:
    cmd = [
        str(PYTHON), "-u", str(SCRIPT),
        "--defenses", defense,
        "--model", "llama3:8b",
        "--trials", "50",
        "--reps", "5",
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
    header = f"\n=== STEP 3/10 RESTART: {datetime.now()} ===\n"
    LOG.write_text(LOG.read_text() + header, encoding="utf-8")
    print(header, end="")
    run_defense("metered")
    run_defense("e_bh")
    end = f"\n=== STEP 3/10 DONE: {datetime.now()} ===\n"
    LOG.write_text(LOG.read_text() + end, encoding="utf-8")
    print(end)


if __name__ == "__main__":
    main()
