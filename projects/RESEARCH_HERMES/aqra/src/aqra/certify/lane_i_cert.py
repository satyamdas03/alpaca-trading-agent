from datetime import datetime, timezone

from aqra.certify.dossier import CertifiedDossier
from aqra.constants import CONFORMAL_COVERAGE_TARGET, DEFAULT_LANE_I_TURNOVER_CAP


class LaneICertifier:
    def evaluate(self, candidate, metrics: dict, selected: bool, p_value: float | None = None, coverage: float | None = None) -> CertifiedDossier | None:
        reasons = []
        if not selected:
            reasons.append("Failed FDR selection")
        if metrics.get("half_life", 0) < 2:
            reasons.append("Half-life below 2 days")
        if metrics.get("turnover", 1e9) > DEFAULT_LANE_I_TURNOVER_CAP:
            reasons.append("Turnover exceeds Lane I cap")
        if coverage is not None and coverage < CONFORMAL_COVERAGE_TARGET - 0.05:
            reasons.append("Coverage below target")
        if reasons:
            return CertifiedDossier(candidate, datetime.now(timezone.utc), "REJECTED", metrics, p_value, coverage, "; ".join(reasons))
        return CertifiedDossier(candidate, datetime.now(timezone.utc), "CERTIFIED", metrics, p_value, coverage)
