from datetime import datetime, timezone

from aqra.certify.dossier import CertifiedDossier
from aqra.constants import CONFORMAL_COVERAGE_TARGET


class LaneSCertifier:
    def evaluate(self, candidate, metrics: dict, selected: bool, p_value: float | None = None, coverage: float | None = None) -> CertifiedDossier | None:
        reasons = []
        if not selected:
            reasons.append("Failed FDR selection")
        if metrics.get("sharpe", 0) < 0.6:
            reasons.append("Sharpe below 0.6")
        if metrics.get("max_drawdown", 0) < -0.20:
            reasons.append("Drawdown exceeds 20%")
        if metrics.get("turnover", 1e9) > 1.0:  # 100% annualized
            reasons.append("Turnover exceeds Lane S cap")
        if coverage is not None and coverage < CONFORMAL_COVERAGE_TARGET - 0.05:
            reasons.append("Coverage below target")
        if reasons:
            return CertifiedDossier(candidate, datetime.now(timezone.utc), "REJECTED", metrics, p_value, coverage, "; ".join(reasons))
        return CertifiedDossier(candidate, datetime.now(timezone.utc), "CERTIFIED", metrics, p_value, coverage)
