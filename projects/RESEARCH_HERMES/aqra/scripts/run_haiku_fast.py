#!/usr/bin/env python3
"""Fast, credit-efficient Haiku-only real-LLM sweep.

Runs the three key arms (naive, protocol, maxleak_metered) against
claude-haiku-4-5-20251001 with m=200 trials x 10 reps and 8 workers.
Uses Anthropic API directly (credits now available). Each cell is
resumable from its per-defense output file.

Output:
  docs/paper/{defense}_claude-haiku-4-5-20251001_llm_attack_results.{json,md}
  docs/paper/haiku_fast.log
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
SCRIPT = ROOT / "scripts" / "llm_adaptive_experiment.py"
LOG = ROOT / "docs" / "paper" / "haiku_fast.log"

ENV = os.environ.copy()
# Prefer Anthropic API; do not set Ollama base URL.
ENV.pop("ANTHROPIC_BASE_URL", None)

MODEL = "claude-haiku-4-5-20251001"
DEFENSES = ["naive", "protocol", "maxleak_metered"]
TRIALS = 200
REPS = 10
WORKERS = 3
BATCH_DELAY = 0.5


def _now() -> str:
    return datetime.now().isoformat()


def _append(line: str) -> None:
    print(line, end="")
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()


def run_cell(defense: str) -> None:
    slug = MODEL.replace(":", "_")
    per_file = ROOT / "docs" / "paper" / f"{defense}_{slug}_llm_attack_results.json"
    if per_file.exists():
        try:
            data = json.loads(per_file.read_text(encoding="utf-8"))
            r = data.get("result", {})
            if r.get("trials") == TRIALS and r.get("reps") == REPS:
                _append(f"\n=== {_now()}: skipping {defense} {MODEL} (already complete) ===\n")
                return
        except Exception:
            pass

    line = f"\n=== {_now()}: running {defense} {MODEL} (m={TRIALS}, r={REPS}) ===\n"
    _append(line)

    cmd = [
        str(PYTHON), "-u", str(SCRIPT),
        "--defenses", defense,
        "--model", MODEL,
        "--trials", str(TRIALS),
        "--reps", str(REPS),
        "--workers", str(WORKERS),
        "--batch-delay", str(BATCH_DELAY),
    ]
    with LOG.open("a", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, cwd=ROOT, env=ENV, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
        for out_line in proc.stdout:
            fh.write(out_line)
            fh.flush()
            print(out_line, end="", flush=True)
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"{defense} {MODEL} failed with exit code {proc.returncode}")

    end = f"=== {_now()}: completed {defense} {MODEL} ===\n"
    _append(end)


def main() -> None:
    LOG.write_text(f"=== HAIKU FAST SWEEP START: {_now()} ===\n", encoding="utf-8")
    for defense in DEFENSES:
        run_cell(defense)
    _append(f"\n=== HAIKU FAST SWEEP DONE: {_now()} ===\n")


if __name__ == "__main__":
    main()
