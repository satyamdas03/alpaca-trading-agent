import numpy as np

from prometheus.c42_kband import kband_bound_float, GRIEGO_C
from prometheus.c42_kband_v2 import kband_bound_float_v2, certify_kband_bound_v2

GRIEGO = np.array([0.36988243, 0.61927309, 0.57623741, 0.59839764, -0.34485185])
# Fully certified record point (state/CERTIFIED_v2b_k3_2026-07-03.json)
RECORD = np.array([0.33343967459766227, 0.5164076199266799, 0.6841540991146009,
                   0.6136920065378704, 0.5481367168410389, -0.4194208225287134,
                   0.6517017631935356, -0.22727123236041122])
RECORD_FLOAT_C = 0.690205297670182
RECORD_TOTAL_UPPER = 0.690395202310285


def test_v2_equals_v1_on_symmetric_k2():
    """For the symmetric k=2 band the corrected kernel integrates to the same
    value, so v1 and v2 must agree (and reproduce Griego)."""
    C1, _, _ = kband_bound_float(GRIEGO, 2, terms=2000, QN=400, Qp=4)
    C2, _, _ = kband_bound_float_v2(GRIEGO, 2, terms=2000, QN=400, Qp=4)
    assert abs(C1 - C2) < 1e-12
    assert abs(C2 - GRIEGO_C) < 1e-9


def test_record_point_float_value():
    C, Y, D = kband_bound_float_v2(RECORD, 3, terms=4000, QN=1200, Qp=4)
    assert abs(C - RECORD_FLOAT_C) < 1e-9
    assert C < GRIEGO_C
    # constraints strictly below C
    alpha = RECORD[2] + 1j * RECORD[3]
    assert abs(1 - alpha) < C
    assert abs(RECORD[4] + 1j * RECORD[5]) < C
    assert abs(RECORD[6] + 1j * RECORD[7]) < C


def test_record_point_interval_certificate_smoke():
    """Quick interval check (low QN): encloses float and enforces t1 > 1/3."""
    res = certify_kband_bound_v2(RECORD, 3, half_width=1e-12, terms=1000, QN=40, Qp=4)
    assert res["t1_above_one_third"]
    C, _, _ = kband_bound_float_v2(RECORD, 3, terms=1000, QN=40, Qp=4)
    assert float(res["interval_C_lower"]) <= C <= float(res["interval_C_upper"])


def test_v1_linear_term_differs_for_asymmetric_k3():
    """Documents the v1 kernel bug: for asymmetric k=3 bands the two
    functionals must differ (v1 is retracted for k >= 3)."""
    C1, _, _ = kband_bound_float(RECORD, 3, terms=1500, QN=300, Qp=4)
    C2, _, _ = kband_bound_float_v2(RECORD, 3, terms=1500, QN=300, Qp=4)
    assert abs(C1 - C2) > 1e-4
