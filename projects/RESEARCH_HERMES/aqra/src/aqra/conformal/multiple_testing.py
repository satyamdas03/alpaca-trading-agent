import numpy as np


def benjamini_yekutieli(pvals: list[float], alpha: float = 0.20) -> list[bool]:
    """BY procedure controlling FDR under arbitrary dependence."""
    p = np.array(pvals)
    n = len(p)
    if n == 0:
        return []
    order = np.argsort(p)
    sorted_p = p[order]
    # harmonic sum
    c_m = sum(1.0 / k for k in range(1, n + 1))
    thresholds = np.arange(1, n + 1) / n * alpha / c_m
    reject = sorted_p <= thresholds
    max_reject = np.where(reject)[0]
    k = max_reject[-1] + 1 if len(max_reject) > 0 else 0
    selected = np.zeros(n, dtype=bool)
    if k > 0:
        selected[order[:k]] = True
    return selected.tolist()
