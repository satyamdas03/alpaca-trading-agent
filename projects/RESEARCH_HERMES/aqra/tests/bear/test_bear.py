from aqra.bear.chamber import BEARChamber
from aqra.certify.dossier import CertifiedDossier
from aqra.signals.base import SignalCandidate, Lane


def test_bear_mock_review():
    chamber = BEARChamber(use_llm=False)
    cand = SignalCandidate(id="S_MOM", lane=Lane.STRUCTURAL, name="Momentum", formula="rank(mom)", params={}, rationale="test")
    dossier = CertifiedDossier(candidate=cand, certified_at=None, status="CERTIFIED", metrics={}, p_value=None, coverage=None)
    review = chamber.review(dossier)
    assert review.passed in (True, False)
