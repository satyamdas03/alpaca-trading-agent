import pandas as pd
from aqra.features.pit import PITGuard


class LaneIFeatureBuilder:
    def __init__(self, db):
        self.db = db
        self.guard = PITGuard()

    def _overnight_gap(self, prices: pd.DataFrame) -> pd.DataFrame:
        prices = prices.sort_values(["ticker", "date"])
        prices["prev_close"] = prices.groupby("ticker")["adjusted_close"].shift(1)
        prices["overnight_gap"] = (prices["open"] - prices["prev_close"]) / prices["prev_close"]
        return prices

    def _volume_zscore(self, prices: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        prices = prices.sort_values(["ticker", "date"])
        prices["volume_ma"] = prices.groupby("ticker")["volume"].transform(lambda x: x.shift(1).rolling(window).mean())
        prices["volume_std"] = prices.groupby("ticker")["volume"].transform(lambda x: x.shift(1).rolling(window).std())
        prices["volume_zscore"] = (prices["volume"] - prices["volume_ma"]) / prices["volume_std"]
        return prices

    def build(self, start: str, end: str) -> pd.DataFrame:
        query = """
            SELECT ticker, date, open, adjusted_close, volume
            FROM raw_prices
            WHERE date BETWEEN ? AND ?
            ORDER BY ticker, date
        """
        prices = self.db.conn.execute(query, [start, end]).fetchdf()
        prices = self._overnight_gap(prices)
        prices = self._volume_zscore(prices)
        # Placeholders for sentiment/earnings
        prices["news_sentiment_zscore"] = 0.0
        prices["earnings_surprise"] = 0.0
        prices["insider_event_score"] = 0.0
        prices["available_at"] = prices["date"] + pd.Timedelta(days=1)
        return prices[[
            "ticker", "date", "overnight_gap", "volume_zscore",
            "news_sentiment_zscore", "earnings_surprise", "insider_event_score", "available_at"
        ]]
