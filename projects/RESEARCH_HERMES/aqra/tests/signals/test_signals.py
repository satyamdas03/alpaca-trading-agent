from aqra.signals.base import Lane
from aqra.signals.lane_s_signals import LaneSSignalLibrary


def test_lane_s_candidates_have_correct_lane():
    lib = LaneSSignalLibrary()
    cands = lib.generate()
    assert len(cands) >= 3
    assert all(c.lane == Lane.STRUCTURAL for c in cands)
