# Honest Agent Protocol — Kaggle GPU Scaling

## Goal
Use Kaggle's free T4 GPU (30 hours/week) to run the Honest Agent Protocol real-LLM adaptive experiment at scale without heating your laptop.

## Files
- `kaggle_honest_agent_scaling.ipynb` — the notebook. Upload this to Kaggle.
- This README — quick instructions.

## One-session plan (repeat for each model family)

1. Open [kaggle.com](https://kaggle.com) → **Notebooks** → **New Notebook**.
2. In the notebook editor, click **File → Upload Notebook** and select `kaggle_honest_agent_scaling.ipynb`.
3. In the first code cell, set `MODEL` to the family for this session:
   - `"mistral"` — finish the cell that died locally
   - `"gemma2:9b"` — Google family
   - `"qwen2.5:7b"` — Alibaba family
   - `"llama3.1:8b"` — Meta family
4. Turn on the GPU: **Settings → Accelerator → GPU T4**.
5. Click **Save Version** and choose **Save & Run All (Commit)**. This runs in the background for up to 12 hours.
6. Come back later, open the **Output** tab, and download all files matching `*_llm_attack_results.{json,md}` plus `llm_attack_results.json`.
7. Copy the downloaded files into `aqra/docs/paper/` on your local machine.
8. Run the local aggregate script:
   ```bash
   cd aqra
   uv run python scripts/aggregate_llm_results.py
   ```
9. Update `aqra/docs/paper/honest_agent_protocol.md` Section 4.3 with the new numbers.

## Expected wall-clock time per model family
On T4 GPU with `WORKERS = 4`:
- 3 defenses × 200 trials × 10 reps ≈ 6,000 LLM calls.
- Estimated 2–4 hours per model family.
- Four families ≈ 12–16 hours of GPU time total, well inside the 30 hours/week free quota.

## Tip: parallelize across accounts
If you have access to multiple Kaggle accounts, run a different model family on each account simultaneously. The output files are named per model, so they will not collide when merged locally.

## Outputs to expect per session
For each model you will get:
- `naive_{model}_llm_attack_results.{json,md}`
- `protocol_{model}_llm_attack_results.{json,md}`
- `maxleak_metered_{model}_llm_attack_results.{json,md}`
- `llm_attack_results.json` (aggregate of the three defenses)

## Known Kaggle quirks
- **12-hour session limit:** one model family per session is safest.
- **30 hours/week GPU quota:** you may need to wait for the weekly reset if you run many sessions.
- **Ollama model cache:** the notebook stores models in `/kaggle/working/ollama_models`. If Kaggle resets the working directory between sessions, models re-download.
- **Timeouts:** Kaggle sometimes kills idle browser tabs but keeps background execution running. Use **Save & Run All (Commit)** for unattended runs.
