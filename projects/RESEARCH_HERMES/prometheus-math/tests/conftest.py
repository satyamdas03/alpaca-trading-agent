import json
import numpy as np
import pytest


@pytest.fixture
def griego_params():
    """Griego's published two-block point; k=2 reproduction target."""
    return np.array([
        0.36988243,          # tau
        0.61927309,          # Re(alpha)
        0.57623741,          # Im(alpha)
        0.59839764,          # Re(eta)
        -0.34485185,         # Im(eta)
    ])


@pytest.fixture
def certified_k3_params():
    """Certified k=3 point from state/CERTIFIED_BREAKTHROUGH_k3_2026-06-20.json."""
    path = "state/CERTIFIED_BREAKTHROUGH_k3_2026-06-20.json"
    with open(path) as f:
        d = json.load(f)
    return np.array(d["params"])


@pytest.fixture
def candidate_k3_params():
    """Best unverified k=3 float candidate; needs recertification."""
    return np.array([
        0.04736092,
        0.99999999,
        0.96043835,
        0.358515,
        0.36855868,
        0.01748711,
        0.17863707,
        -0.32284686,
    ])
