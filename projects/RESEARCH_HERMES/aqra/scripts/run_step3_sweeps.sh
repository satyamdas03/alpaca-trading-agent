#!/bin/bash
# Run Step 3/10 sweeps sequentially: metered, then e_bh
# Uses .venv python directly to avoid uv run parent/child duplication
set -euo pipefail

cd /c/Users/point/projects/RESEARCH_HERMES/aqra
export ANTHROPIC_BASE_URL=http://127.0.0.1:11434

LOG=docs/paper/step3_metered_ebh.log
> "$LOG"

echo "=== STEP 3/10 START: $(date) ===" | tee -a "$LOG"

echo "--- Running metered llama3:8b m=50 reps=5 ---" | tee -a "$LOG"
.venv/Scripts/python.exe -u scripts/llm_adaptive_experiment.py \
  --defenses metered --model llama3:8b --trials 50 --reps 5 2>&1 | tee -a "$LOG"

echo "--- Running e_bh llama3:8b m=50 reps=5 ---" | tee -a "$LOG"
.venv/Scripts/python.exe -u scripts/llm_adaptive_experiment.py \
  --defenses e_bh --model llama3:8b --trials 50 --reps 5 2>&1 | tee -a "$LOG"

echo "=== STEP 3/10 DONE: $(date) ===" | tee -a "$LOG"
