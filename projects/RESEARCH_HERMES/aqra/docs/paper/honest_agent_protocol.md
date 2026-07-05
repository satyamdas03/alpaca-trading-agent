# Honest Agent Protocol: Statistical Guarantees Against Adaptive LLM Hypothesis Generators

**Authors:** Satyam Das  
**Date:** 2026-07-05  
**Target:** NeurIPS / ICML / similar general ML venue (8 pages)  
**Code:** `aqra/scripts/attack_suite.py`, `aqra/scripts/ml_benchmark_demo.py`, `aqra/src/aqra/verify/proof_of_trial.py`

---

## Abstract

Large language model agents can generate, evaluate, and iteratively refine
empirical hypotheses at machine speed. Their outputs are increasingly used as
research claims, yet the generation loop invalidates the classical statistical
assumption that hypotheses are pre-specified: an adaptive agent can hill-climb on
the same held-out data it is being tested against. We introduce the **Honest
Agent Protocol**, a lightweight statistical discipline that lets an arbitrary,
memoryful, possibly adversarial generator propose hypotheses while guaranteeing
that only a bounded false-discovery rate is certified. The protocol combines
three ingredients: a constrained proposal grammar, a pre-registration trials
ledger, and a train-only feedback wall. We prove (i) exact FDR control under
the wall with arbitrary dependence among proposals; (ii) a distribution-free
conformal variant that removes parametric assumptions; (iii) graceful
degradation when bounded feedback leaks through the wall; and (iv) an anytime
online-FDR extension for agents that never stop trialing. We also provide a
**Proof-of-Trial** verifier: a hash-chained ledger format whose FDR selections
can be independently recomputed by third parties. Empirically, a synthetic
finance attack suite shows the wall separates adaptive overfitting (211 false
certifications) from honest certification (0), and a cross-domain ML demo
reproduces the same separation on a no-signal classification benchmark. The
primitive is domain-agnostic: any adaptive generator whose proposals can be
ledgered and scored on a held-out set can be made honest.

---

## 1. Introduction

LLM agents are becoming autonomous empirical researchers. They propose
hypotheses, write code, run experiments, inspect results, and iterate. This
speed is powerful, but it also revives the oldest statistical worry at a new
scale: **the hypothesis was suggested by the data**. When a human researcher
tests a hundred trading rules and reports the best one, multiplicity must be
charged. When an LLM does the same thing in a loop, the problem is identical in
form but far faster and harder to audit.

The adaptive-data-analysis literature has shown that standard holdout estimates
can fail under repeated adaptive queries (Dwork et al., 2015; Russo & Zou,
2016). The core mechanism is simple: the analyst uses feedback from the holdout
to steer the next query, so the holdout p-values lose their marginal validity.
What is missing for real agents is an **operational protocol** that makes the
premises of the known theorems enforceable against a generative model with its
own memory and optimizer.

We propose such a protocol. Its ingredients are:

1. **Constrained proposal grammar.** Candidates are emitted in a restricted
   DSL; the grammar guarantees that a proposal is a function of train-side data
   and past feedback only.
2. **Trials ledger.** Every proposal is registered *before* evaluation, with a
   unique id and a public hash chain. Failed and malformed proposals stay on
   the books. The multiplicity correction runs over the *full* ledger, not the
   survivors.
3. **Train-only feedback wall.** The generator receives only train-window
   statistics; validation-window numbers never enter its context. This makes
   every proposal independent of the validation sample, restoring marginal
   p-value validity regardless of the dependence among proposals.
4. **Anytime FDR correction.** Batch BY-FDR is replaced by sequential BY over
   ledger prefixes, so a live agent can publish a running certified set without
   waiting for a batch endpoint.
5. **Proof-of-Trial verifier.** The ledger can be exported to a hash-chained
   format; an independent tool recomputes the correction and checks the chain,
   so third parties need not trust the agent.

Our contribution is not a new multiple-testing procedure. Benjamini and
Yekutieli (2001), conformal prediction (Vovk et al., 2005; Angelopoulos & Bates,
2021), and adaptive-data-analysis transfer bounds (Dwork et al., 2015) are the
technical engines. Our contribution is the **protocol architecture** that makes
their premises hold against an adaptive LLM: the grammar fixes the function
class, the ledger fixes the trial set, the wall fixes the feedback
measurability, the online correction supports immortal agents, and the
verifier makes the guarantee auditable.

We validate the protocol with two experiments. First, a synthetic finance
attack suite in which a cheating generator hill-climbs on validation returns.
At 400 trials, a naive uncorrected loop certifies 211 false strategies,
a loop with BY-FDR but no wall still certifies 43.85, and the full protocol
certifies 0. Second, a cross-domain ML demo on a synthetic no-signal binary
classification task: without the wall the generator certifies 0.50 spurious
classifiers, with the wall 0. Both results are independently verifiable from
hash-chained ledgers.

---

## 2. Related Work

**Adaptive data analysis.** Dwork et al. (2015) introduced reusable holdout and
max-information bounds for adaptive queries; Russo & Zou (2016) gave
mutual-information bias bounds. These works bound the damage of adaptivity but
do not provide a ready protocol for LLM agents. We instantiate their tools in
an agentic loop with an auditable ledger.

**Multiple testing.** Benjamini & Yekutieli (2001) control FDR under arbitrary
dependence, which is essential because the proposals share the same validation
sample. Online FDR methods (LORD, SAFFRON, ADDIS; Javanmard & Montanari 2018;
Ramdas et al. 2017, 2018) handle sequential hypotheses but assume independence
or specific dependence structures. Our online_BY arm uses BY over fixed
prefixes, which is valid under arbitrary dependence at every audit time but
may be conservative.

**Conformal prediction.** Split-conformal p-values (Papadopoulos et al., 2002;
Vovk et al., 2005) give distribution-free finite-sample validity under
exchangeability. We use them to remove the parametric t-test caveat from the
base theorem.

**LLM research agents.** Systems such as FactorMAD, QuantaAlpha, AlphaCrafter,
and QRAFTI generate trading signals or research hypotheses but do not
maintain a pre-registration ledger or enforce a train-only feedback wall.
AQRA (Das, 2026) is the finance instantiation that motivates this work; the
Honest Agent Protocol abstracts the ledger discipline out of that domain.

---

## 3. The Honest Agent Protocol

### 3.1 Setup and threat model

A protocol run proceeds in rounds $i = 1, 2, \dots$:

- A training sample $T$ and a held-out validation sample $V$ are fixed before
  the run and satisfy $T \perp V$.
- A generator $G$ is an arbitrary randomized algorithm **with memory**. In each
  round it emits a candidate $a_i$ in a constrained grammar. $G$ is adversarial:
  it may be designed solely to force false certifications.
- A validator evaluates $a_i$ on $V$ and produces a p-value $p_i$ under the null
  that $a_i$ has no edge.
- A ledger records every registered candidate before evaluation. Failed or
  invalid trials receive $p_i = 1$.
- A feedback channel $F_i$ is revealed to $G$ after round $i$.

The protocol's only restriction on $G$ is informational: $F_i$ must be
measurable with respect to $\sigma(T, a_1, \dots, a_i, \text{G's coins})$. It
must not contain $V$-side information.

### 3.2 Theorem 1 (train-only wall): exact FDR control

**Claim.** If every $F_i$ is train-measurable, then for every strategy of $G$
and every number of rounds $m$:

1. Each $a_i$ is independent of $V$ (induction on $i$: $a_i$ is a function of
   train-measurable feedback and $G$'s coins, all $V$-independent).
2. Hence each $p_i$ is marginally super-uniform under its null, regardless of
   the dependence among the $p_i$ (they share $V$).
3. Benjamini–Yekutieli at level $\alpha$ over the full ledger controls
   $\mathrm{FDR} \le \alpha$.

The theorem is simple once the wall is enforced; the engineering is the wall.

### 3.3 Conformal Theorem 1 (distribution-free wall)

Replace the parametric t-test with a three-way split: $T_{\text{train}}$ visible
to $G$, $T_{\text{calib}}$ visible only to the validator, and $V$ visible only
to the validator. The validator computes a nonconformity score $s_i(v)$ and the
split-conformal p-value

$$p_i = \frac{1 + \#\{u \in T_{\text{calib}} : s_i(u) \ge s_i(v)\}}{|T_{\text{calib}}| + 1}.$$

Under the same train-only wall, each $p_i$ is super-uniform under the null,
so BY-FDR over the full ledger controls FDR $\le \alpha$ with no parametric
assumption on returns or accuracy.

### 3.4 Theorem 2 (leaky wall): graceful degradation

Real systems leak: even publishing accept/reject decisions is feedback about
$V$. Let the transcript $\Phi$ visible to $G$ satisfy a max-information bound
$I_\infty^\beta(V; \Phi) \le B$ (Dwork et al., 2015). Then for any event $E$
defined on $(V, \Phi)$,
$\Pr(E) \le 2^B \Pr_{V' \perp \Phi}(E) + \beta$.
Applying to $E = \{p_i \le u\}$ gives effective super-uniformity
$\Pr(p_i \le u) \le 2^B u + \beta$. Running BY at level
$\alpha / 2^B$ (with $m\beta$ additive slack) restores
$\mathrm{FDR} \lesssim \alpha + m\beta$.

The operational reading is that the protocol can **meter the channel** and
price the correction accordingly.

### 3.5 Theorem 3 (immortal wall): anytime online FDR

Theorem 1 certifies a batch. A live agent never stops. Run **sequential
Benjamini–Yekutieli over prefixes**: at time $t$, apply BY to the first $t$
ledger entries. Because each prefix is a fixed (non-data-dependent) subset and
BY controls FDR under arbitrary dependence, the rejection set at every audit
time $t$ satisfies $\mathrm{FDR}(t) \le \alpha$. The agent can trial forever;
the FDR promise is perpetual.

### 3.6 Proof-of-Trial verifier

A theorem is not enough if the agent can lie about the ledger. The verifier
exports the DuckDB ledger to a hash-chained JSON-line file. Each record carries
`previous_hash` and `this_hash`; `this_hash` is a SHA-256 digest of all other
canonical fields. The metadata line publishes the FDR level, the correction
method, and the claimed certified set. An independent verifier recomputes the
hashes, walks the chain, and recomputes BY/online-BY. Any tampering or
overclaiming is detected.

---

## 4. Empirical Validation

### 4.1 M2: Finance attack suite

Ground truth: all candidates are null (random weight vectors over 50 assets,
returns are iid noise). Any certification is a false discovery.

| Defense | Model | Mean false certs at $m=400$ |
|---|---|---|
| naive | uncorrected, full leak | 211.4 |
| no_wall | BY-FDR, full leak | 43.85 |
| metered | BY-FDR, one-bit leak | 2.5 |
| protocol | BY-FDR, train-only wall | 0.0 |
| conformal | conformal p-value, train-only wall | 0.0 |
| online_by | sequential BY prefixes, train-only wall | 0.0 |
| online_lond | LORD probe, train-only wall | 0.45 |
| no_wall + random | BY-FDR, no adaptivity | 0.0 |

The `no_wall + random` control isolates **adaptivity** as the breaking force,
not dependence or multiplicity.

### 4.2 M3: Cross-domain ML demo

Synthetic 50-feature binary classification, labels independent of features.
Candidates are random linear classifiers; the generator hill-climbs on either
train accuracy (wall) or validation p-value (no wall).

| Protocol | Mean false certs at $m=400$ |
|---|---|
| no wall, batch BY-FDR | 0.50 |
| wall, batch BY-FDR | 0.00 |
| wall, online BY | 0.00 |

Exported ledgers verify independently. The separation transfers outside
finance.

---

## 5. Discussion and Limitations

**Tightness of leakage accounting.** Theorem 2 uses worst-case max-information
$2^B$ pricing. For the structured channel (train stats + accept/reject bits)
the exponential bound is likely pessimistic; tightening it is open work.

**Online power.** `online_by` is rigorous but may be conservative; `online_lond`
has better empirical power but no proof under shared-$V$ dependence. A SAFFRON
or ADDIS proof under the ledger structure is an open direction.

**Verifier trust assumptions.** The verifier checks the ledger math but does
not verify that the validation data itself was collected correctly. It moves
trust from the agent to the data pipeline.

**Generality.** The protocol requires three things: a grammar that constrains
proposals, a train/validation split, and a score whose null distribution is
known or exchangeable. Many empirical domains satisfy this.

---

## 6. Conclusion

The Honest Agent Protocol shows that an arbitrary adaptive LLM can propose
empirical hypotheses while a separate statistical layer disposes of them. The
ledger discipline, the train-only wall, the conformal/online extensions, and
the Proof-of-Trial verifier turn a soft hope — "the LLM won't overfit" — into
a checkable guarantee. The experiments show the wall is load-bearing and
transfers across domains. We release the code and ledgers for reproduction and
invite other domains to adopt the primitive.

---

## References

- Angelopoulos, A. N., & Bates, S. (2021). A gentle introduction to conformal prediction and distribution-free uncertainty quantification. *arXiv:2107.07511*.
- Benjamini, Y., & Yekutieli, D. (2001). The control of the false discovery rate in multiple testing under dependency. *Annals of Statistics*, 29(4), 1165–1188.
- Das, S. (2026). AQRA: Autonomous Quant Research Agent. *GitHub repository*.
- Dwork, C., Feldman, V., Hardt, M., Pitassi, T., Reingold, O., & Roth, A. (2015). The reusable holdout: Preserving validity in adaptive data analysis. *Science*, 349(6248), 636–638.
- Javanmard, A., & Montanari, A. (2018). Online rules for control of false discovery rate and false discovery exceedance. *Annals of Statistics*, 46(2), 526–554.
- Papadopoulos, H., Proedrou, K., Vovk, V., & Gammerman, A. (2002). Inductive confidence machines for regression. *ECML*.
- Ramdas, A., Yang, F., Wainwright, M. J., & Jordan, M. I. (2017). Online control of the false discovery rate with decaying memory. *NeurIPS*.
- Ramdas, A., Zrnic, T., Wainwright, M. J., & Jordan, M. I. (2018). SAFFRON: An adaptive algorithm for online control of the false discovery rate. *ICML*.
- Russo, D., & Zou, J. (2016). Controlling bias in adaptive data analysis using information theory. *AISTATS*.
- Vovk, V., Gammerman, A., & Shafer, G. (2005). *Algorithmic learning in a random world*. Springer.
