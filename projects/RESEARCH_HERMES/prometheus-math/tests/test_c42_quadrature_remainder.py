import mpmath as mp
from prometheus.c42_theorem import density_from_kband_params
from prometheus.c42_quadrature_remainder import (
    remainder_bound_Qjl,
    remainder_bound_Qjl_rigorous,
    total_Q_remainder,
    total_Q_remainder_rigorous,
)


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


def test_rigorous_remainder_dominates_heuristic_and_shrinks(certified_k3_params):
    density = density_from_kband_params(certified_k3_params, k=3)
    a_u, b_u, _ = density.bands[0]
    a_v, b_v, _ = density.bands[0]
    alpha = density.alpha
    h = remainder_bound_Qjl(a_u, b_u, a_v, b_v, alpha, QN=40, Qp=4)
    r = remainder_bound_Qjl_rigorous(a_u, b_u, a_v, b_v, alpha, QN=40, Qp=4)
    assert r.a > 0
    assert r.b >= h.a  # rigorous bound is at least the heuristic one
    r20 = remainder_bound_Qjl_rigorous(a_u, b_u, a_v, b_v, alpha, QN=20, Qp=4)
    r40 = remainder_bound_Qjl_rigorous(a_u, b_u, a_v, b_v, alpha, QN=40, Qp=4)
    assert r40.b < r20.b


def test_total_rigorous_remainder_matches_certificate(certified_k3_params):
    density = density_from_kband_params(certified_k3_params, k=3)
    heur = total_Q_remainder(density, QN=850, Qp=4)
    # At N=850 the rigorous ellipse-sampled bound is still sizable; it is a
    # valid upper bound and dominates the heuristic one.
    rig850 = total_Q_remainder_rigorous(density, QN=850, Qp=4, grid=128)
    assert rig850.a > 0
    assert rig850.b >= heur.a
    assert rig850.b <= 1.0

    # At N=1700 the bound collapses to the level used in the certificate.
    rig1700 = total_Q_remainder_rigorous(density, QN=1700, Qp=4, grid=128)
    assert rig1700.a > 0
    assert rig1700.b <= 0.001
