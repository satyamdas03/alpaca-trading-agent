import numpy as np

from aqra.certify.dossier import CertifiedDossier
from aqra.config import AQRAConfig
from aqra.constants import Lane


class Allocator:
    def __init__(self, config: AQRAConfig):
        self.config = config

    def allocate(self, dossiers: list[CertifiedDossier], regime: str = "Risk-On") -> list[tuple[CertifiedDossier, float]]:
        # Split by lane
        s_dossiers = [d for d in dossiers if d.candidate.lane == Lane.STRUCTURAL]
        i_dossiers = [d for d in dossiers if d.candidate.lane == Lane.INFORMATIONAL]

        # Adjust lane split by regime
        s_weight, i_weight = self._regime_adjusted_split(regime)
        s_budget = self.config.paper_capital * s_weight
        i_budget = self.config.paper_capital * i_weight

        s_alloc = self._risk_parity(s_dossiers, s_budget)
        i_alloc = self._risk_parity(i_dossiers, i_budget)
        return [(d, a) for d, a in zip(s_dossiers, s_alloc)] + [(d, a) for d, a in zip(i_dossiers, i_alloc)]

    def _regime_adjusted_split(self, regime: str) -> tuple[float, float]:
        base_s, base_i = self.config.lane_s_split, self.config.lane_i_split
        if regime == "Bear":
            return 0.85, 0.15  # reduce fast lane in bear
        if regime == "Risk-Off":
            return 0.75, 0.25  # moderately reduce fast lane
        return base_s, base_i

    def _risk_parity(self, dossiers: list[CertifiedDossier], budget: float) -> list[float]:
        if not dossiers:
            return []
        edges = np.array([d.metrics.get("sharpe", 0) for d in dossiers])
        edges = np.maximum(edges, 0.01)
        weights = edges / edges.sum()
        # Risk parity floor: no strategy > 50% of lane budget
        weights = np.minimum(weights, 0.5)
        weights = weights / weights.sum()
        return (weights * budget).tolist()
