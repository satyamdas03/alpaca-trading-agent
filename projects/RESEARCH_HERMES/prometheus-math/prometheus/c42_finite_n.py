"""Exact finite-n oracle for the C_42 block construction.

For a k-band profile (same parameter layout as c42_kband), prescribe power sums
S_m = rho(m/n) on the first and middle blocks (m <= n - A_n - 1, A_n = floor(t1*n))
and leave the free block F_n = {n - A_n, ..., n} to be chosen adaptively with
|S_m| <= C so that the top coefficient b_n of

    E(z) = exp(- sum_{m=1}^{n} S_m z^m / m)

vanishes.  Because two free indices sum beyond n (for t1 < 1/2), the free values
enter e_n linearly:

    e_n = e~_n - sum_{m in F_n} (S_m / m) e~_{n-m},

with e~ the coefficients computed with the free block zeroed.  Feasibility of
|S_m| <= C is therefore exactly

    |e~_n| <= C * sum_{m in F_n} |e~_{n-m}| / m,

giving the minimal feasible constant at size n:

    C_n = max(|1 - alpha|, max_j |eta_j|, |e~_n| / sum_{m in F_n} |e~_{n-m}| / m).

This evaluation is exact at every order of the correction expansion -- no
quadratic or cubic truncation -- and serves as ground truth for any limiting
functional.  As n -> infinity it should converge to Griego's |Y|/D at his
two-block point (tau > 1/3), which is the validation gate.
"""
import numpy as np

from prometheus.c42_kband import _unpack_float


def profile_values(params, k, n):
    """Return prescribed S_1..S_n (complex) with the free block set to 0.

    Layout mirrors c42_kband: first block [1, A_n] gets 1-alpha; band j = 2..k
    covers (t_{j-1}, t_j] in u = m/n and gets eta_j; free block (t_k, 1] is 0
    here (absorbed adaptively).  t_k = 1 - t1 by construction.
    """
    t, alpha, eta = _unpack_float(np.asarray(params, dtype=float), k)
    u = np.arange(1, n + 1) / n
    S = np.zeros(n, dtype=complex)
    S[u <= t[0]] = 1.0 - alpha
    for j in range(1, k):
        S[(u > t[j - 1]) & (u <= t[j])] = eta[j - 1]
    # free block u > t[-1] stays 0
    return S, t, alpha, eta


def _exp_coeffs(S, n):
    """Coefficients e_0..e_n of exp(-sum_{m>=1} S_m z^m / m) via the standard
    log-derivative recurrence e_l = -(1/l) * sum_{m=1}^{l} S_m e_{l-m}."""
    e = np.zeros(n + 1, dtype=complex)
    e[0] = 1.0
    for l in range(1, n + 1):
        # dot(S_1..S_l, e_{l-1}..e_0)
        e[l] = -np.dot(S[:l], e[l - 1::-1]) / l
    return e


def finite_n_C(params, k, n):
    """Exact minimal feasible constant C_n for the block construction at size n.

    The generating function includes the 1/(1-z) factor (the forced unimodular
    point z=1 that satisfies max|z_i| = 1), so the working coefficients are the
    partial sums B_l = sum_{j<=l} e_j.  Forcing b_n = 0 with free-block values
    |S_m| <= C is feasible iff

        |B~_n| <= C * sum_{m in F_n} |B~_{n-m}| / m,

    with B~ computed from the free-block-zeroed profile.  Returns dict with
    C_n, the free-block ratio, the constraint values, and the free-block range.
    """
    S, t, alpha, eta = profile_values(params, k, n)
    e = _exp_coeffs(S, n)
    B = np.cumsum(e)  # coefficients of exp(-sum S_m z^m/m) / (1-z)

    A_n = int(np.floor(t[0] * n))
    free_lo = n - A_n  # F_n = {n - A_n, ..., n}
    m_free = np.arange(free_lo, n + 1)
    denom = np.sum(np.abs(B[n - m_free]) / m_free)
    ratio = np.abs(B[n]) / denom if denom > 0 else np.inf

    constraints = [abs(1.0 - alpha)] + [abs(x) for x in eta]
    C_n = max([ratio] + constraints)
    return {
        "C_n": float(C_n),
        "free_ratio": float(ratio),
        "constraint_max": float(max(constraints)),
        "free_lo": int(free_lo),
        "n": int(n),
    }


def finite_n_C_sequence(params, k, ns):
    """Evaluate C_n over a list of n values (for convergence checks)."""
    return [finite_n_C(params, k, n) for n in ns]


def richardson_extrapolate(ns, values):
    """Simple linear-in-1/n extrapolation from the last two points."""
    n1, n2 = ns[-2], ns[-1]
    v1, v2 = values[-2], values[-1]
    return v2 + (v2 - v1) * (1.0 / n2) / (1.0 / n1 - 1.0 / n2)
