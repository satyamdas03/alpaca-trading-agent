#!/usr/bin/env python3
"""Phase 1 scaled real-LLM experiments.

Runs llama3:8b and mistral, each on naive/protocol/maxleak_metered,
with m=200 trials and reps=10, using 4 concurrent LLM workers.
Each defense/model cell runs sequentially to avoid file races; each
individual cell is resumable from its per-defense output file.

Output files:
  docs/paper/{defense}_{model_slug}_llm_attack_results.{json,md}
  docs/paper/phase1_scaled_llm.log

Usage:
  uv run python scripts/run_phase1_scaled_llm.py
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
LOG = ROOT / "docs" / "paper" / "phase1_scaled_llm.log"

ENV = os.environ.copy()
ENV["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:11434"

MODELS = ["llama3:8b", "mistral"]
DEFENSES = ["naive", "protocol", "maxleak_metered"]
TRIALS = 200
REPS = 10
WORKERS = 4


def _now() -> str:
    return datetime.now().isoformat()


def _slug(model: str) -> str:
    return model.replace(":", "_")


def _append(line: str) -> None:
    print(line, end="")
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()


def run_cell(defense: str, model: str) -> None:
    slug = _slug(model)
    per_file = ROOT / "docs" / "paper" / f"{defense}_{slug}_llm_attack_results.json"
    if per_file.exists():
        try:
            data = json.loads(per_file.read_text(encoding="utf-8"))
            r = data.get("result", {})
            if r.get("trials") == TRIALS and r.get("reps") == REPS:
                _append(f"\n=== {_now()}: skipping {defense} {model} (already complete) ===\n")
                return
        except Exception:
            pass

    line = f"\n=== {_now()}: running {defense} {model} (m={TRIALS}, r={REPS}) ===\n"
    _append(line)

    cmd = [
        str(PYTHON), "-u", str(SCRIPT),
        "--defenses", defense,
        "--model", model,
        "--trials", str(TRIALS),
        "--reps", str(REPS),
        "--workers", str(WORKERS),
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
        raise RuntimeError(f"{defense} {model} failed with exit code {proc.returncode}")

    end = f"=== {_now()}: completed {defense} {model} ===\n"
    _append(end)


def main() -> None:
    LOG.write_text(f"=== PHASE 1 SCALED LLM START: {_now()} ===\n", encoding="utf-8")
    total = len(MODELS) * len(DEFENSES)
    done = 0
    for model in MODELS:
        for defense in DEFENSES:
            done += 1
            _append(f"\n[{done}/{total}] Next cell: {defense} {model}\n")
            run_cell(defense, model)
    _append(f"\n=== PHASE 1 SCALED LLM DONE: {_now()} ===\n")


if __name__ == "__main__":
    main()
