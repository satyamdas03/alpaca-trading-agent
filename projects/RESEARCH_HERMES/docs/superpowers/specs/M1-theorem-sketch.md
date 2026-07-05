# M1 — Threat Model and Theorem Sketch (Honest Agent Protocol)

**Date:** 2026-07-04. Companion to
`2026-07-04-honest-agent-protocol-moonshot.md`; empirical footprint =
attack suite commit `e619731` (`aqra/scripts/attack_suite.py`).

## 1. Setup and threat model

- Holdout (validation) sample $V$: in the trading instantiation, the
  validation-window return panel; in general, any data reserved for
  certification.
- Training sample $T$, independent of $V$.
- Generator $G$: an arbitrary randomized algorithm **with memory** (an LLM
  agent). In rounds $i = 1, \dots, m$ it emits a candidate hypothesis $a_i$
  (a program in the constrained DSL). $G$ is **adversarial**: it may be
  designed solely to force false certifications.
- Feedback channel: after round $i$ the protocol reveals $F_i$ to $G$.
- Ledger: each $a_i$ is registered before evaluation; $m$ and the full
  transcript are public and binding (hash-chainable). Failed/invalid trials
  receive $p_i = 1$.
- Test statistic: each candidate gets a validation p-value $p_i$ computed
  on $V$ (t-test in the current code; conformal p-value in the clean
  version — see §5.2). All candidates in the attack model are null:
  certification of any $a_i$ is a false discovery.

**Assumptions.**
- (A1) $T \perp V$.
- (A2) Under the null, $p_i$ is super-uniform when $a_i \perp V$:
  $\Pr(p_i \le u) \le u$.
- (A3) The number of trials $m$ (or the stopping rule) is a function of
  train-side information only — enforced operationally by the ledger:
  the FDR correction at any audit time runs over ALL registered trials,
  so "stop when something certifies" cannot shrink the denominator.

## 2. Theorem 1 (the wall): exact FDR control against arbitrary agents

**Claim.** If every $F_i$ is measurable with respect to
$\sigma(T, a_1, \dots, a_i, \text{G's coins})$ — i.e., the feedback contains
train-window information only — then for every strategy of $G$:

1. Each $a_i$ is independent of $V$ (induction: $a_i$ is a function of
   past feedback and $G$'s coins, all $V$-independent under A1).
2. Hence each $p_i$ is super-uniform under its null (A2), regardless of the
   dependence among the $p_i$ (they share $V$).
3. Benjamini–Yekutieli at level $\alpha$ over the full ledger controls
   $\mathrm{FDR} \le \alpha$ — BY (2001) requires only marginal
   super-uniformity and tolerates arbitrary dependence.

**Status:** not deep once stated — the entire contribution is the
*protocol that makes its premises enforceable against an agent* (grammar
constrains $a_i$'s semantics; ledger fixes $m$; wall fixes the feedback
measurability). The attack suite shows each premise is load-bearing:
remove the wall and FDR fails empirically even with BY intact
(no_wall: 79.9 false certs at $m = 400$).

## 2.1 Conformal Theorem 1 (distribution-free wall)

The parametric t-test in Theorem 1 can be replaced with a split-conformal
p-value. The protocol now uses a **three-way split**:

- $T_{\text{train}}$ — visible to the generator for building candidates.
- $T_{\text{calib}}$ — visible only to the validator; used to calibrate
  nonconformity scores.
- $V$ — the held-out validation set; visible only to the validator.

The train-only feedback wall is strengthened to: $G$ sees only
$T_{\text{train}}$ and past train-measurable feedback. The validator computes
a nonconformity score $s_i(v)$ for each validation observation using a score
that is monotone in the evidence against the null (e.g. $s(r) = r$ for the
one-sided test that the strategy has positive edge). The split-conformal
p-value is

$$p_i = \frac{1 + \#\{u \in T_{\text{calib}} : s_i(u) \ge s_i(v)\}}{|T_{\text{calib}}| + 1}.$$

**Claim.** Under the same train-only wall, each $p_i$ is super-uniform under
its null, because $a_i$ is independent of both $T_{\text{calib}}$ and $V$ and
the conformal score is exchangeable under the null. Benjamini–Yekutieli at
level $\alpha$ over the full ledger therefore controls
$\mathrm{FDR} \le \alpha$ for every strategy of $G$, with **no parametric
assumption** on returns.

**Empirical footprint:** attack-suite arm `conformal` (three-way split +
split-conformal p-value + BY over ledger). At $m=400$ hill-climb trials it
produces **0.0 false certifications**, matching the t-test `protocol` arm and
confirming the distribution-free version of the wall.

## 3. Theorem 2 (leaky wall): graceful degradation under bounded leakage

Real systems leak: even publishing which candidates were *certified* is
feedback about $V$ (≈1 bit per certification decision).

**Claim (sketch).** Let the transcript $\Phi$ visible to $G$ satisfy a
max-information bound $I_\infty^{\beta}(V; \Phi) \le B$ bits. Then for any
event $E$ defined on $(V, \Phi)$,
$\Pr(E) \le 2^{B} \, \Pr_{V' \perp \Phi}(E) + \beta$
(max-information transfer; Dwork et al. 2015). Applying to
$E = \{p_i \le u\}$: effective super-uniformity degrades to
$\Pr(p_i \le u) \le 2^B u + \beta$. Consequently BY run at level
$\alpha / 2^B$ (with a $m\beta$ additive slack) restores
$\mathrm{FDR} \lesssim \alpha + m\beta$.

**Sources of the tool:** Dwork, Feldman, Hardt, Pitassi, Reingold, Roth
(reusable holdout / generalization in adaptive data analysis); Russo &
Zou (mutual-information bias bounds); typical stability. **The
instantiation for agentic LLM loops with an auditable ledger appears
new** — in particular the operational reading: *the protocol can meter the
channel* (e.g., accept/reject-only feedback ⇒ $B \le$ #decisions bits) and
price the correction accordingly.

## 4. Mapping to the attack suite (e619731)

| Suite arm | Model | Predicted | Observed (m=400, hill-climb) |
|---|---|---|---|
| naive | unbounded leakage, no correction | FDR → 1 | 216.8 false certs, 100% |
| no_wall | unbounded leakage + BY | premise of Thm 1 broken; BY powerless | 79.9 false certs |
| protocol | $B = 0$ (Thm 1) | FDR ≤ α | 0.05 false certs |
| no_wall + random attacker | valid p's (no adaptivity) | BY holds | ≈ 0.05 |

The fourth row is the control that isolates *adaptivity* (not dependence,
not multiplicity) as the breaking force.

## 5. Open problems (the research program)

1. **Tight budget accounting for structured feedback.** Our protocol leaks
   exactly: train stats (0 bits about $V$) + per-campaign certification
   decisions (≤ #certified bits). Sharpen $2^B$ for this structured channel;
   worst-case exponential pricing is likely far too pessimistic.
2. **Conformal p-values.** Replace the t-test with conformal p-values on
   exchangeable validation blocks → distribution-free, finite-sample
   version of Theorem 1 (removes the parametric caveat from A2). Natural
   fit — AQRA already has the conformal machinery.
3. **Online FDR for immortal agents.** A live agent never stops trialing;
   replace batch BY with online FDR (LORD/SAFFRON/ADDIS, Ramdas et al.) so
   the ledger supports continuous certification with anytime guarantees.
4. **Verifier artifact.** Hash-chained ledger format + independent checker:
   third parties recompute the correction from the transcript without
   trusting the agent ("Proof-of-Trial", milestone M4).

## 6. Honest assessment

Theorem 1 is an assembly of known parts whose value is the enforceable
protocol; Theorem 2 is an application of known transfer lemmas with a new
operational target. The candidate breakthrough is the *combination*:
grammar + ledger + metered feedback + online FDR + verifier = empirical
claims from adversarial agents that third parties can check. Kill
criteria stay live: if §5.1's sharpened accounting collapses to triviality
or the conformal version fails on real panels, say so.
