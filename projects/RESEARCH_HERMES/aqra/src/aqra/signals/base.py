from dataclasses import dataclass

from aqra.constants import Lane


@dataclass
class SignalCandidate:
    id: str
    lane: Lane
    name: str
    formula: str  # human-readable formula
    params: dict
    rationale: str
