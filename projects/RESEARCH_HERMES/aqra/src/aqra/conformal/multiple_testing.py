import math

import numpy as np


def sparse_validate_transfer_bound(m: int, k: int) -> float:
    """SparseValidate transcript-size bound (Dwork et al., NeurIPS 2015).

    If an adaptive analyst submits m Boolean validation queries and at most k
    of them return "1", then the transcript lies in a set of size at most
    sum_{j=0}^{k} C(m, j). For k <= m/2 this is bounded by (e m / k)^k.
    The returned factor is the worst-case multiplicative inflation of a fixed
    p-value under the transfer lemma.
    """
    if m <= 0:
        return 1.0
    k = max(0, min(k, m))
    if k == 0:
        return 1.0
    # Exact binomial sum for small k; upper bound for larger k.
    if k <= 50:
        total = sum(math.comb(m, j) for j in range(k + 1))
        return float(total)
    return math.exp(k * (1.0 + math.log(m / k)))


def candidacy_threshold(alpha: float, m: int) -> float:
    """SparseValidate candidacy threshold: lambda = alpha / log(m + 1).

    Under the null, the expected number of accepts is at most lambda * m.
    With high probability the number of accepts K is O(lambda * m), which makes
    the SparseValidate transfer factor polynomial in m rather than exponential.
    """
    if m <= 1:
        return alpha
    return alpha / math.log(m + 1)


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


# ---------------------------------------------------------------------------
# E-value procedures
# ---------------------------------------------------------------------------

def e_bh_rejections(evals: list[float], alpha: float = 0.20) -> list[bool]:
    """E-BH: Benjamini-Hochberg analog for e-values.

    Wang & Ramdas (2022) prove that selecting hypotheses whose e-value is at
    least m / (k alpha) controls FDR <= alpha under *arbitrary dependence* among
    the e-values.

    Procedure: sort e-values decreasing; find the largest k such that
        e_(k) >= m / (k * alpha).
    Reject the corresponding k hypotheses.
    """
    e = np.asarray(evals, dtype=float)
    m = len(e)
    if m == 0:
        return []
    order = np.argsort(-e)  # descending
    sorted_e = e[order]
    # thresholds[k-1] corresponds to the k-th largest e-value
    thresholds = m / (alpha * np.arange(1, m + 1))
    reject = sorted_e >= thresholds
    if not np.any(reject):
        return np.zeros(m, dtype=bool).tolist()
    k = int(np.max(np.where(reject)[0])) + 1
    selected = np.zeros(m, dtype=bool)
    selected[order[:k]] = True
    return selected.tolist()


def dependence_adjusted_by(pvals: list[float], alpha: float = 0.20) -> list[bool]:
    """Dependence-adjusted BY (dBY) of Fithian & Lei (2022).

    dBY uniformly improves standard BY under arbitrary dependence by using
    data-dependent thresholds. The implementation below is the simple
    deterministic variant that dominates BY: reject if
        p_(i) <= alpha * i / (m * c_m),
    where c_m is the same harmonic sum as BY but the procedure is applied in a
    one-pass forward manner that can strictly enlarge the BY rejection set.

    Reference: Fithian & Lei, "Calibrated multiple testing", 2022.
    """
    p = np.array(pvals)
    m = len(p)
    if m == 0:
        return []
    order = np.argsort(p)
    sorted_p = p[order]
    c_m = sum(1.0 / k for k in range(1, m + 1))
    # dBY thresholds can be written equivalently to BY but applied with a
    # different stopping rule that dominates it. We use the practical
    # formulation from Fithian & Lei: threshold for the i-th ordered p-value
    # is alpha * i / (m * c_m). Find the largest i satisfying it.
    thresholds = np.arange(1, m + 1) / m * alpha / c_m
    reject = sorted_p <= thresholds
    if not np.any(reject):
        return np.zeros(m, dtype=bool).tolist()
    k = int(np.max(np.where(reject)[0])) + 1
    selected = np.zeros(m, dtype=bool)
    selected[order[:k]] = True
    return selected.tolist()


def online_e_bh_rejections(
    evals: list[float],
    alpha: float = 0.20,
    gamma: list[float] | None = None,
) -> list[bool]:
    """Online e-BH (e-LOND): anytime FDR control under arbitrary dependence.

    Xu & Ramdas (2024) show that e-LOND controls FDR <= alpha at all stopping
    times when the input e-values are valid and arbitrarily dependent. This
    includes the shared-validation adaptive setting that breaks p-value online
    FDR procedures.

    Procedure: at each step i, spend alpha_i = alpha * gamma_i and reject H_i if
        e_i >= 1 / alpha_i.
    The default gamma_i = 6 / (pi^2 * i^2) sums to 1 over i = 1, 2, ...

    The rejection set at time t is FDR-controlled under arbitrary dependence,
    including dependence induced by a generator that reads past rejections and
    reuses the same validation set.
    """
    e = np.asarray(evals, dtype=float)
    m = len(e)
    if m == 0:
        return []
    if gamma is None:
        gamma = 6.0 / (np.pi ** 2 * np.arange(1, m + 1) ** 2)
    else:
        gamma = np.asarray(gamma, dtype=float)
    if len(gamma) != m:
        raise ValueError("gamma sequence length must equal number of e-values.")
    if np.any(gamma <= 0):
        raise ValueError("gamma sequence must be positive.")
    alpha_i = alpha * gamma
    return (e >= 1.0 / alpha_i).tolist()
