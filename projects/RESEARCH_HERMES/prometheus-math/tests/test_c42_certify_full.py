import numpy as np
import pytest
from prometheus.c42_certify_full import certify_with_remainder
from prometheus.c42_kband import certify_kband_bound, kband_bound_float


def test_certify_full_k3_breaks_griego(certified_k3_params):
    result = certify_with_remainder(certified_k3_params, k=3, half_width=1e-12,
                                     QN=850, terms=500, Qp=4)
    assert result["verdict"] == "CERTIFIED"
    assert result["total_upper_bound"] < 0.3994
    assert result["constraints_ok"]
    assert result["interval_C"] > 0
    assert result["remainder_C"] >= 0
    assert result["interval_C"] + result["remainder_C"] == pytest.approx(
        result["total_upper_bound"], rel=1e-12
    )


def test_interval_encloses_float(certified_k3_params):
    C_float = kband_bound_float(certified_k3_params, k=3)[0]
    interval = certify_kband_bound(certified_k3_params, k=3, half_width=1e-12,
                                 terms=500, QN=200, Qp=4)
    assert interval["interval_C_lower"] <= C_float <= interval["interval_C_upper"]
    assert interval["constraints_ok"]
