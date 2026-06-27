from aqra.registry.allocator import Allocator
from aqra.config import load_config
from aqra.certify.dossier import CertifiedDossier
from aqra.signals.base import SignalCandidate, Lane


def test_allocator_respects_lane_splits():
    cfg = load_config()
    alloc = Allocator(cfg)
    dossiers = [
        CertifiedDossier(candidate=SignalCandidate("S1", Lane.STRUCTURAL, "S1", "", {}, ""), certified_at=None, status="CERTIFIED", metrics={"sharpe": 1.0}, p_value=0.05, coverage=0.9),
        CertifiedDossier(candidate=SignalCandidate("I1", Lane.INFORMATIONAL, "I1", "", {}, ""), certified_at=None, status="CERTIFIED", metrics={"sharpe": 0.8}, p_value=0.05, coverage=0.9),
    ]
    weights = alloc.allocate(dossiers, regime="Risk-On")
    assert sum(w for d, w in weights if d.candidate.lane == Lane.STRUCTURAL) == cfg.lane_s_capital
    assert sum(w for d, w in weights if d.candidate.lane == Lane.INFORMATIONAL) == cfg.lane_i_capital
