"""Full rigorous certificate: float check + interval check + quadrature remainder."""
import numpy as np
import mpmath as mp
from mpmath import iv

from prometheus.c42_kband import (
    kband_bound_float,
    certify_kband_bound,
    _unpack_interval,
    _abs_iv,
)
from prometheus.c42_theorem import density_from_kband_params
from prometheus.c42_quadrature_remainder import (
    remainder_bound_Qjl_rigorous,
    remainder_bound_K,
    remainder_bound_D,
)


mp.mp.dps = 50


def _enlarge_Y_for_per_pair_remainder(Y_iv, D_iv, err_matrix, alpha_iv, eta_iv):
    """Propagate per-pair 2D quadrature remainders through Y.

    Q contributes to Y as 0.5 * sum_{j,l} w_j w_l Q_{jl} with
    w_j = eta_j - (1-alpha).  If each Q_{jl} is known up to an error
    e_{jl}, the total additive uncertainty in Y is bounded by

        E_Y <= 0.5 * sum_{j,l} |w_j| |w_l| e_{jl}.

    The remainders are intervals, so the sum is evaluated in interval
    arithmetic.  Returns the enlarged Y_iv and the original D_iv (the
    Q-remainder does not affect D).
    """
    ctx = mp.iv
    s_iv = ctx.mpc(1, 0) - alpha_iv
    # err_matrix rows/cols are indexed by density.bands, which contains ONLY the
    # k-1 middle bands (eta_2 .. eta_k).  The weight vector must align with that
    # indexing: w_abs[j] = |eta_{j+2} - (1-alpha)|.  (A previous version
    # prepended a zero for the first block, shifting every weight by one and
    # silently zeroing most of the propagated remainder.)
    w_abs = [_abs_iv(e - s_iv) for e in eta_iv]
    if len(w_abs) != len(err_matrix):
        raise ValueError(
            f"weight/err_matrix mismatch: {len(w_abs)} weights vs {len(err_matrix)} bands"
        )
    E_Y = ctx.mpf('0')
    for j in range(len(err_matrix)):
        for l in range(len(err_matrix)):
            E_Y += ctx.mpf('0.5') * w_abs[j] * w_abs[l] * err_matrix[j][l]
    radius = E_Y  # interval non-negative
    Y_enlarged = ctx.mpc(
        Y_iv.real + ctx.mpf([-radius.b, radius.b]),
        Y_iv.imag + ctx.mpf([-radius.b, radius.b]),
    )
    return Y_enlarged, D_iv


def certify_with_remainder(params: np.ndarray,
                           k: int,
                           half_width: float = 1e-12,
                           QN: int = 200,
                           terms: int = 4000,
                           Qp: float = 4.0,
                           grid: int = 64) -> dict:
    """Produce a rigorous upper bound for C_42 from a k-band parameter box.

    Combines:
      1. fast float sanity check,
      2. interval arithmetic certificate over the parameter box,
      3. validated quadrature remainder bound for the 2D integrals,
      4. validated 1D series tail for K and D.

    Returns
    -------
    dict with keys:
      float_C           : float evaluation at the box center
      interval_C        : upper bound on the quadrature-approximated part (float)
      interval_C_lower  : lower bound on the quadrature-approximated part (float)
      interval_C_upper  : upper bound on the quadrature-approximated part (float)
      q_remainder       : upper bound on the 2D quadrature remainder (float)
      k_tail            : upper bound on the 1D series tail in Y (float)
      d_tail            : upper bound on the 1D series tail in D (float)
      total_upper_bound : rigorous upper bound on C_42 (float)
      constraints_ok    : bool, whether |1-alpha| and |eta_j| are below C
      verdict           : 'CERTIFIED' or 'FAILED'
    """
    params = np.asarray(params, dtype=float)

    # 1. Float sanity check (used internally, not exposed)
    C_float = kband_bound_float(params, k=k, terms=terms, QN=QN, Qp=Qp)[0]
    if not np.isfinite(C_float):
        return {
            "float_C": np.inf,
            "interval_C": np.inf,
            "interval_C_lower": np.inf,
            "interval_C_upper": np.inf,
            "q_remainder": np.inf,
            "k_tail": np.inf,
            "d_tail": np.inf,
            "total_upper_bound": np.inf,
            "constraints_ok": False,
            "verdict": "FAILED",
        }

    # 2. Interval certificate (quadrature-approximated functional)
    interval_result = certify_kband_bound(params, k=k, half_width=half_width,
                                          terms=terms, QN=QN, Qp=Qp)
    Y_iv = interval_result["Y_iv"]
    D_iv = interval_result["D_iv"]
    interval_C_lower = float(interval_result["interval_C_lower"])
    interval_C_upper = float(interval_result["interval_C_upper"])
    constraints_ok = interval_result["constraints_ok"]

    # 3. 2D quadrature remainder, rigorously propagated through Y
    density = density_from_kband_params(params, k=k)
    err_matrix = []
    q_total = iv.mpf('0')
    for a_u, b_u, _ in density.bands:
        row = []
        for a_v, b_v, _ in density.bands:
            e = remainder_bound_Qjl_rigorous(
                a_u, b_u, a_v, b_v, density.alpha, QN, Qp, grid=grid
            )
            row.append(e)
            q_total += e
        err_matrix.append(row)

    t_iv, alpha_iv, eta_iv = _unpack_interval(interval_result["box"], k)
    Y_iv_enlarged, D_iv_enlarged = _enlarge_Y_for_per_pair_remainder(
        Y_iv, D_iv, err_matrix, alpha_iv, eta_iv
    )

    # 4. 1D series tails for K (in Y) and D (in denominator)
    t1 = float(params[0])
    k_tail_iv = remainder_bound_K(t1, density.alpha, terms)
    d_tail_iv = remainder_bound_D(t1, density.alpha, terms)
    # Y contains s*K where K is a partial sum of the 1D singular series.
    # The tail is multiplied by s = 1-alpha and added to Y; the D tail is
    # added to the denominator.  Both are astronomically small for terms>=500.
    s_iv = mp.iv.mpc(1, 0) - alpha_iv
    Y_iv_true = Y_iv_enlarged + s_iv * k_tail_iv
    D_iv_true = D_iv_enlarged + d_tail_iv
    C_iv_true = _abs_iv(Y_iv_true) / D_iv_true

    total_upper_bound = float(C_iv_true.b)
    interval_C = interval_C_upper

    # Griego's value 0.690653695151631 is the previous best known upper bound.
    verdict = "CERTIFIED" if (constraints_ok and total_upper_bound < 0.690653695151631) else "FAILED"

    return {
        "float_C": float(C_float),
        "interval_C": interval_C,
        "interval_C_lower": interval_C_lower,
        "interval_C_upper": interval_C_upper,
        "q_remainder": float(q_total.b),
        "k_tail": float(k_tail_iv.b),
        "d_tail": float(d_tail_iv.b),
        "total_upper_bound": total_upper_bound,
        "constraints_ok": constraints_ok,
        "verdict": verdict,
    }


def certify_with_remainder_v2(params: np.ndarray,
                              k: int,
                              half_width: float = 1e-12,
                              QN: int = 850,
                              terms: int = 1000,
                              Qp: float = 4.0,
                              grid: int = 64) -> dict:
    """Full-rigor certificate for the CORRECTED (v2) k-band functional.

    Same structure as certify_with_remainder, but:
      * uses the corrected linear kernel (1-u)^{alpha-1}/u via c42_kband_v2,
      * enforces the validity condition t1 > 1/3 (quadratic truncation exact),
      * propagates the per-pair 2D quadrature remainder with correctly aligned
        band weights.
    """
    from prometheus.c42_kband_v2 import (kband_bound_float_v2,
                                         certify_kband_bound_v2)

    params = np.asarray(params, dtype=float)
    C_float = kband_bound_float_v2(params, k=k, terms=terms, QN=QN, Qp=Qp)[0]

    interval_result = certify_kband_bound_v2(params, k=k, half_width=half_width,
                                             terms=terms, QN=QN, Qp=Qp)
    Y_iv = interval_result["Y_iv"]
    D_iv = interval_result["D_iv"]

    density = density_from_kband_params(params, k=k)
    err_matrix = []
    q_total = iv.mpf('0')
    for a_u, b_u, _ in density.bands:
        row = []
        for a_v, b_v, _ in density.bands:
            e = remainder_bound_Qjl_rigorous(
                a_u, b_u, a_v, b_v, density.alpha, QN, Qp, grid=grid
            )
            row.append(e)
            q_total += e
        err_matrix.append(row)

    t_iv, alpha_iv, eta_iv = _unpack_interval(interval_result["box"], k)
    Y_enl, D_enl = _enlarge_Y_for_per_pair_remainder(
        Y_iv, D_iv, err_matrix, alpha_iv, eta_iv
    )

    t1 = float(params[0])
    k_tail_iv = remainder_bound_K(t1, density.alpha, terms)
    d_tail_iv = remainder_bound_D(t1, density.alpha, terms)
    s_iv = mp.iv.mpc(1, 0) - alpha_iv
    Y_true = Y_enl + s_iv * k_tail_iv
    D_true = D_enl + d_tail_iv
    C_true = _abs_iv(Y_true) / D_true

    total_upper = float(C_true.b)
    griego = 0.690653695151631
    verdict = "CERTIFIED" if (interval_result["constraints_ok"]
                              and interval_result["t1_above_one_third"]
                              and total_upper < griego) else "FAILED"
    return {
        "float_C": float(C_float),
        "interval_C_lower": float(interval_result["interval_C_lower"]),
        "interval_C_upper": float(interval_result["interval_C_upper"]),
        "q_remainder": float(q_total.b),
        "k_tail": float(k_tail_iv.b),
        "d_tail": float(d_tail_iv.b),
        "total_upper_bound": total_upper,
        "constraint_margin": float(interval_result["margin"].a),
        "t1_above_one_third": interval_result["t1_above_one_third"],
        "constraints_ok": interval_result["constraints_ok"],
        "verdict": verdict,
    }
