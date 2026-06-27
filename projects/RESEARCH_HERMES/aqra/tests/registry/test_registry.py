from datetime import datetime, timezone

from aqra.certify.dossier import CertifiedDossier
from aqra.config import load_config
from aqra.db import AQRADatabase
from aqra.registry.registry import StrategyRegistry
from aqra.signals.base import SignalCandidate, Lane


def test_registry_registers_certified_dossier(tmp_path):
    db = AQRADatabase(str(tmp_path / "registry.db"))
    registry = StrategyRegistry(db)
    cand = SignalCandidate("S1", Lane.STRUCTURAL, "Momentum", "rank(mom)", {"h": 21}, "test")
    dossier = CertifiedDossier(
        candidate=cand,
        certified_at=datetime.now(timezone.utc),
        status="CERTIFIED",
        metrics={"sharpe": 1.0},
        p_value=0.05,
        coverage=0.92,
    )
    registry.register(dossier)
    active = registry.active_strategies()
    assert len(active) == 1
    assert active[0][0] == "S1"
