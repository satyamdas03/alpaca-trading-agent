# QuantCoder-3B Design — Open, Verified, Calibrated Financial Code Generation

**Date:** 2026-07-30  
**Project:** [quantcoder-3b](https://github.com/satyamdas03/quantcoder-3b)  
**Status:** Design spec — awaiting user review before implementation plan  
**Constraint:** Licensing-clean path only. No patented formal methods, no proprietary IP, no encumbered datasets. All outputs Apache 2.0.

---

## 1. Purpose

Design the next extraordinary version of QuantCoder-3B: a small, open-weight language model that generates point-in-time (PIT) quant factor code, verifies every output by execution, and provides calibrated uncertainty for each prediction.

The goal is to create a public, reproducible, trustable quant-coding assistant — not a black-box strategy generator.

---

## 2. Vision

> **QuantCoder-3B: the first fully open-source, execution-verified, point-in-time financial code generation system — model, dataset, verifier, and benchmark all under Apache 2.0.**

Every output is either:
- **Verified PIT-safe code** that compiles, runs, and matches a reference implementation, or
- **A calibrated refusal** with a confidence estimate when the model cannot produce a safe answer.

---

## 3. Why This Is Extraordinary

1. **No open model currently guarantees PIT-safe financial code.** Existing models generate code that looks correct but leaks future data.
2. **We attack "laundered alpha" at the source.** Code runs, Sharpe looks real, but the model is cheating — our verifier rejects this before deployment.
3. **We publish the entire trust chain:** dataset, verifier, benchmark, model weights, training configs, logs.
4. **We leverage existing open-source moats:** factor-forge, conformal-finance, lumina-lob, and the AI Trading Brain.
5. **We add calibrated uncertainty** using conformal prediction — a mathematically grounded way to say "I don't know."

---

## 4. Target Audiences

| Audience | Problem | What we deliver |
|---|---|---|
| Quant researchers | Need trustworthy factor code fast | Verified PIT factor generation + benchmark |
| Fintech builders | Need a small, deployable financial AI | Open weights, clean Apache 2.0 license |
| Retail platforms | Need strategy builders without hidden bias | Transparent, execution-verified code |
| Wealthtech / RegTech | Need on-premise, auditable AI | Local inference, deterministic verifier, no API calls |
| Open-source community | Needs a reproducible finance-code baseline | Public dataset, benchmark, and leaderboard |

---

## 5. Core Differentiators

1. **Execution verification** — every training example and every generated candidate is compiled and run against a synthetic panel.
2. **Point-in-time enforcement** — heuristic + structural checks reject `.shift(-n)`, centered rolling windows, forbidden future columns, and future-dependent indexing.
3. **Reference correlation** — generated factors are scored against factor-forge reference implementations.
4. **Calibrated uncertainty** — conformal prediction provides per-example confidence and refusal thresholds.
5. **Fully open** — Apache 2.0 weights, dataset, code, benchmark, logs.

---

## 6. Architecture

```text
Inkling / Together / Fireworks / local teacher API
           ↓
FactorCorpus + DatasetGenerator
           ↓
CodeVerifier: syntax → run → shape → PIT → reference correlation
           ↓
verified_pilot_1.jsonl + verified_overnight.jsonl → verified_combined.jsonl
           ↓
Unsloth QLoRA SFT + optional GRPO with verifiable rewards
           ↓
CalibratedUncertainty head (via conformal-finance)
           ↓
14-factor benchmark + public leaderboard
           ↓
Hugging Face weights + FastAPI/vLLM serving
```

### Components

| Component | File(s) | Responsibility |
|---|---|---|
| FactorCorpus | `quantcoder/data/corpus.py` | Registry of canonical factors and reference implementations |
| DatasetGenerator | `quantcoder/data/generator.py` | Calls teacher API to generate NL → code pairs |
| CodeVerifier | `quantcoder/data/verifier.py` | Verifies generated code by execution and PIT checks |
| DatasetFormatter | `quantcoder/data/formats.py` | Converts to Alpaca / ShareGPT / Hugging Face datasets |
| SFTTrainer | `quantcoder/training/sft_unsloth.py` | Unsloth QLoRA supervised fine-tuning |
| GRPOTrainer | `quantcoder/training/grpo_unsloth.py` | Optional verifiable-reward RL |
| CalibratedHead | `quantcoder/training/calibration.py` | Conformal confidence model |
| Evaluator | `quantcoder/evaluation/benchmark.py` | Runs 14-factor benchmark and computes metrics |
| FactorGenerator | `quantcoder/inference/model.py` | Loads model + adapter and generates code |
| serve | `scripts/serve.py` | FastAPI endpoint (currently placeholder) |

---

## 7. Dataset Strategy

### Current state
- `data/verified_pilot_1.jsonl`: 35 examples
- `data/verified_overnight.jsonl`: 103 examples
- `data/verified_combined.jsonl`: 138 examples
- 14 factor categories

### Target for next phase
- **500 verified examples** within 2–3 weeks.
- Add **adversarial refusal examples** where the prompt asks for something PIT-unsafe and the correct response is a refusal with explanation.
- Add **multi-asset / multi-frequency variants** (daily, weekly, monthly rebalancing guards).
- Include **conformal calibration labels**: difficulty tags, correlation confidence, and correctness flags.

### Verification rules
1. Python syntax valid.
2. Contains `factor(df: pd.DataFrame) -> pd.Series`.
3. Runs without error on synthetic `(date, symbol)` panel.
4. Output shape/index matches the panel.
5. No `.shift(-n)`, centered rolling windows, forbidden future columns.
6. Spearman correlation ≥ 0.5 against reference implementation.

---

## 8. Model Strategy

### Phase 1 (now): Prove the loop on Qwen2.5-1.5B
- Fix the CUDA illegal-instruction error blocking inference.
- Get real combined-run benchmark numbers.
- Add calibrated uncertainty head.
- Publish updated README and results.

### Phase 2: Scale to Qwen3.5-4B
- Train on 500+ verified examples on a 24 GB cloud GPU.
- Keep Apache 2.0 base model.
- Publish adapter and merged weights on Hugging Face.

### Phase 3: AlphaWeaver-7B (future)
- Expand to reasoning + code + agentic tool use.
- Add SEC filing / earnings-call reasoning traces.
- Integrate into QuantAlpha AI as a copilot.

---

## 9. Evaluation & Benchmark

### Primary metric: Verified PIT-Safe Accuracy (VAcc)
Fraction of generated factors that:
1. Compile
2. Run
3. Have correct shape/index
4. Are PIT-clean
5. Correlate ≥ 0.5 with reference

### Secondary metrics
- `compile_ok`, `runs_ok`, `shape_ok`, `pit_clean`
- Mean Spearman correlation
- Mean score
- Conformal coverage at target alpha
- Refusal rate on adversarial examples

### Benchmark leaderboard
- Public JSON file in `logs/leaderboard.json`
- Tracks each model variant (base, PoC, combined, target)
- Updated automatically after each evaluation run

---

## 10. Calibrated Uncertainty

### Approach
Use `conformal-finance` to build a lightweight calibration layer:
- During training/validation, collect nonconformity scores per example.
- At inference, compute a prediction set or confidence interval for whether the generated code will pass verification.
- If the confidence is below threshold, refuse and ask for clarification.

### Why this is safe from licensing risk
- `conformal-finance` is our own Apache 2.0 package.
- Conformal prediction is a well-established, non-patented statistical framework.

---

## 11. Risk & Licensing Map

| Risk | How we avoid it |
|---|---|
| Patent on formal PIT verification | Do not use proprietary type-and-effect checkers. Use transparent execution-based verification only. |
| Proprietary dataset | Generate all data via API or write it ourselves. No scraping of paywalled sources. |
| Base model license | Use Apache 2.0 / MIT base models only: Qwen3.5-4B, Qwen2.5-1.5B, Phi-4-mini. |
| Teacher output license | Inkling is Apache 2.0; API-generated outputs are not encumbered. |
| Conformal method patents | Use standard split/CQR/ACI methods; cite public literature. |

---

## 12. Immediate Implementation Plan (High Level)

1. Fix CUDA illegal-instruction error in evaluation.
2. Rerun combined-dataset evaluation and capture real VAcc.
3. Update README with honest results and corrected dataset counts.
4. Add adversarial refusal examples to the dataset.
5. Build calibrated uncertainty head.
6. Scale dataset to 500 verified examples.
7. Train Qwen3.5-4B on a rented 24 GB GPU.
8. Publish weights and benchmark leaderboard on Hugging Face.

---

## 13. Success Criteria

- [ ] Inference works locally on RTX 5060 or via documented cloud fallback.
- [ ] Combined-run VAcc is measured and reported honestly.
- [ ] README reflects the new "open, verified, calibrated" positioning.
- [ ] Dataset reaches 500 verified examples.
- [ ] Conformal calibration layer is integrated and tested.
- [ ] Qwen3.5-4B adapter is trained and published.
- [ ] Public benchmark leaderboard exists.

---

## 14. Non-Goals

- No proprietary data sources.
- No patented formal verification methods.
- No closed-source weights or benchmarks.
- No live trading deployment in this phase.
- No claim of profitability — only verifiable correctness.

---

## 15. Open Decisions

1. Do we publish intermediate Qwen2.5-1.5B adapters or wait for Qwen3.5-4B?
2. Do we add a public Hugging Face dataset card for the verified examples?
3. Do we target a specific paper/workshop deadline (e.g., NeurIPS workshop, ICAIF, ACL industry)?

---

END OF SPEC
