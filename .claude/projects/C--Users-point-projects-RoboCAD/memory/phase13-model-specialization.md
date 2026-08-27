---
name: phase13-model-specialization
description: Phase 13 model specialization — fine-tuning scaffolding complete plus Claude 5 integration and first Claude Sonnet 5 benchmark run.
metadata:
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-27T07:52:31.036Z
---

Phase 13 — model specialization / fine-tuning — has produced its scaffolding and is now being validated against both local Ollama models and Claude 5.

## Local-model specialization (Ollama)

**Dataset build results:**
- 30 prompts from `benchmarks/complexity_ladder.json`
- 20 successful validated feature trees (66.7% success rate)
- Split into 16 train / 4 test examples
- Files: `training/feature_tree_dataset.jsonl`, `feature_tree_train.jsonl`, `feature_tree_test.jsonl`, `dataset_summary.json`
- Note: many failures were local-model timeouts on slower prompts; subsequent re-runs hit the same timeout even at 240 s, so the first completed run was kept.

**Ollama few-shot specialization:**
- `python scripts/build_ollama_modelfile.py` selected 10 diverse examples by tier and embedded them into the Feature-Tree system prompt.
- `ollama create robocad-ft -f models/robocad-ft/Modelfile` succeeded.
- System prompt length: ~81 KB.

**A/B evaluation:**
- Command: `python scripts/evaluate_finetuned.py --base-model qwen3-coder:latest --specialized-model robocad-ft:latest --dataset training/feature_tree_test.jsonl`
- Output: `output/benchmarks/finetune_eval_20260825_022701/`
- Produces `comparison.json` and `comparison_report.md` with pass-rate delta.

## Claude 5 cloud integration

Because the Phase 8 baseline with `qwen3-coder:latest` was 26/30 (86.7%) and local fine-tuning is awaiting dataset completion, we also wired the codebase to Claude 5 to compare cloud vs local performance.

**Benchmark results with `claude-sonnet-5-20250501`:**
- Full Phase 8 complexity benchmark: **21/30 (70.0%)** after Anthropic SDK compatibility fixes.
- T1–T4 aggregate: **21/24 (87.5%)**, meeting the ≥80% quality gate.
- Targeted T4 re-run after nested-fence extraction hardening: **4/6 (66.7%)** — one geometry failure (2-DOF arm assembly non-watertight), one empty-text-block timeout (parallel-jaw gripper).
- Targeted T5 re-run after nested-fence extraction hardening: **1/6 (16.7%)** — T5 remains genuinely hard: nested-fence syntax errors, empty text blocks, and geometry fillet failures.
- Root causes: token/context length, model emits nested fences during self-correction, and genuine geometry complexity (assemblies, fillets, fine features).

**Compatibility fixes committed (see [[claude5-integration-fixes]]):**
- httpx2/httpcore2 → standard httpx/httpcore shim in `ai_cad/__init__.py`.
- `_anthropic_base_url()` forces official `https://api.anthropic.com` when env points local.
- `_first_text_block()` skips Claude 5 `ThinkingBlock` and returns first `TextBlock`.
- Retry loop for empty Claude 5 text blocks (increased from 3 to 5 attempts).
- Default `max_tokens` raised to 4096 in `ai_cad/generator.py` and `ai_cad/api.py`.
- `_extract_code_block()` aggressively strips nested markdown fences from self-correction responses and falls back to fence-free code detection.

## Code state

- `ai_cad/generator.py` — local-model timeout fixes + Claude 5 compatibility + nested-fence extraction.
- `ai_cad/api.py` — default `max_tokens=4096`.
- `ai_cad/__init__.py` — httpx2/httpcore2 shims.
- Four Phase 13 scripts committed: `build_training_dataset.py`, `build_ollama_modelfile.py`, `finetune_model.py`, `evaluate_finetuned.py`.
- `tests/test_phase13.py` committed.
- Full pytest suite: **134/134 passing**.

## Phase 13 verdict

Phase 13 is **green on the T1–T4 ≥80% criterion** (87.5%). T5 is explicitly a known-hard tier and is not gating the next phase. Local fine-tuning scaffolding is in place and can be iterated in parallel; it is not a blocker for Phase 14A.

## Next steps

1. ✅ Claude 5 integration and extraction fixes committed and pushed.
2. Move to **Phase 14A GEDA Bridge**: build `ai_cad/geda_bridge/exporter.py` to export any part/assembly to MuJoCo/URDF and verify bundles.
3. Continue local-model fine-tuning (`robocad-ft:latest`) as a background experiment; re-evaluate once dataset quality improves.
4. Keep README/PLAN/memory files in sync with Phase 14A progress.

**Related:** [[claude5-integration-fixes]] | [[phase8-baseline-in-progress]] | [[robocad-path-analysis]] | [[robocad-end-to-end-roadmap]]
