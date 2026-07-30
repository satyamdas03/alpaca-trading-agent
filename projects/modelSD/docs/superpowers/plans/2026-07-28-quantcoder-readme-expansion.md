# QuantCoder-3B README Expansion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the minimal `README.md` in the quantcoder-3b repo with a research-lab style, traction-oriented README that serves ML/quant researchers, open-source users, and hiring managers.

**Architecture:** Single-file documentation update (`README.md`) plus one commit/push. No code changes. All commands and numbers are sourced from existing repo files.

**Tech Stack:** Markdown, Git, GitHub.

## Global Constraints
- Target repo: `C:\Users\point\projects\quantcoder-3b` (existing public repo at https://github.com/satyamdas03/quantcoder-3b).
- License: Apache 2.0.
- Benchmark numbers must match `logs/poc_eval_run2.json` exactly.
- Do not overstate results; label in-progress work clearly.
- README should render well on GitHub desktop and mobile (under ~180 lines).

---

## Task 1: Read Existing README and Benchmark Numbers

**Files:**
- Read: `C:\Users\point\projects\quantcoder-3b\README.md`
- Read: `C:\Users\point\projects\quantcoder-3b\logs\poc_eval_run2.json`

**Interfaces:**
- Consumes: None
- Produces: Context for writing the new README.

- [ ] **Step 1: Read existing README**

Read `README.md` to preserve any useful phrasing and understand current structure.

- [ ] **Step 2: Extract benchmark numbers**

From `logs/poc_eval_run2.json`, extract:
- total: 14
- compile_ok: 28.6%
- runs_ok: 14.3%
- shape_ok: 14.3%
- pit_clean: 14.3%
- mean_correlation: 0.425
- mean_score: 12.9%

- [ ] **Step 3: Note dataset counts**

From `data/` directory, confirm:
- verified_pilot_1.jsonl: 35 examples
- verified_overnight.jsonl: 78 examples
- verified_combined.jsonl: 113 examples

---

## Task 2: Write Expanded README.md

**Files:**
- Modify: `C:\Users\point\projects\quantcoder-3b\README.md`

**Interfaces:**
- Consumes: Existing README content, benchmark numbers, dataset counts, spec from `docs/superpowers/specs/2026-07-28-quantcoder-readme-design.md`.
- Produces: New `README.md` content.

- [ ] **Step 1: Write hero section**

Replace the top of `README.md` with:
```markdown
# QuantCoder-3B

A small, open-weight language model that turns plain-English quantitative finance ideas into correct, runnable, point-in-time Python code.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)
[![Unsloth](https://img.shields.io/badge/Unsloth-QLoRA-green)](https://unsloth.ai/)

**Base model:** `Qwen3.5-4B` (target) / `Qwen2.5-1.5B` (PoC)  
**Teacher model:** `Inkling` by Thinking Machines Lab (via Together AI)  
**Training framework:** `Unsloth` (free single-GPU QLoRA)  
**Verification engine:** custom `CodeVerifier` + `factor-forge` reference checks  
**License:** Apache 2.0
```

- [ ] **Step 2: Write quickstart section**

```markdown
## Quickstart

```bash
git clone https://github.com/satyamdas03/quantcoder-3b.git
cd quantcoder-3b
pip install -e .
cp .env.example .env  # add TOGETHER_API_KEY or INKLING_API_KEY

# Generate verified training examples
python scripts/scale_dataset.py --target 100 --provider together --variants 7

# Train on the combined dataset
python scripts/train.py --config configs/combined_config.json

# Evaluate the trained adapter
python scripts/evaluate.py unsloth/Qwen2.5-1.5B \
  --adapter-path models/qwen2.5-1.5b-combined/lora_adapter \
  --output logs/combined_eval.json
```
```

- [ ] **Step 3: Write what-makes-it-different section**

Include four bullets: verified-by-execution, point-in-time enforcement, reference correlation, fully open.

- [ ] **Step 4: Write architecture diagram**

Use the ASCII pipeline from the spec.

- [ ] **Step 5: Write dataset card**

Include the 113-example count, 14 factor categories, generation parameters, and verification rules.

- [ ] **Step 6: Write model card**

List PoC and target model configs from `configs/poc_config.json` and `configs/combined_config.json`.

- [ ] **Step 7: Write benchmark results table**

Use exact numbers from `logs/poc_eval_run2.json`. Add an in-progress row for the 113-example combined run.

| Model | Dataset | Compile OK | Runs OK | Shape OK | PIT Clean | Mean Correlation | Mean Score |
|---|---|---|---|---|---|---|---|
| Qwen2.5-1.5B + LoRA | 35 examples (PoC) | 28.6% | 14.3% | 14.3% | 14.3% | 0.425 | 12.9% |
| Qwen2.5-1.5B + LoRA | 113 examples (combined) | *in progress* | — | — | — | — | — |

- [ ] **Step 8: Write reproducibility, project structure, roadmap, citation sections**

Use the spec sections verbatim.

- [ ] **Step 9: Self-review the README for rendering**

Check that all markdown fences are closed, badges are valid, and tables align.

---

## Task 3: Commit and Push README

**Files:**
- Stage: `C:\Users\point\projects\quantcoder-3b\README.md`

**Interfaces:**
- Consumes: Updated `README.md`.
- Produces: Commit pushed to GitHub.

- [ ] **Step 1: Stage the README**

Run in the quantcoder-3b repo:
```bash
cd /c/Users/point/projects/quantcoder-3b
git add README.md
```

- [ ] **Step 2: Commit**

```bash
git commit -m "docs(readme): expand README with architecture, dataset card, benchmarks, and reproducibility" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 3: Push**

```bash
git push origin main
```

- [ ] **Step 4: Verify on GitHub**

Open `https://github.com/satyamdas03/quantcoder-3b/blob/main/README.md` and confirm the README renders correctly.

---

## Self-Review Checklist

1. **Spec coverage:** Hero, quickstart, differentiators, architecture, dataset card, model card, benchmarks, reproducibility, structure, roadmap, citation — all present.
2. **Placeholder scan:** No TBD/TODO.
3. **Number accuracy:** All benchmark percentages and counts verified against `logs/poc_eval_run2.json` and `data/*.jsonl`.
4. **Rendering:** Markdown fences closed, table columns aligned, badges valid.
