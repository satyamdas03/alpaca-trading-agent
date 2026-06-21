import numpy as np
from prometheus.c42_certify_full import certify_with_remainder


def test_certify_full_k3_breaks_griego(certified_k3_params):
    result = certify_with_remainder(certified_k3_params, k=3, half_width=1e-12,
                                     QN=850, terms=500, Qp=4)
    assert result["verdict"] == "CERTIFIED"
    assert result["total_upper_bound"] < 0.3994
    assert result["constraints_ok"]
