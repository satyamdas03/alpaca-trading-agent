import mpmath as mp
from prometheus.c42_theorem import density_from_kband_params
from prometheus.c42_quadrature_remainder import remainder_bound_Qjl


def test_remainder_bound_is_positive_and_shrinks(certified_k3_params):
    density = density_from_kband_params(certified_k3_params, k=3)
    a_u, b_u, _ = density.bands[0]
    a_v, b_v, _ = density.bands[0]
    alpha = density.alpha
    r1 = remainder_bound_Qjl(a_u, b_u, a_v, b_v, alpha, QN=20, Qp=4)
    r2 = remainder_bound_Qjl(a_u, b_u, a_v, b_v, alpha, QN=40, Qp=4)
    assert r1.a > 0
    assert r2.a > 0
    assert r2.b < r1.b
