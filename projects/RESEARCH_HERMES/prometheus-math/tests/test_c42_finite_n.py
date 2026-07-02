import numpy as np

from prometheus.c42_finite_n import finite_n_C, profile_values, _exp_coeffs
from prometheus.c42_kband import kband_bound_float

GRIEGO = np.array([0.36988243, 0.61927309, 0.57623741, 0.59839764, -0.34485185])
GRIEGO_C = 0.690653695151631


def test_free_block_linearity():
    """e_n depends linearly on the free-block values (no free-free interaction)."""
    n = 300
    S, t, alpha, eta = profile_values(GRIEGO, 2, n)
    rng = np.random.default_rng(0)
    A_n = int(np.floor(t[0] * n))
    free_lo = n - A_n
    S_free = S.copy()
    vals = rng.normal(size=(n + 1 - free_lo, 2))
    S_free[free_lo - 1:] = vals[:, 0] + 1j * vals[:, 1]
    e_tilde = _exp_coeffs(S, n)
    e_direct = _exp_coeffs(S_free, n)
    m_free = np.arange(free_lo, n + 1)
    e_n_linear = e_tilde[n] - np.sum(S_free[m_free - 1] / m_free * e_tilde[n - m_free])
    assert abs(e_direct[n] - e_n_linear) < 1e-12


def test_griego_convergence_power_law():
    """C_n errors at Griego's point shrink with a stable per-doubling ratio and
    extrapolate to Griego's constant."""
    ns = [500, 1000, 2000, 4000]
    cs = [finite_n_C(GRIEGO, 2, n)["C_n"] for n in ns]
    errs = [c - GRIEGO_C for c in cs]
    assert all(e > 0 for e in errs)
    ratios = [errs[i + 1] / errs[i] for i in range(len(errs) - 1)]
    assert max(ratios) - min(ratios) < 0.02  # clean power law
    q = ratios[-1]
    c_inf = cs[-1] - (cs[-2] - cs[-1]) * q / (1 - q)
    assert abs(c_inf - GRIEGO_C) < 5e-4


def test_oracle_matches_quadratic_at_nonbinding_point():
    """At a tau > 1/3 point where |Y|/D binds, the oracle ratio must trend to the
    quadratic functional value."""
    P = GRIEGO.copy()
    P[3] *= 0.9
    P[4] *= 0.9
    Cq, _, _ = kband_bound_float(P, 2, terms=2000, QN=400, Qp=4)
    r2000 = finite_n_C(P, 2, 2000)["free_ratio"]
    r4000 = finite_n_C(P, 2, 4000)["free_ratio"]
    # decreasing toward Cq, and already within 1e-2 at n=4000
    assert r4000 < r2000
    assert r4000 - Cq > 0
    assert r4000 - Cq < 1e-2
