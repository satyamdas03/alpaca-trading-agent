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

## Program milestones

- M1: formal threat model + theorem sketch (adaptive data analysis mapping) — DONE
- M2: attack suite + separation plot (start immediately, synthetic data) — DONE
- M3: cross-domain instantiation (ML benchmark claims — test-set overfitting
  on a public dataset) to demonstrate universality beyond finance — NEXT
- M4: hash-chained public ledger format ("Proof-of-Trial") + verifier tool — DONE
  (`aqra/src/aqra/verify/proof_of_trial.py`, `aqra/scripts/verify_ledger.py`)
- M5: paper targeting a general venue (NeurIPS/ICML class) with AQRA/ICAIF
  as the domain instantiation citation

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
