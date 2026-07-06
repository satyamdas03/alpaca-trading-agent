# Design: Honest Agent Protocol — Empirical Scaling (A) + Theoretical Tightening (C)

**Date:** 2026-07-06  
**Status:** Approved by user. Implementation begins.  
**Goal:** Push the Honest Agent Protocol from "promising proof-of-concept" (score ~65) toward a top-tier paper (score 85+) using only local compute. No Anthropic API credits will be used.

---

## Summary

We execute two tracks in parallel where possible:

1. **Track A — Empirical scaling:** Run larger local-LLM sweeps with `llama3:8b` and `mistral` to produce statistically meaningful separation between naive validation-feedback and protocol defenses. Generate a real-LLM FDR-vs-trials plot.
2. **Track C — Theoretical tightening:** Replace the conservative SparseValidate polynomial factor with a sharper **maximal leakage** bound (Esposito et al. 2019) for the metered accept/reject channel. Implement the bound, add a defense comparator, and update the paper theorem.

After A+C, we will evaluate whether Track B (real-discovery domain demo) is needed.

---

## Track A: Empirical scaling

### A1 — Scale `llama3:8b` to `m=50, reps=5`

Run the following defenses one batch at a time (2 concurrent maximum to avoid Ollama overload):

- `naive`
- `protocol`
- `metered`
- `e_bh`
- `sparse_metered`

Each defense: `m=50`, `reps=5`. Total trials per defense: 250. Expected runtime per defense: ~58 minutes at 14s/trial if run alone; ~2 hours per batch of 2 concurrent.

Output files: `{defense}_llm_attack_results.{json,md}`.

### A2 — Model robustness with `mistral`

Run all 5 defenses on `mistral` with `m=30`, `reps=3`. Use the same 2-at-a-time batching. This checks whether the separation is an artifact of `llama3:8b`.

### A3 — Aggregate and visualize

Create a script that:
- Reads all `docs/paper/*_llm_attack_results.json` files.
- Produces a single comparison table.
- Generates `docs/paper/llm_fdr_by_trials.png`: mean false certs vs trials for `naive` vs firewalls.
- Updates `aqra/docs/paper/honest_agent_protocol.md` Section 4.3 with the final numbers and plot.

---

## Track C: Theoretical tightening

### C1 — Maximal leakage bound

For a metered accept/reject channel, the maximal leakage from validation $V$ to the accept bit $A_i$ at round $i$ is bounded by

$$\mathcal{L}(V \to A_i) \le \log\left(\frac{1}{\lambda}\right) \quad \text{bits}$$

under the null, because $\Pr(A_i = 1 \mid \text{null}) \le \lambda$. The multi-round transcript leakage is at most the sum if the bits are independent across null rounds, or bounded via directed information for adaptive dependence.

Implement in `aqra/src/aqra/conformal/multiple_testing.py`:
- `maximal_leakage_evalue(p, lambda_m)` — returns `2^{-\mathcal{L}} * indicator(p <= lambda_m) / lambda_m` as the corrected e-value.
- `maximal_leakage_bound(lambda_m)` — returns `log2(1/lambda_m)`.

### C2 — Maximal-leakage defense in attack suite

Add `maxleak_metered` to `aqra/scripts/attack_suite.py`:
- One-bit feedback at threshold `lambda_m`.
- E-value corrected by `2^{-leakage_bound}` before e-BH.
- Compare against `sparse_metered` (polynomial factor) and `metered` (uncorrected).

### C3 — Paper theorem update

Add **Theorem M** (maximal leakage wall) to `aqra/docs/paper/honest_agent_protocol.md`:
- States that under the metered channel, the leakage-corrected e-values satisfy $\mathbb{E}[e_i^* \mid \text{null}] \le 1$.
- Compares Theorem M (sharper) vs Theorem S (conservative SparseValidate safety case).

---

## Execution order (10 steps)

| Step | Work | Track | Approx. time |
|---|---|---|---|
| 1/10 | Write and commit this spec | Setup | 5 min |
| 2/10 | Run `naive` + `protocol` `llama3:8b` `m=50 reps=5` | A | ~2h |
| 3/10 | Run `metered` + `e_bh` `llama3:8b` `m=50 reps=5` | A | ~2h |
| 4/10 | Run `sparse_metered` `llama3:8b` `m=50 reps=5` | A | ~1h |
| 5/10 | Run `mistral` all defenses `m=30 reps=3` (batched) | A | ~2.5h |
| 6/10 | Aggregate results + plot + update paper | A | 20 min |
| 7/10 | Implement maximal leakage bound + unit tests | C | 30 min |
| 8/10 | Add `maxleak_metered` to attack suite and run | C | 20 min |
| 9/10 | Update paper with Theorem M and discussion | C | 20 min |
| 10/10 | Power/FDR figure + final commit and push | A+C | 20 min |

---

## Files touched

- `aqra/scripts/llm_adaptive_experiment.py` (no changes expected; already supports per-defense files)
- `aqra/scripts/monitor_llm_sweeps.py` (no changes expected)
- `aqra/src/aqra/conformal/multiple_testing.py` (new maximal leakage functions)
- `aqra/tests/conformal/test_evalue_multiple_testing.py` (new tests)
- `aqra/scripts/attack_suite.py` (new `maxleak_metered` defense)
- `aqra/docs/paper/honest_agent_protocol.md` (Section 4.3 update, Theorem M)
- `docs/superpowers/specs/2026-07-06-honest-agent-ac-design.md` (this file)

---

## Success criteria

- A: `naive` shows ≥1.0 mean false certs with ≥50% any-false-cert rate at `m=50`; all firewalls show ≤0.2 mean false certs.
- A: `mistral` reproduces the same qualitative separation.
- C: `maxleak_metered` certifies fewer false strategies than `sparse_metered` at same `m` (higher power).
- C: Paper contains both Theorem S (conservative) and Theorem M (sharper) with explicit comparison.

---

## Blockers

- Ollama server capacity. Mitigation: max 2 concurrent tasks, use loaded `llama3:8b` first.
- Runtime. Mitigation: steps are background-friendly; user can sleep/pause between steps.

---

## Why this pushes toward revolutionary

Track A turns the real-LLM demo from a 60-sample pilot into a 250+ sample result with cross-model replication. Track C replaces a pessimistic polynomial factor with an information-theoretic leakage measure that is actually tight. Together they close the two biggest gaps: weak empirical evidence and conservative theory.
