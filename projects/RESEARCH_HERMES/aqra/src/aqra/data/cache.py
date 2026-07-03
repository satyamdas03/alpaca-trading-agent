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

    def refresh_prices(self, start: str, end: str, tickers: list[str] | None = None,
                       limit: int | None = None):
        """Bulk-ingest OHLCV for the (historical) universe into raw_prices.

        Universe = union of members at start and at end, so tickers that
        entered or left during the window are included (survivorship-free).
        """
        if tickers is None:
            members = set(self.universe.at_date(start)) | set(self.universe.at_date(end))
            tickers = sorted(members)
        if limit:
            tickers = tickers[:limit]
        # Wikipedia uses dots in some symbols (BRK.B); yfinance wants dashes.
        yf_tickers = [t.replace(".", "-") for t in tickers]
        df = self.yf.fetch_ohlcv_many(yf_tickers, start, end)
        if df.empty:
            logger.warning("No price data downloaded for %d tickers", len(tickers))
            return 0
        # store under the yfinance symbol form for consistency
        self.db.conn.execute("""
            INSERT OR REPLACE INTO raw_prices
                (ticker, date, open, high, low, close, volume, adjusted_close, source)
            SELECT ticker, date, open, high, low, close, volume, adjusted_close, source
            FROM df
        """)
        logger.info("Cached %d rows for %d tickers", len(df), df["ticker"].nunique())
        return len(df)
