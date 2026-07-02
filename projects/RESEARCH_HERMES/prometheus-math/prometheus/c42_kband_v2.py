"""Corrected k-band functional (v2): fixes the linear-term kernel.

The 2026-07-02 term-wise arbitration against the exact finite-n oracle
(prometheus/c42_finite_n.py) showed that the linear term of the limiting
functional uses the kernel (1-u)^{alpha-1}/u, NOT u^{alpha-1}/(1-u) as coded in
c42_kband.py.  The two agree for the symmetric k=2 band (tau, 1-tau) — which is
why Griego's point reproduced exactly — but differ for asymmetric bands (k>=3).

Corrected functional (valid for t1 > 1/3, where cubic corrections cannot reach
the z^n coefficient):

    Y = 1 + s*K - sum_j w_j A1_j^corr + (1/2) sum_{j,l} w_j w_l Q_jl
    A1_j^corr = int_{t_{j-1}}^{t_j} (1-u)^{alpha-1}/u du
              = I_A(1 - t_{j-1}) - I_A(1 - t_j)

with s = 1-alpha, w_j = eta_j - s, K = I_A(t1), D = I_A^{Re alpha}(t1), and the
same pair kernel Q_jl as before (confirmed correct by the arbitration).

Both float and interval paths are provided; the interval path reuses the
outward-rounded helpers from c42_kband.
"""
import numpy as np
import mpmath as mp

from prometheus.c42_kband import (
    _unpack_float,
    _unpack_interval,
    _I_A_float,
    _I_A_interval,
    _Q_jl_float,
    _Q_jl_interval,
    _abs_iv,
    _re_iv,
)

mp.mp.dps = 50


def kband_Y_float_v2(params, k, terms=1200, QN=400, Qp=4):
    """Corrected float evaluation of (Y, D)."""
    t, alpha, eta = _unpack_float(np.asarray(params, dtype=float), k)
    s = 1.0 - alpha
    w = eta - s

    t1 = t[0]
    K = _I_A_float(alpha, t1, terms)
    D = _I_A_float(alpha.real, t1, terms).real

    A1 = np.empty(k - 1, dtype=complex)
    for j in range(1, k):
        A1[j - 1] = (
            _I_A_float(alpha, 1.0 - t[j - 1], terms)
            - _I_A_float(alpha, 1.0 - t[j], terms)
        )

    Q = np.zeros((k - 1, k - 1), dtype=complex)
    for j in range(1, k):
        for l in range(1, k):
            Q[j - 1, l - 1] = _Q_jl_float(
                t[j - 1], t[j], t[l - 1], t[l], alpha, N=QN, p=Qp
            )

    Y = 1.0 - np.sum(w * A1) + 0.5 * np.sum(w[:, None] * w[None, :] * Q) + s * K
    return Y, D


def kband_bound_float_v2(params, k, terms=1200, QN=400, Qp=4):
    """Return (C, Y, D) for the corrected k-band functional (float path)."""
    Y, D = kband_Y_float_v2(params, k, terms=terms, QN=QN, Qp=Qp)
    return abs(Y) / D, Y, D


def kband_Y_interval_v2(params_box, k, terms=4000, QN=80, Qp=4):
    """Corrected interval evaluation of (Y, D) over a parameter box."""
    t_iv, alpha_iv, eta_iv = _unpack_interval(params_box, k)
    ctx = mp.iv
    one = ctx.mpf(1)
    s_iv = ctx.mpc(1, 0) - alpha_iv
    w_iv = [e - s_iv for e in eta_iv]

    t1_iv = t_iv[0]
    K_iv = _I_A_interval(alpha_iv, t1_iv, terms)
    D_iv = _I_A_interval(_re_iv(alpha_iv), t1_iv, terms)

    A1_iv = []
    for j in range(1, k):
        A1_iv.append(
            _I_A_interval(alpha_iv, one - t_iv[j - 1], terms)
            - _I_A_interval(alpha_iv, one - t_iv[j], terms)
        )

    Q_iv = [[None] * (k - 1) for _ in range(k - 1)]
    for j in range(1, k):
        for l in range(1, k):
            Q_iv[j - 1][l - 1] = _Q_jl_interval(
                t_iv[j - 1], t_iv[j], t_iv[l - 1], t_iv[l], alpha_iv, N=QN, p=Qp
            )

    Y_iv = ctx.mpc(1, 0)
    for j in range(k - 1):
        Y_iv -= w_iv[j] * A1_iv[j]
    quad = ctx.mpc(0, 0)
    for j in range(k - 1):
        for l in range(k - 1):
            quad += w_iv[j] * w_iv[l] * Q_iv[j][l]
    Y_iv += ctx.mpf(0.5) * quad
    Y_iv += s_iv * K_iv
    return Y_iv, D_iv


def certify_kband_bound_v2(params, k, half_width=1e-12, terms=4000, QN=80, Qp=4):
    """Interval certificate for the corrected functional over a box.

    Same contract as c42_kband.certify_kband_bound.  Additionally reports the
    validity condition t1 > 1/3 (required for the quadratic truncation to be
    the true limit).
    """
    p = np.asarray(params, dtype=float)
    ctx = mp.iv
    box = [ctx.mpf([v - half_width, v + half_width]) for v in p]

    t_iv, alpha_iv, eta_iv = _unpack_interval(box, k)
    Y_iv, D_iv = kband_Y_interval_v2(box, k, terms=terms, QN=QN, Qp=Qp)
    C_iv = _abs_iv(Y_iv) / D_iv

    one_minus_alpha = ctx.mpc(1, 0) - alpha_iv
    R = _abs_iv(one_minus_alpha).b
    for e in eta_iv:
        R = max(R, _abs_iv(e).b)

    margin = C_iv.a - R
    third = mp.mpf(1) / 3
    t1_ok = t_iv[0].a > third
    verdict = "CERTIFIED" if (margin > 0 and t1_ok) else "INCONCLUSIVE"

    return {
        "verdict": verdict,
        "C_iv": C_iv,
        "interval_C_lower": C_iv.a,
        "interval_C_upper": C_iv.b,
        "Y_iv": Y_iv,
        "D_iv": D_iv,
        "margin": margin,
        "t1_above_one_third": bool(t1_ok),
        "params": p,
        "box": box,
        "constraints_ok": margin > 0,
    }
