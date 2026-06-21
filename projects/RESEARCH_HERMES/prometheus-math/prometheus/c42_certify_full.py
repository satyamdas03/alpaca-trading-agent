"""Full rigorous certificate: float check + interval check + quadrature remainder."""
import numpy as np
import mpmath as mp
from mpmath import iv

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
      float_C, interval_C_lower, interval_C_upper, remainder_upper,
      total_upper_bound, constraints_ok, verdict
    """
    params = np.asarray(params, dtype=float)

    # 1. Float sanity check
    float_C = kband_bound_float(params, k=k, terms=terms, QN=QN, Qp=Qp)

    # 2. Interval certificate (quadrature-approximated functional)
    interval_result = certify_kband_bound(params, k=k, half_width=half_width,
                                          terms=terms, QN=QN, Qp=Qp)
    interval_C_upper = interval_result["interval_C_upper"]
    interval_C_lower = interval_result["interval_C_lower"]
    constraints_ok = interval_result["constraints_ok"]

    # 3. Quadrature remainder bound evaluated at the center density
    density = density_from_kband_params(params, k=k)
    remainder = total_Q_remainder(density, QN=QN, Qp=Qp)
    remainder_upper = float(remainder.b)

    total_upper_bound = interval_C_upper + remainder_upper

    verdict = "CERTIFIED" if (constraints_ok and total_upper_bound < 0.690653695151631) else "FAILED"

    return {
        "float_C": float_C,
        "interval_C_lower": interval_C_lower,
        "interval_C_upper": interval_C_upper,
        "remainder_upper": remainder_upper,
        "total_upper_bound": total_upper_bound,
        "constraints_ok": constraints_ok,
        "verdict": verdict,
    }
