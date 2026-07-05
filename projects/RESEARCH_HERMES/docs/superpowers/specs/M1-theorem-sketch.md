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
(no_wall: 43.85 false certs at $m = 400$).

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

## 3. Theorem 3 (immortal wall): anytime online FDR control

Theorem 1 certifies a *batch* of $m$ trials. A live research agent never
stops; it keeps proposing indefinitely. We want an **anytime** guarantee:
at every audit time $t = 1, 2, \dots$, the set of rejections made up to $t$
controls $\mathrm{FDR} \le \alpha$.

**Setup.** Maintain the train-only feedback wall of Theorem 1, but now the
validator applies a multiple-testing correction to the *prefix* of the ledger
at each time $t$. The most direct valid choice is **sequential
Benjamini–Yekutieli**: at time $t$, run BY-FDR on $(p_1, \dots, p_t)$.

**Claim.** For every $t$ and every strategy of $G$:

1. The prefix $(a_1, \dots, a_t)$ is independent of $V$ (the wall prevents
   any $a_i$ from using validation-side information).
2. Therefore each $p_i$ in the prefix is marginally super-uniform under its
   null, regardless of dependence among the $p_i$.
3. Benjamini–Yekutieli on the prefix controls $\mathrm{FDR}(t) \le \alpha$.

Because the prefix at time $t$ is not selected based on the data (it is
just the first $t$ registered trials), this is a valid fixed-set application
of BY at each $t$. The guarantee holds **simultaneously at all $t$**: the
rejection set reported at any audit time is FDR-controlled.

**Operational meaning.** The ledger can publish a running certified set at
any moment — e.g. every day, after every LLM proposal — without waiting for a
batch endpoint. An immortal agent can trial forever; the FDR promise is
perpetual.

**Empirical footprint:** attack-suite arm `online_by` (sequential BY over
prefixes + train-only wall). At $m=400$ hill-climb trials it produces
**0.0 false certifications**, matching `protocol` and `conformal`. The arm
`online_lond` implements a LORD-style fixed-spending probe; it also stays
near zero in our null world but is not proved under the shared-$V$ dependence
of the attack model.

## 4. Theorem 2 (leaky wall): graceful degradation under bounded leakage

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

## 5. Mapping to the attack suite (e619731)

| Suite arm | Model | Predicted | Observed (m=400, hill-climb) |
|---|---|---|---|
| naive | unbounded leakage, no correction | FDR → 1 | 211.4 false certs, 100% |
| no_wall | unbounded leakage + BY | premise of Thm 1 broken; BY powerless | 43.85 false certs |
| protocol | $B = 0$ (Thm 1) | FDR ≤ α | 0.0 false certs |
| metered | bounded leakage $B > 0$ (Thm 2) | FDR ≤ α with corrected level | 2.5 false certs (uncorrected BY level; expected to drop to ≈0 with $\alpha/2^B$) |
| conformal | $B = 0$, three-way split + conformal p-value (§2.1) | FDR ≤ α, no parametric assumption | 0.0 false certs |
| online_by | $B = 0$, sequential BY over prefixes (§3) | anytime FDR ≤ α | 0.0 false certs |
| online_lond | LORD-style fixed-spending probe | empirical, not yet proved under shared-$V$ dependence | 0.45 false certs |
| no_wall + random attacker | valid p's (no adaptivity) | BY holds | 0.0 false certs |

The last row is the control that isolates *adaptivity* (not dependence,
not multiplicity) as the breaking force.

## 6. Proof-of-Trial verifier (M4): don't trust the agent

A theorem is not enough for a deployed primitive. The agent could lie about
which trials it ran or which ones it certified. The Proof-of-Trial
artifact makes the ledger independently auditable.

`aqra/src/aqra/verify/proof_of_trial.py` exports the DuckDB-backed
`TrialsLedger` to a hash-chained JSON-line file:

- Every trial record carries `previous_hash` and `this_hash`.
- `this_hash` is a SHA-256 digest of all other canonical fields (trial id,
  timestamp, DSL version, lane, status, p-value, formula, rationale,
  source, metrics).
- The metadata line at the end publishes the FDR level, the correction
  method (`benjamini_yekutieli` or `online_by`), and the claimed certified
  set.

`ProofOfTrialVerifier` independently:

1. Walks the chain and checks that each `this_hash` matches the recomputed
   hash and that each `previous_hash` links to the previous record.
2. Recomputes the FDR correction from the published p-values.
3. Compares the recomputed certified set to the claimed set and reports any
   discrepancy.

This turns the protocol's statistical guarantee into a publicly checkable
object: anyone with the ledger file can verify that the certified
strategies are exactly those selected by BY-FDR (or online-BY) over the
*full* ledger, without trusting the agent that produced the candidates.

## 7. Open problems (the research program)

1. **Tight budget accounting for structured feedback.** Our protocol leaks
   exactly: train stats (0 bits about $V$) + per-campaign certification
   decisions (≤ #certified bits). Sharpen $2^B$ for this structured channel;
   worst-case exponential pricing is likely far too pessimistic.
2. **LORD-style online FDR under shared-$V$ dependence.** `online_lond`
   works empirically in our null world but has no proof under the
   shared-validation dependence created by the cheating generator.
   SAFFRON/ADDIS-style adaptive weights and a martingale proof may close
   this, or the shared-$V$ structure may invalidate it — a crisp kill
   criterion.
3. **Cross-domain transfer.** Port the grammar/ledger/online-FDR stack to a
   non-finance adaptive-generation problem (e.g., ML hyperparameter search
   or benchmark gaming) so the primitive is tested outside its home domain
   (milestone M3).

## 8. Honest assessment

Theorem 1 is an assembly of known parts whose value is the enforceable
protocol; Theorem 2 is an application of known transfer lemmas with a new
operational target. The conformal, online, and verifier extensions
(§2.1, §3, §6) remove the operational caveats that would block real
deployment. The candidate breakthrough is the *combination*: grammar +
ledger + metered feedback + online FDR + verifier = empirical claims from
adversarial agents that third parties can check. Kill criteria stay live:
if §7.1's sharpened accounting collapses to triviality, or the cross-domain
demo shows the primitive does not transfer, say so.
