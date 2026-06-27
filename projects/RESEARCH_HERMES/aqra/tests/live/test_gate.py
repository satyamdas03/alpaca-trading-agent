from aqra.live.gate import DeploymentGate
from aqra.config import load_config


def test_gate_refuses_live_without_keys(monkeypatch):
    monkeypatch.setenv("ALPACA_API_KEY", "")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "")
    cfg = load_config()
    gate = DeploymentGate(cfg)
    assert not gate.can_trade_live()
