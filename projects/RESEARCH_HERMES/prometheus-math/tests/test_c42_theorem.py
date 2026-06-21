import json
import numpy as np
import pytest
from prometheus.c42_theorem import density_from_kband_params, F_functional


# Absolute tolerance used for reproducing published/float reference values.
FLOAT_REPRO_TOL = 2e-9


def test_griego_density_reproduces_float(griego_params):
    """k=2 density built from Griego's published point reproduces Griego's C."""
    dens = density_from_kband_params(griego_params, k=2)
    Y, D, C = F_functional(dens, terms=3000, QN=500, Qp=4)
    assert abs(C - 0.690653695151631) < FLOAT_REPRO_TOL


def test_certified_k3_density_reproduces_float(certified_k3_params):
    """k=3 density built from the certified fixture reproduces the certified C bound."""
    dens = density_from_kband_params(certified_k3_params, k=3)
    Y, D, C = F_functional(dens, terms=3000, QN=500, Qp=4)
    # Compare against the high-resolution float reference stored with the certificate.
    path = "state/CERTIFIED_BREAKTHROUGH_k3_2026-06-20.json"
    with open(path) as f:
        reference = json.load(f)["float_C_hi_res"]
    assert abs(C - reference) < FLOAT_REPRO_TOL
