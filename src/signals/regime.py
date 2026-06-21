from enum import Enum


class Regime(Enum):
    RISK_ON = "risk_on"
    LATE_CYCLE = "late_cycle"
    STRESS = "stress"


def classify_regime(vix: float) -> Regime:
    if vix < 20:
        return Regime.RISK_ON
    elif vix <= 30:
        return Regime.LATE_CYCLE
    else:
        return Regime.STRESS


_REGIME_SHIFTS = {
    Regime.RISK_ON: {"momentum": 1.3, "value": 0.7, "low_vol": 0.8},
    Regime.LATE_CYCLE: {"momentum": 0.8, "value": 1.3, "low_vol": 1.1},
    Regime.STRESS: {"momentum": 0.6, "value": 1.0, "low_vol": 1.5},
}


def adjust_weights(base: dict[str, float], regime: Regime) -> dict[str, float]:
    shifts = _REGIME_SHIFTS[regime]
    adjusted = {}
    for factor, weight in base.items():
        shift = shifts.get(factor, 1.0)
        adjusted[factor] = weight * shift
    total = sum(adjusted.values())
    return {k: v / total for k, v in adjusted.items()}