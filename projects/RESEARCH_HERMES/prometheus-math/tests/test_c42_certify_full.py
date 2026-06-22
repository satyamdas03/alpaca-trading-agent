import numpy as np
import pytest
from prometheus.c42_certify_full import certify_with_remainder
from prometheus.c42_kband import certify_kband_bound, kband_bound_float


def test_certify_full_k3_breaks_griego(certified_k3_params):
    # QN=1700 is required for the rigorous 2D quadrature remainder to collapse;
    # at N=850 the Bernstein-ellipse far-bound is still too conservative.
    result = certify_with_remainder(certified_k3_params, k=3, half_width=1e-12,
                                     QN=1700, terms=500, Qp=4, grid=64)
    assert result["verdict"] == "CERTIFIED"
    # The unrigorous quadrature value is ~0.39933335; the validated remainder
    # lifts the rigorous certificate slightly above 0.4.
    assert result["total_upper_bound"] < 0.401
    assert result["constraints_ok"]
    assert result["interval_C"] > 0
    assert result["q_remainder"] >= 0
    assert result["k_tail"] >= 0
    assert result["d_tail"] >= 0


def test_interval_encloses_float(certified_k3_params):
    result = certify_with_remainder(certified_k3_params, k=3, half_width=1e-12,
                                     QN=50, terms=500, Qp=4)
    assert result["interval_C_lower"] <= result["float_C"] <= result["interval_C_upper"]
    assert result["constraints_ok"]
