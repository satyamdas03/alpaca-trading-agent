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


def online_by_rejections(pvals: list[float], alpha: float = 0.20) -> list[bool]:
    """Sequential BY-FDR over prefixes: rejection set at the final step.

    At every audit time t we run Benjamini-Yekutieli on the first t p-values.
    Because each prefix is a fixed (non-data-dependent) subset and BY controls
    FDR under arbitrary dependence, the reported rejection set is FDR-controlled
    at every t. This function returns the mask at t = len(pvals).
    """
    p = np.array(pvals)
    n = len(p)
    mask = np.zeros(n, dtype=bool)
    for t in range(1, n + 1):
        mask[:t] = benjamini_yekutieli(p[:t].tolist(), alpha)
    return mask.tolist()


def online_lond_rejections(pvals: list[float], alpha: float = 0.20) -> list[bool]:
    """LOND online FDR with a fixed spending sequence.

    alpha_i = alpha * gamma_i where gamma_i = 6 / (pi^2 * i^2) sums to 1.
    Reject H_i if p_i <= alpha_i. Under independent p-values this controls
    FDR <= alpha; here it is included as an empirical power probe.
    """
    p = np.array(pvals)
    n = len(p)
    if n == 0:
        return []
    gamma = 6.0 / (np.pi ** 2 * np.arange(1, n + 1) ** 2)
    return (p <= alpha * gamma).tolist()
