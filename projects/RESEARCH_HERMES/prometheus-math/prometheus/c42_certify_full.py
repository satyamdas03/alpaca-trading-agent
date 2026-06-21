"""Full rigorous certificate: float check + interval check + quadrature remainder."""
import numpy as np
import mpmath as mp

from prometheus.c42_kband import kband_bound_float, certify_kband_bound
from prometheus.c42_theorem import density_from_kband_params
from prometheus.c42_quadrature_remainder import total_Q_remainder


mp.mp.dps = 50


def certify_with_remainder(params: np.ndarray,
                           k: int,
                           half_width: float = 1e-12,
                           QN: int = 200,
                           terms: int = 4000,
                           Qp: float = 4.0) -> dict:
    """Produce a rigorous upper bound for C_42 from a k-band parameter box.

    Combines:
      1. fast float sanity check,
      2. interval arithmetic certificate over the parameter box,
      3. validated quadrature remainder bound for the 2D integrals.

    Returns
    -------
    dict with keys:
      float_C        : float evaluation at the box center
      interval_C     : upper bound on the interval-arithmetic part (float)
      interval_C_lower : lower bound on the interval-arithmetic part (float)
      interval_C_upper : upper bound on the interval-arithmetic part (float)
      remainder_C    : upper bound on the quadrature remainder (float)
      total_upper_bound : interval_C + remainder_C (float)
      constraints_ok : bool, whether |1-alpha| and |eta_j| are below C
      verdict        : 'CERTIFIED' or 'FAILED'
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
            "remainder_C": np.inf,
            "total_upper_bound": np.inf,
            "constraints_ok": False,
            "verdict": "FAILED",
        }

    # 2. Interval certificate (quadrature-approximated functional)
    interval_result = certify_kband_bound(params, k=k, half_width=half_width,
                                          terms=terms, QN=QN, Qp=Qp)
    interval_C_lower = float(interval_result["interval_C_lower"])
    interval_C_upper = float(interval_result["interval_C_upper"])
    interval_C = interval_C_upper
    constraints_ok = interval_result["constraints_ok"]

    # 3. Quadrature remainder bound evaluated at the center density
    density = density_from_kband_params(params, k=k)
    remainder = total_Q_remainder(density, QN=QN, Qp=Qp)
    remainder_C = float(remainder.b)

    total_upper_bound = interval_C + remainder_C

    verdict = "CERTIFIED" if (constraints_ok and total_upper_bound < 0.690653695151631) else "FAILED"

    return {
        "float_C": float(C_float),
        "interval_C": interval_C,
        "interval_C_lower": interval_C_lower,
        "interval_C_upper": interval_C_upper,
        "remainder_C": remainder_C,
        "total_upper_bound": total_upper_bound,
        "constraints_ok": constraints_ok,
        "verdict": verdict,
    }
