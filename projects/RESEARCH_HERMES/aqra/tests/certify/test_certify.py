from aqra.signals.base import SignalCandidate, Lane
from aqra.certify.lane_s_cert import LaneSCertifier


def test_lane_s_certifier_accepts_good_candidate():
    cert = LaneSCertifier()
    cand = SignalCandidate(id="S_MOM", lane=Lane.STRUCTURAL, name="Momentum", formula="rank(mom)", params={}, rationale="test")
    metrics = {"sharpe": 1.2, "max_drawdown": -0.10, "ic": 0.06, "turnover": 0.8}
    result = cert.evaluate(cand, metrics, selected=True)
    assert result is not None
    assert result.status == "CERTIFIED"
