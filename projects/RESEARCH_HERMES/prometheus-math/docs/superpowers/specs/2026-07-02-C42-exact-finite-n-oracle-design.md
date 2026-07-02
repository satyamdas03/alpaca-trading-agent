# Design: Exact finite-n oracle + cubic-corrected functional for C_42

**Date:** 2026-07-02
**Status:** Approved (user authorized autonomous drive via /loop)
**Goal:** One breakthrough: a certified upper bound for C_42 strictly below Griego's 0.690653695151631, via the only legally unexplored region tau < 1/3.

## Background (from 2026-07-02 diagnosis)

Griego's construction (github.com/sebastian-griego/turan-c42-certificate) prescribes power sums
S_k = 1-alpha on the first block k <= tau*n, S_k = eta_j on middle bands, and chooses the free
block S_m (m in F_n = {n-A_n..n}, A_n = floor(tau*n)) adaptively with |S_m| <= C to force
b_n = 0. Solvability <=> |Y_n| <= C * sum_{m in F_n} |P_m|. His quadratic functional
Y = 1 - sum w_j A1_j + 1/2 sum w_j w_l Q_jl + sK is valid ONLY for tau > 1/3 (no triple
correction product reaches z^n). Our earlier 0.3993 "record" violated this (t1 = 0.04) and is
dead. Legal k-band search (t1 > 1/3) gives 0.6912 — worse than Griego. Remaining freedom:
tau in (1/4, 1/3] where exactly one extra (cubic) term enters.

## Core insight: the exact finite-n oracle

Let E(z) = exp(-sum_{k=1}^{n} S_k z^k / k) = sum e_l z^l. Split S into prescribed part
(blocks, k <= n - A_n - 1) and free part (m in F_n). Because two free indices satisfy
m1 + m2 >= 2n(1-tau) > n for tau < 1/2, the free values enter e_n LINEARLY:

    e_n = e~_n - sum_{m in F_n} (S_m / m) * e~_{n-m},

where e~ are the coefficients with the free block zeroed. Forcing e_n = 0 with |S_m| <= C is
feasible iff |e~_n| <= C * sum_{m in F_n} |e~_{n-m}| / m. Hence the minimal feasible constant
at size n is

    C_n = max( |1-alpha|, max_j |eta_j|, |e~_n| / sum_{m in F_n} |e~_{n-m}| / m ).

This is EXACT at every order in w — no quadratic/cubic truncation. O(n^2) evaluation
(sequential dot-product recurrence), n = 20000 tractable.

## Pipeline

1. **Oracle module** `prometheus/c42_finite_n.py`: `finite_n_C(params, k, n)` implementing the
   recurrence + absorption formula.
   **Validation gate (hard):** at Griego's k=2 point, C_n must converge to
   0.690653695151631 as n -> infinity (check n = 500..16000, Richardson extrapolate).
   If it does not, the absorption identity or block mapping is wrong — fix before ANY search.
   Secondary gate: at the legal k=3 point (t1 = 0.335, C = 0.691245) oracle must agree with the
   quadratic functional (tau > 1/3 => quadratic is exact in the limit).
2. **Scout:** optimize (tau, alpha, eta_j) against C_n at fixed n (2000-4000), tau in
   (0.25, 0.34], k = 2 and 3 bands. Extrapolate best candidates at n up to 16000+.
   Go/no-go: does anything dip below 0.690653695 with margin > extrapolation error?
3. **Cubic derivation (only if scout is GO):** derive the w^3 term
   (1/6) sum w_j w_l w_m T_jlm with kernel (1-u-v-w)^{alpha-1}/(uvw) on u+v+w <= 1
   restricted to band triples, valid for 4*tau > 1; cross-validate against oracle
   (|F_cubic - C_n| -> 0). Then interval-certify with existing machinery
   (c42_kband interval path + quadrature remainder, extended to the 3D term).
4. **Paper:** correct the 0.3993 claim; new theorem = cubic-extended certificate with explicit
   validity hypotheses tau in (1/4, 1/3], plus the (possible) new record.

## Failure handling

- Oracle fails Griego gate -> debug identity (most likely: 1/(1-z) bookkeeping or free-block
  index range). Nothing else proceeds.
- Scout shows constraint re-binding (optimizer pushes all |eta_j| -> C, C_n >= Griego) ->
  region dead; report honestly; project pivots to methods paper. No heroics.
- Cubic functional disagrees with oracle -> derivation bug; oracle is ground truth.

## Testing

- `tests/test_c42_finite_n.py`: Griego convergence gate, legal-k3 agreement gate,
  monotonicity of C_n in n (rough), linearity-of-free-block property check
  (direct e_n with random free S vs linear formula).

## Non-goals

- No k >= 4 sweeps, no cross-field analogies, no lower-bound work until go/no-go resolved.
- No claims without the oracle gate + interval certificate + validity conditions verified.
