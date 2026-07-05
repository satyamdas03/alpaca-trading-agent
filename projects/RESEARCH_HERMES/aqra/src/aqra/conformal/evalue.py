"""E-value primitives for the Honest Agent Protocol.

An e-value is a non-negative random variable E with E_{H_0}[E] <= 1. E-values
are the currency of the e-BH and online e-BH procedures; they control FDR under
arbitrary dependence without the logarithmic correction that plagues p-value
procedures under dependence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class EValue:
    """A generic e-value with optional metadata."""

    value: float
    signal_id: str | None = None
    source: str | None = None

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("E-value must be non-negative.")

    def __float__(self):
        return float(self.value)

    def __lt__(self, other):
        return float(self) < float(other)


def evalue_from_pvalue(p: float, threshold: float = 1.0) -> EValue:
    """Convert a p-value into an e-value via the universal inference kernel.

    E = 1{P <= t} / t is an e-value under the null because Pr(P <= t) <= t.
    Setting t=1 recovers E = 1/P, but t can be tuned for power.
    """
    if p <= 0:
        return EValue(value=float("inf"))
    return EValue(value=(1.0 if p <= threshold else 0.0) / threshold)


def conformal_evalue(
    nonconformity_score: float,
    calib_scores: Sequence[float],
) -> EValue:
    """Build an e-value from a split-conformal nonconformity score.

    The conformal p-value is
        p = (1 + #{calib scores >= test score}) / (|calib| + 1).
    Under the null, P is super-uniform, so E[-log(P)] = 1 because
    E[-log(U)] = 1 for U ~ Uniform[0,1]. Hence we use the e-value
        E = -log(p).
    This is more powerful than the thresholded 1{p <= t}/t e-value while
    still having exact expectation 1 under the null.
    """
    calib = np.asarray(calib_scores, dtype=float)
    p = (1.0 + np.sum(calib >= nonconformity_score)) / (len(calib) + 1.0)
    if p <= 0:
        return EValue(value=float("inf"))
    # Clamp tiny p-values to avoid overflow while preserving validity.
    p_clamped = max(p, np.finfo(float).tiny)
    return EValue(value=float(-np.log(p_clamped)))
