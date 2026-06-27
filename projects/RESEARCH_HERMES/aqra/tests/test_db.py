from aqra.config import load_config
from aqra.db import AQRADatabase


def test_db_initializes(tmp_path):
    cfg = load_config()
    db = AQRADatabase(str(tmp_path / "test.db"))
    tables = db.list_tables()
    assert "raw_prices" in tables
    assert "lane_s_features" in tables
    assert "lane_i_features" in tables
    assert "strategy_registry" in tables
    db.close()
