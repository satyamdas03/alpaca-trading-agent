from aqra.db import AQRADatabase
from aqra.data.cache import DataCache


def test_cache_refresh_prices(tmp_path):
    db = AQRADatabase(str(tmp_path / "cache.db"))
    cache = DataCache(db)
    cache.refresh_prices("2024-01-01", "2024-01-10", tickers=["AAPL"])
    rows = db.conn.execute("SELECT COUNT(*) FROM raw_prices").fetchone()[0]
    assert rows > 0
    db.close()
