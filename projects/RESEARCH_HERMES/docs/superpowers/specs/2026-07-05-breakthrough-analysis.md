# Honest Agent Protocol — Path to Breakthrough-Level Paper

**Date:** 2026-07-05  
**Author:** Bull / AQRA  
**Status:** Deep analysis complete; implementation phase pending approval.

## Executive summary

The current Honest Agent Protocol paper is a strong methodology contribution: it frames statistical firewalls for adaptive LLM-driven research, provides four theorems (train-only wall, leaky wall, immortal wall, proof-of-trial), and includes a working code base with synthetic and small ML experiments. However, it is not yet extraordinary enough for a top-tier full paper because (1) Theorem 1 is largely an assembly of known parts, (2) Theorem 2’s $2^{-B}$ leakage degradation is worst-case exponential and pessimistic, (3) the online FDR procedure (`online_lond`) is empirical with an open shared-$V$ proof, and (4) no real-world LLM has been tested under the protocol.

The single highest-leverage move is to **replace the p-value machinery with e-values** (e-BH, online e-BH / e-LOND, dBY). This simultaneously:

1. Gives a new theorem with FDR control under **arbitrary adaptive dependence**, including the shared-validation setting.
2. Removes the log-correction that makes BY pessimistic.
3. Proves the online firewall under the same shared-$V$ dependence that currently breaks LORD-style analysis.
4. Provides the natural currency for a real-LLM experiment, where each generated hypothesis emits a calibrated e-value.

After this upgrade the paper’s unique claim becomes:

> **The first adversarially robust, anytime-valid FDR firewall for autonomous AI-driven scientific discovery that provably controls false discoveries even when the agent reads its own rejections and keeps reusing the same validation data.**

This document lays out the literature, the theorem sketch, the differentiation from competing work, and a concrete implementation roadmap.

---

## 1. Current gaps in detail

| Gap | Current state | Why it weakens the paper |
|-----|--------------|--------------------------|
| **Theorem 1 is “an assembly of known parts”** | Conformal split + BY-FDR on held-out $V$. | Pre-registration + multiple-testing correction is standard. The framing is new, but the guarantee is not. |
| **Theorem 2 leakage is pessimistic** | Max-information bound $I_\infty^\beta(V;\Phi)\le B$ yields FDR $\le \alpha/2^B$. | A $2^{-B}$ degradation is empirically implausible and makes the theorem a curiosity. Reviewers will ask for a tighter leakage calculus. |
| **`online_lond` is empirical** | LORD-style thresholds with shared $V$; proof open. | The strongest online claim is a conjecture supported by simulations. Top venues will demand a proof. |
| **No real LLM deployment** | Synthetic hill-climbers and hand-coded attacks. | The problem the paper solves is LLM p-hacking, but no LLM has actually been subjected to the firewall. |

---

## 2. The e-value upgrade

### 2.1 What e-values are

An **e-value** for a null hypothesis $H_0$ is a non-negative random variable $E$ such that $\mathbb{E}_{H_0}[E] \le 1$. It can be interpreted as a fair bet against the null: the null expects to lose money. E-values compose under optional continuation, filtering, and averaging in ways that p-values do not.

### 2.2 Key literature

- **Wang & Ramdas (2022).** *"False discovery rate control with e-values."* JRSSB. Introduces e-BH, the e-value analog of Benjamini-Hochberg. FDR control holds under **arbitrary dependence** of the e-values.
- **Xu & Ramdas (2024).** *"Online multiple testing with e-values."* Introduces online e-BH (also called e-LOND): anytime FDR control for sequential e-values under arbitrary dependence.
- **Fischer, Xu & Ramdas (2024).** *"Gambling-based confidence sequences and multiple testing."* GAME: growth-rate adaptive e-values that recover power in online settings.
- **Fithian & Lei (2022).** *"Calibrated multiple testing."* Dependence-adjusted BY (dBY): uniformly dominates standard BY under arbitrary dependence.
- **Dwork, Feldman, Hardt, Pitassi, Reingold & Roth (2015).** *"Generalization in Adaptive Data Analysis and Holdout Reuse."* NeurIPS. SparseValidate: rare accepts give polynomial transfer bounds for adaptive Boolean queries.
- **Esposito, Gastpar & Issa (2019).** *"Generalization error bounds via maximal leakage."* Tighter leakage measure than max-information for adaptive data analysis.
- **NeurIPS 2024 adversarial BH paper** (Kumar et al. / title may vary) — demonstrates that p-value BH can be adversarially inflated, motivating e-value robustness.
- **Sargsyan 2025** — close competitor using LORD++ + Lean 4 formalization; p-value based, dependence assumptions needed.

### 2.3 Why e-values close all four gaps

| Gap | E-value solution |
|-----|-----------------|
| **Theorem 1** | Replace BY-FDR with **conformal e-BH**. Theorem becomes: FDR $\le \alpha$ under arbitrary adaptive dependence between the generator and the test statistics, because e-BH does not require independence. |
| **Theorem 2** | Leakage causes **expected e-value inflation**, not exponential degradation. For the metered accept/reject channel, combine e-values with **SparseValidate** (Dwork et al. 2015): a candidacy threshold $\lambda$ keeps the number $K$ of accepts small, the transcript has at most $\sum_{j=0}^{K}\binom{m}{j}$ possibilities, and the transfer factor becomes polynomial in $m$ instead of $2^m$. |
| **online_lond** | Replace LORD with **online e-BH / e-LOND**. Shared-$V$ adaptivity is now inside the model and still FDR-controlled. |
| **Real LLM** | LLM emits e-values naturally: each hypothesis is paired with a betting score / conformal e-value. The wall-on/off experiment is cleaner and has a stronger null guarantee. |

---

## 3. The new core theorem

### Theorem E — E-value firewall

Let $\Phi$ be an adaptive hypothesis generator that operates in rounds $t=1,2,\dots$. At round $t$, $\Phi$ proposes a candidate signal $S_t$ and an associated e-value $E_t$ computed on a fixed validation set $V$. The generator may use the entire history $(S_1,E_1,R_1),\dots,(S_{t-1},E_{t-1},R_{t-1})$, where $R_t\in\{0,1\}$ indicates whether $S_t$ was selected by the firewall.

Assume that for every null signal $S_t$,

$$\mathbb{E}\left[ E_t \mid \mathcal{F}_{t-1} \right] \le 1,$$

where $\mathcal{F}_{t-1}$ is the filtration generated by $\Phi$ up to round $t-1$.

Apply the **online e-BH** (e-LOND) procedure with target FDR $\alpha$ to the stream $(E_1,E_2,\dots)$. Then for every $t \ge 1$,

$$\operatorname{FDR}_t \;:=\; \mathbb{E}\!\left[ \frac{|\{i\le t : H_i\text{ null and } R_i=1\}|}{\max\{1, \sum_{i\le t} R_i\}} \right] \;\le\; \alpha.$$

The guarantee holds under **arbitrary dependence** among the e-values, including the dependence induced by the shared validation set $V$ and by the generator reading past rejections.

### Why this is a breakthrough

1. **Positive + adversarially robust.** It gives the LLM full adaptivity (read rejections, reuse $V$, hill-climb) while still controlling FDR.
2. **No log correction.** BY and its online variants pay a $\log m$ factor under dependence; e-values do not.
3. **Shared-$V$ proof is immediate.** The shared validation set is just another source of dependence, and e-BH/online e-BH handle arbitrary dependence by design.
4. **Constructive for LLMs.** An LLM can be forced to emit valid e-values via conformal prediction, betting scores, or likelihood ratios.

---

## 4. Sharper leakage accounting (Theorem 2 upgrade)

### 4.1 Problem with the current bound

Current Theorem 2: if $I_\infty^\beta(V;\Phi)\le B$, then FDR $\le \alpha/2^B$.

A leakage of $B=10$ bits gives $\alpha/1024$; a leakage of $B=1$ bit halves the effective $\alpha$. This is far too pessimistic in practice: the attack suite shows leakage but not catastrophic FDR blow-up.

### 4.2 SparseValidate + rare accepts = polynomial leakage bound

The metered feedback channel reveals only accept/reject bits. This channel is **sparse**: if we use a candidacy threshold $\lambda$ separate from the final FDR level $\alpha$ (e.g., $\lambda = \alpha / \log m$), then under the null the number $K$ of accepts is concentrated around $\lambda m$. **SparseValidate** (Dwork et al., NeurIPS 2015) then bounds the number of possible transcripts by

$$\sum_{j=0}^{K}\binom{m}{j} \le \left(\frac{em}{K}\right)^{K},$$

so the transfer lemma gives

$$\Pr(p_i \le u) \le \left(\frac{em}{K}\right)^{K} u + \beta_0.$$

With $\lambda = \alpha / \log m$ this factor is polynomial in $m$ rather than exponential. This is the direct replacement for the current $2^{-B}$ bound.

### 4.3 E-value leakage calculus

For e-values, leakage acts on the **expectation** rather than the entire distribution. Suppose the generator obtains $b$ bits of information about $V$. Under a standard likelihood-ratio / Hellinger argument, the expected null e-value can inflate by at most $2^b$:

$$\mathbb{E}[E_t \mid \text{leakage of } b \text{ bits}] \le 2^b.$$

Consequently, if we run e-BH at threshold $\alpha / 2^b$, FDR control is preserved. The degradation is multiplicative in the e-value budget rather than exponential in the FDR budget. Layering SparseValidate on top means the inflation $2^b$ is applied to a channel whose transcript size is already polynomially bounded.

### 4.4 Maximal-leakage tightening

Replace max-information with **maximal leakage** (Esposito et al. 2019):

$$\mathcal{L}(V\to\Phi) \;=\; \sup_{P_V} \frac{I(V;\Phi)}{\log |\mathcal{V}|}.$$

Maximal leakage is designed for adaptive data analysis and can give better constants. We can state Theorem 2 as:

> If the maximal leakage from $V$ to the generator $\Phi$ is $L$, then there exists a deterministic inflation factor $\gamma(L)$ such that the e-value firewall at level $\alpha/\gamma(L)$ controls FDR at $\alpha$.

Initial target: prove $\gamma(L) \le 2^{\kappa L}$ for a small constant $\kappa$ (ideally $\kappa=1$), then tighten via Hellinger contraction.

---

## 5. Real-world LLM experiment

### 5.1 Design

Create `aqra/scripts/llm_adaptive_experiment.py` with the following protocol:

1. **Nullified universe.** Generate synthetic classification data where features and labels are independent. No true signal exists.
2. **LLM generator loop.** At each round, prompt an LLM (Claude 3.5 Sonnet) to propose a binary classification feature / rule based on:
   - The full history of proposed rules,
   - Which rules were certified / rejected,
   - The raw validation set $V$ (or a summary).
3. **Wall arms.**
   - **No wall:** LLM chooses rules freely; nominal uncorrected threshold.
   - **BY wall:** conformal p-values + BY-FDR.
   - **E-wall:** conformal e-values + online e-BH.
4. **Replication.** Run 20 independent universes × 200–400 rounds each.
5. **Metrics.** False discovery proportion, empirical FDR, number of discoveries, wall violations, API cost.

### 5.2 Expected result

- **No wall:** LLM p-hacks; FDR → 1 as rounds progress.
- **BY wall:** FDR controlled when generator is weakly adaptive, but breaks under strong shared-$V$ adaptivity.
- **E-wall:** FDR controlled throughout, including when the LLM reads its own rejection history and reuses $V$.

### 5.3 Cost estimate

- 20 reps × 300 rounds × ~1.5k input + 0.5k output tokens.
- Claude 3.5 Sonnet: ~$3 per 1M input / $15 per 1M output.
- Total: ~$2,000–$2,500.
- Pilot first with Haiku: ~$200 to confirm the effect.

### 5.4 Code changes needed

- Extend `aqra/src/aqra/ledger.py` so `TrialsLedger` can serialize LLM prompts/responses.
- Add `LLMGenerator` class in `aqra/src/aqra/generators/llm_generator.py` that wraps Anthropic API and emits e-values or p-values.
- Add `llm_adaptive_experiment.py` script.
- Wire the experiment output into `aqra/src/aqra/verify/proof_of_trial.py` so each run is hash-chained and auditable.

---

## 6. Differentiation from competing work

| Work | Approach | Our difference |
|------|----------|---------------|
| **Sargsyan 2025** | LORD++ + Lean 4 formalization + scaffolding | LORD++ needs p-value independence/PRDS; we use e-values and control FDR under arbitrary dependence, including shared-$V$ adaptivity. |
| **NeurIPS 2024 adversarial BH** | Shows BH is brittle to adversarial p-values | We sidestep p-values entirely; e-BH is robust by construction. |
| **Accounting/LLM p-hacking papers** | Empirical demonstrations of LLM p-hacking | We provide a deployable, provable firewall rather than just documenting the problem. |
| **Conformal prediction + LLM papers** | Uncertainty quantification for LLM outputs | We integrate conformal e-values into an adaptive multiple-testing protocol with online guarantees. |

---

## 7. Implementation roadmap

### Phase A — E-value core (1–2 days)
1. Implement `EValue` primitive.
2. Implement offline e-BH and online e-BH / e-LOND in `aqra.conformal.multiple_testing`.
3. Implement dBY as drop-in BY replacement.
4. Add Theorem E to paper draft; rewrite Theorem 1 around e-BH.

### Phase B — Leakage calculus (1–2 days)
1. Add a **candidacy threshold** $\lambda$ to the metered channel, separate from the final FDR level $\alpha$. Suggested $\lambda = \alpha / \log m$ so null accepts are rare.
2. Bound the number $K$ of accept bits by $K = O(\lambda m)$ with high probability and prevent duplicate resubmissions so $K$ cannot be artificially inflated.
3. Apply **SparseValidate** (Dwork et al. 2015) to replace the $2^{-B}$ factor with a polynomial transfer factor $(em/K)^K$.
4. Layer **e-BH** on top so the polynomial correction lives on e-value expectations and the BY log factor is removed.
5. Optionally add a **maximal-leakage** variant for non-sparse channels.
6. Run leakage experiments comparing p-value vs e-value degradation.

### Phase C — Real LLM experiment (2–3 days)
1. Build `llm_adaptive_experiment.py`.
2. Pilot with Haiku (small scale).
3. Full run with Claude 3.5 Sonnet.
4. Integrate with proof-of-trial ledger/verifier.

### Phase D — Paper rewrite (1–2 days)
1. Lead abstract with e-value firewall.
2. Restructure theorems:
   - Theorem 1: conformal e-BH offline wall
   - Theorem 2: leakage as e-value inflation
   - Theorem 3: online e-BH / immortal wall
   - Theorem 4: proof-of-trial verifier
3. Add real-LLM experiment section with wall-on/off separation plot.
4. Sharpen related-work comparison.

---

## 8. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Reviewers unfamiliar with e-values | Include a short primer; frame e-values as “bets against the null” and e-BH as the natural BH analog. |
| E-value power lower than p-value BY | Use dBY baseline + GAME adaptive e-values; report explicit power/FDR trade-offs. |
| Real LLM experiment too expensive | Pilot with Haiku first; run full Sonnet only after pilot shows expected separation. |
| Leakage constants still loose | Start with conceptual upgrade; tighten constants in a follow-up. The new theorem form is the main contribution. |
| Sargsyan 2025 has formalization | We can add a formal specification of the e-value firewall in Lean 4 in a subsequent sprint; it is not required for the core theorem. |

---

## 9. Decision

**Recommended next action:** implement Phase A immediately. It is the lowest-risk, highest-payoff step and unblocks Phases B, C, and D. Once the e-value core is in place, the paper has a genuinely new theorem and a clear path to the real-LLM experiment.

If Phase A is approved, begin with `aqra/src/aqra/conformal/evalue.py` and update `multiple_testing.py` to expose `e_bh_rejections` and `online_e_bh_rejections`.
