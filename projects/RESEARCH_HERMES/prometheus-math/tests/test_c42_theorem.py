import numpy as np
from prometheus.c42_theorem import density_from_kband_params, F_functional


def test_griego_density_reproduces_float(certified_k3_params):
    # Use only the first 5 values and interpret as k=2 params.
    # The tau placeholder from certified_k3_params[0] is replaced with Griego's
    # published tau so that the test reproduces Griego's C value.
    p2 = np.array([
        0.36988243,  # replaced tau placeholder with Griego's tau
        0.61927309,
        0.57623741,
        0.59839764,
        -0.34485185,
    ])
    dens = density_from_kband_params(p2, k=2)
    Y, D, C = F_functional(dens, terms=3000, QN=500, Qp=4)
    assert abs(C - 0.690653695151631) < 1e-9
