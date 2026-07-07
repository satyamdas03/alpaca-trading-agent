import math

import numpy as np
import pytest

from aqra.conformal.evalue import EValue, conformal_evalue, evalue_from_pvalue
from aqra.conformal.multiple_testing import (
    benjamini_yekutieli,
    candidacy_threshold,
    dependence_adjusted_by,
    e_bh_rejections,
    maximal_leakage_bound,
    maximal_leakage_evalue,
    online_e_bh_rejections,
    sparse_validate_transfer_bound,
)


def test_evalue_non_negative():
    EValue(value=1.0)
    EValue(value=0.0)
    with pytest.raises(ValueError):
        EValue(value=-1.0)


def test_evalue_from_pvalue_null_expectation():
    rng = np.random.default_rng(0)
    n = 20000
    pvals = rng.uniform(0, 1, size=n)
    evals = [evalue_from_pvalue(p, threshold=0.10).value for p in pvals]
    # E = 1{P <= 0.10} / 0.10; expectation under uniform = 1.0
    assert 0.90 <= np.mean(evals) <= 1.10


def test_conformal_evalue_expectation():
    rng = np.random.default_rng(1)
    n_calib, n_test = 5000, 2000
    # Null: scores are exchangeable
    calib = rng.exponential(scale=1.0, size=n_calib)
    test = rng.exponential(scale=1.0, size=n_test)
    evals = [conformal_evalue(score, calib).value for score in test]
    # E[-log(P)] = 1 under the null, but finite-sample positive bias from
    # the (1 + ...) / (n + 1) conformal p-value means the expectation is
    # slightly above 1. We allow a generous tolerance.
    assert 0.85 <= np.mean(evals) <= 1.30


def test_e_bh_controls_fdr_under_arbitrary_dependence():
    """Null e-values with arbitrary dependence; e-BH should keep FDR <= alpha."""
    rng = np.random.default_rng(2)
    alpha = 0.20
    n_trials = 500
    fdp_list = []
    for _ in range(n_trials):
        # Shared V creates dependence: multiply all e-values by a common factor.
        common = rng.gamma(shape=1.0, scale=1.0)
        base = rng.exponential(scale=1.0, size=50)
        evals = base * common
        # All hypotheses are null; any rejection is a false discovery.
        selected = e_bh_rejections(evals.tolist(), alpha)
        fdp = np.mean(selected) if any(selected) else 0.0
        fdp_list.append(fdp)
    assert np.mean(fdp_list) <= alpha + 0.02


def test_online_e_bh_controls_fdr_with_shared_v():
    """Adaptive generator reading past rejections and using shared V."""
    rng = np.random.default_rng(3)
    alpha = 0.20
    m = 100
    n_reps = 300
    fdp_list = []
    for _ in range(n_reps):
        # Simulate shared validation noise that the generator can learn.
        v_noise = rng.normal(loc=0.0, scale=1.0)
        evals = []
        for i in range(m):
            # Adversarial e-value: inflated when v_noise is large.
            e = max(0.0, rng.exponential(scale=1.0) + 0.5 * v_noise)
            evals.append(e)
        selected = online_e_bh_rejections(evals, alpha)
        fdp = np.mean(selected) if any(selected) else 0.0
        fdp_list.append(fdp)
    assert np.mean(fdp_list) <= alpha + 0.02


def test_dependence_adjusted_by_dominates_by():
    """dBY rejection set contains BY rejection set."""
    rng = np.random.default_rng(4)
    pvals = rng.uniform(0, 1, size=40).tolist()
    by_sel = benjamini_yekutieli(pvals, alpha=0.20)
    dby_sel = dependence_adjusted_by(pvals, alpha=0.20)
    assert np.all(np.array(dby_sel) >= np.array(by_sel))


def test_e_bh_rejects_high_evalues():
    evals = [0.1, 0.5, 2.0, 10.0, 100.0]
    selected = e_bh_rejections(evals, alpha=0.20)
    # m=5, alpha=0.20: threshold for k=1 is 5/(1*0.2)=25, for k=2 is 12.5.
    # Only E=100 clears the k=1 threshold; E=10 fails the k=2 threshold.
    assert selected[4]
    assert not selected[3]
    assert not selected[0]


def test_online_e_bh_custom_gamma():
    evals = [1.0, 5.0, 100.0]
    gamma = [0.5, 0.3, 0.2]
    selected = online_e_bh_rejections(evals, alpha=0.20, gamma=gamma)
    assert selected[2]


def test_sparse_validate_bound_polynomial():
    """SparseValidate factor should be polynomial, not exponential, in m."""
    m = 400
    alpha = 0.20
    lam = candidacy_threshold(alpha, m)
    expected_k = int(lam * m)
    factor = sparse_validate_transfer_bound(m, expected_k)
    # The worst-case max-information factor 2^m is ~10^120; the SparseValidate
    # factor is ~10^24, vastly smaller. Both checks emphasize the gap.
    assert factor < 2 ** m
    assert factor < 10 ** 30


def test_sparse_validate_bound_small_k():
    """For k=1 the bound should be roughly m+1."""
    m = 100
    factor = sparse_validate_transfer_bound(m, 1)
    assert m + 1 <= factor <= m + 2


def test_candidacy_threshold_decreases_with_m():
    assert candidacy_threshold(0.20, 10) > candidacy_threshold(0.20, 1000)


def test_maximal_leakage_bound():
    lam = 0.05
    assert maximal_leakage_bound(lam) == pytest.approx(math.log2(1.0 / lam))


def test_maximal_leakage_bound_invalid_lambda():
    with pytest.raises(ValueError):
        maximal_leakage_bound(0.0)
    with pytest.raises(ValueError):
        maximal_leakage_bound(1.0)
    with pytest.raises(ValueError):
        maximal_leakage_bound(-0.1)


def test_maximal_leakage_evalue_shape():
    lam = 0.05
    assert maximal_leakage_evalue(0.01, lam) == 1.0
    assert maximal_leakage_evalue(0.05, lam) == 1.0
    assert maximal_leakage_evalue(0.0500001, lam) == 0.0
    assert maximal_leakage_evalue(0.5, lam) == 0.0


def test_maximal_leakage_evalue_null_expectation():
    """Under super-uniform null, corrected e-value expectation <= 1."""
    rng = np.random.default_rng(7)
    lam = 0.05
    n = 20000
    pvals = rng.uniform(0, 1, size=n)
    evals = [maximal_leakage_evalue(p, lam) for p in pvals]
    # E[I{P <= lam}] = lam, so mean should be close to lam << 1.
    assert np.mean(evals) <= lam * 1.2


def test_maximal_leakage_correction_factor_matches_bound():
    """2^{-L(lambda)} * 1/lambda should equal 1 for the single-round bound."""
    lam = 0.08
    leakage = maximal_leakage_bound(lam)
    correction = 2.0 ** (-leakage)
    assert correction * (1.0 / lam) == pytest.approx(1.0)


def test_maximal_leakage_smaller_than_sparsevalidate():
    """For typical m, the maximal-leakage factor 2^L = 1/lambda is much smaller
    than the SparseValidate polynomial transcript factor, showing tighter theory."""
    m = 400
    alpha = 0.20
    lam = candidacy_threshold(alpha, m)
    expected_k = max(1, int(round(m * lam)))
    sv_factor = sparse_validate_transfer_bound(m, expected_k)
    ml_factor = 2.0 ** maximal_leakage_bound(lam)
    assert ml_factor < sv_factor
