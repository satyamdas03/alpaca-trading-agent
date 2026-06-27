from dataclasses import dataclass
from datetime import datetime

from aqra.signals.base import SignalCandidate


@dataclass
class CertifiedDossier:
    candidate: SignalCandidate
    certified_at: datetime
    status: str  # CERTIFIED or REJECTED
    metrics: dict
    p_value: float | None
    coverage: float | None
    rejection_reason: str | None = None
