from aqra.config import load_config
from aqra.constants import Lane


def test_config_loads_from_env(monkeypatch):
    monkeypatch.setenv("AQRA_PAPER_CAPITAL", "15000")
    cfg = load_config()
    assert cfg.paper_capital == 15000.0
    assert cfg.lane_s_split == 0.65
    assert cfg.lane_i_split == 0.35


def test_lane_enum():
    assert Lane.STRUCTURAL.value == "S"
    assert Lane.INFORMATIONAL.value == "I"
