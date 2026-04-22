from src.signals.regime import classify_regime, adjust_weights, Regime

def test_risk_on():
    assert classify_regime(vix=18.0) == Regime.RISK_ON

def test_late_cycle():
    assert classify_regime(vix=22.0) == Regime.LATE_CYCLE

def test_stress():
    assert classify_regime(vix=35.0) == Regime.STRESS

def test_adjust_weights_risk_on():
    base = {"quality": 0.25, "momentum": 0.30, "value": 0.10, "low_vol": 0.15, "sentiment": 0.20}
    adjusted = adjust_weights(base, Regime.RISK_ON)
    assert adjusted["momentum"] > base["momentum"]
    assert adjusted["value"] < base["value"]

def test_adjust_weights_stress():
    base = {"quality": 0.25, "momentum": 0.30, "value": 0.10, "low_vol": 0.15, "sentiment": 0.20}
    adjusted = adjust_weights(base, Regime.STRESS)
    assert adjusted["low_vol"] > base["low_vol"]
    assert adjusted["momentum"] < base["momentum"]

def test_weights_sum_to_one():
    base = {"quality": 0.25, "momentum": 0.30, "value": 0.10, "low_vol": 0.15, "sentiment": 0.20}
    for regime in Regime:
        adjusted = adjust_weights(base, regime)
        assert abs(sum(adjusted.values()) - 1.0) < 0.01