# Design: Honest Agent Protocol (moonshot track)

**Date:** 2026-07-04
**Status:** Track approved as auto-decision (user AFK; asked for AIAYN-level
breakthrough hunt; two-track structure recommended+adopted — ICAIF sprint
unaffected). User veto welcome.
**Slogan candidate:** "Verification is all you need."

## Thesis

Every field building LLM research agents optimizes the *generator*. We claim
the transferable breakthrough is the *verification protocol*: a way for an
autonomous agent to make empirical claims that a third party can trust
WITHOUT trusting the agent — with statistical guarantees that hold even when
the agent is adversarial.

Components (AQRA already prototypes all three in finance):
1. **Constrained claim language** — hypotheses expressible only in a grammar
   whose semantics make the classic cheats (look-ahead) unrepresentable.
2. **Pre-registration ledger** — register-before-eval; corrections computed
   over every attempt ever made; hash-chainable for third-party audit.
3. **Information-budgeted feedback wall** — the agent's feedback channel
   carries bounded information about the holdout; guarantee degrades
   gracefully and *measurably* with the budget.

## The open theorem (novel piece)

FDR/generalization guarantees under ADAPTIVE, ADVERSARIAL generation:
the generator is an LLM with memory across trials that may actively try to
reconstruct the holdout through its feedback. Adaptive data analysis (Dwork
et al. reusable holdout; max-information; typical-stability) gives tools but
has not been instantiated for agentic LLM loops. Target result: FDR ≤ α
whenever the feedback channel's information about the holdout is ≤ B bits,
with explicit B → guarantee curve; ledger makes the trial count m public and
binding.

## Killer experiment M2 (runnable now, no API keys)

Cheating-generator attack suite on synthetic + real panel data:
- Attacker strategies: (a) binary-search the holdout through
  accept/reject feedback, (b) mutation flooding around lucky seeds,
  (c) feedback-free random baseline.
- Defenses compared: naive loop (validation numbers fed back), ledger
  without wall, full protocol (ledger + train-only feedback).
- Metric: realized false discovery rate among "certified" claims vs number
  of trials. Prediction: naive curve climbs toward 1, protocol curve stays
  ≤ α. That plot is Figure 1 of the breakthrough paper.

## M2 VERDICT (2026-07-05): SEPARATION CONFIRMED — thesis survives

Commit e619731 (+ uncommitted online-FDR extension), artifacts
aqra/docs/paper/attack_results.*. At m=400 trials, hill-climb attacker:
naive 211.4 false certs (100% of campaigns), ledger-without-wall 43.85 DESPITE
BY-FDR (adaptive feedback voids p-value validity — the theorem's empirical
footprint), metered one-bit feedback 2.5 false certs (leaks, but slowly;
Theorem 2 regime), full protocol 0.0 (at/below alpha), conformal three-way-
split p-value 0.0 (distribution-free wall; Conformal Theorem 1), sequential-
BY online prefix `online_by` 0.0 (anytime-valid immortal wall; Theorem 3),
LORD-style fixed-spending `online_lond` 0.45 (empirical probe, unproved under
shared-$V$ dependence). Control: no_wall vs random attacker 0.0, isolating
adaptivity as the breaking force. Next: M3 cross-domain demo.

## M3 VERDICT (2026-07-05): TRANSFER CONFIRMED — not finance-specific

`aqra/scripts/ml_benchmark_demo.py`: synthetic 50-feature binary
classification with independent labels (pure-noise, all-null world).  A
linear-classifier generator hill-climbs for 400 trials:

- **Without wall** (feedback = validation p-value): mean 0.50 false
  certifications; generator overfits noise in the holdout.
- **With wall + batch BY-FDR** (feedback = train accuracy only): mean 0.00
  false certifications.
- **With wall + online BY** (`--online`): mean 0.00 false certifications.
- Exported ledgers verify independently with `verify_ledger.py`.

This confirms the ledger/wall/FDR stack transfers outside quantitative
finance: the primitive is a domain-agnostic guardrail for adaptive
hypothesis generation.

## PHASE A UPDATE (2026-07-05): E-value core implemented

The breakthrough direction identified in `2026-07-05-breakthrough-analysis.md`
has been implemented:

- `aqra/src/aqra/conformal/evalue.py` — `EValue` primitive, p-value→e-value
  conversion, and conformal e-value `E = -log P`.
- `aqra/src/aqra/conformal/multiple_testing.py` — `e_bh_rejections`,
  `online_e_bh_rejections` (e-LOND), and `dependence_adjusted_by`.
- `aqra/src/aqra/generate/ledger.py` — `e_value` column added to the ledger.
- `aqra/src/aqra/verify/proof_of_trial.py` — exporter/verifier support e-BH
  and online e-BH hash-chain audits.
- `aqra/scripts/attack_suite.py` — `e_bh`, `online_e_bh`, `dby` arms added.
- `aqra/scripts/ml_benchmark_demo.py` — `--e-value` flag added.
- `aqra/docs/paper/honest_agent_protocol.md` — rewritten around Theorem E
  (e-value firewall), SparseValidate leakage pricing, and conformal e-values.
- `aqra/tests/conformal/test_evalue_multiple_testing.py` — 8 new unit tests,
  all passing.

Attack suite full run at m=400:
- `e_bh`: 0.00 false certs
- `online_e_bh`: 0.00 false certs
- `dby`: 0.00 false certs
- `naive`: 216.85 false certs

## PHASE B UPDATE (2026-07-05): SparseValidate leakage calculus implemented

Phase B closes the leakage-accounting gap identified in the breakthrough
analysis:

- `aqra/src/aqra/conformal/multiple_testing.py` — `candidacy_threshold(alpha, m)`
  and `sparse_validate_transfer_bound(m, k)` with exact combinatorial formula
  and polynomial upper bound $(em/k)^k$.
- `aqra/tests/conformal/test_evalue_multiple_testing.py` — tests for
  candidacy-threshold sparsity, exact transfer bound, and polynomial dominance
  over $2^m$.
- `aqra/scripts/attack_suite.py` — new `sparse_metered` defense. It uses the
  candidacy threshold $\lambda = \alpha / \log(m+1)$, expected accepts
  $K_m \approx \lambda m$, and deflates universal e-values by the SparseValidate
  factor $\mathcal{T}(m,K_m)$ before running e-BH.
- `aqra/docs/paper/honest_agent_protocol.md` — Theorem S added: a formal
  SparseValidate-corrected e-BH guarantee for the metered accept/reject channel,
  with polynomial leakage factor priced into the e-values.

Attack suite full run at $m=400$:
- `sparse_metered`: **0.00 false certs** (conservative but valid worst-case
  leakage pricing)
- `metered`: 0.75 false certs (no SparseValidate correction)
- `no_wall`: 91.55 false certs
- `naive`: 200.80 false certs

Next: Phase C (real LLM adaptive experiment with Anthropic API key).

## Program milestones

- M1: formal threat model + theorem sketch (adaptive data analysis mapping) — DONE
- M2: attack suite + separation plot (start immediately, synthetic data) — DONE
- M3: cross-domain instantiation (ML benchmark claims — test-set overfitting
  on a public dataset) to demonstrate universality beyond finance — DONE
  (`aqra/scripts/ml_benchmark_demo.py`)
- M4: hash-chained public ledger format ("Proof-of-Trial") + verifier tool — DONE
  (`aqra/src/aqra/verify/proof_of_trial.py`, `aqra/scripts/verify_ledger.py`)
- M5: paper targeting a general venue (NeurIPS/ICML class) with AQRA/ICAIF
  as the domain instantiation citation — NEXT

## Relationship to ICAIF sprint

Two tracks. ICAIF submission (Aug 2) proceeds unchanged — it is the finance
instantiation and establishes priority on the ledger idea. Moonshot work
uses spare loop cycles; never blocks sprint tasks. If M2 separation plot is
strong before Jul 17 (results freeze), a compressed version may enter the
ICAIF paper as an additional experiment — decision point then.

## Honesty note

AIAYN-level impact cannot be scheduled. This is a structured search: clear
falsifiable thesis, cheap kill criteria (if the naive loop does NOT show
inflated FDR, or the protocol does not separate, the thesis dies and we say
so), and a survivor that scales. The user asked for everything needed to
make it possible; this is that, without pretending certainty.
