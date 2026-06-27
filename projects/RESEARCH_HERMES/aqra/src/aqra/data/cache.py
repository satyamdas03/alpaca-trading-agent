import logging
from aqra.db import AQRADatabase
from aqra.data.yf_source import YFSource
from aqra.data.universe import Universe

logger = logging.getLogger(__name__)

class DataCache:
    def __init__(self, db: AQRADatabase, config=None):
        self.db = db
        self.yf = YFSource()
        self.universe = Universe()

    def refresh_prices(self, start: str, end: str, tickers: list[str] | None = None):
        if tickers is None:
            tickers = self.universe.at_date(end)
        for ticker in tickers[:10]:  # Phase 1: limit for speed
            try:
                df = self.yf.fetch_ohlcv(ticker, start, end)
                if df.empty:
                    continue
                self.db.conn.execute("""
                    INSERT OR REPLACE INTO raw_prices
                        (ticker, date, open, high, low, close, volume, adjusted_close, source)
                    SELECT * FROM df
                """)
                logger.info("Cached %d rows for %s", len(df), ticker)
            except Exception as e:
                logger.warning("Failed to fetch %s: %s", ticker, e)
