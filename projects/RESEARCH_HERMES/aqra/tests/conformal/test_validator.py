import numpy as np
from aqra.conformal.validator import ConformalValidator


def test_coverage_on_exchangeable_data():
    np.random.seed(42)
    calib_pred = np.random.randn(500)
    calib_true = calib_pred + np.random.randn(500)  # residual ~ N(0,1)
    test_pred = np.random.randn(100)
    test_true = test_pred + np.random.randn(100)
    validator = ConformalValidator(calib_pred, calib_true, alpha=0.10)
    intervals = [validator.predict_interval(p) for p in test_pred]
    covered = sum(lo <= t <= hi for (lo, hi), t in zip(intervals, test_true)) / len(test_true)
    assert 0.80 <= covered <= 0.99
