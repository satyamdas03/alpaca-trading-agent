import numpy as np
import pandas as pd
from aqra.features.pit import PITGuard


class LaneSFeatureBuilder:
    def __init__(self, db):
        self.db = db
        self.guard = PITGuard()

    def _momentum_12_1(self, prices: pd.DataFrame) -> pd.DataFrame:
        prices = prices.sort_values(["ticker", "date"])
        prices["mom_12_1"] = prices.groupby("ticker")["adjusted_close"].transform(
            lambda x: x.shift(21) / x.shift(252) - 1
        )
        return prices

    def _value_ranks(self, fundamentals: pd.DataFrame) -> pd.DataFrame:
        # Placeholder: P/E and P/B percentile ranks within universe
        fundamentals["pe_rank"] = fundamentals.groupby("date")["pe_ttm"].rank(pct=True, ascending=False)
        fundamentals["pb_rank"] = fundamentals.groupby("date")["pb"].rank(pct=True, ascending=False)
        return fundamentals

    def build(self, start: str, end: str) -> pd.DataFrame:
        # Query raw_prices and fundamentals, apply PIT lags, compute features
        # Phase 1 minimal implementation
        query = """
            SELECT ticker, date, adjusted_close, volume
            FROM raw_prices
            WHERE date BETWEEN ? AND ?
            ORDER BY ticker, date
        """
        prices = self.db.conn.execute(query, [start, end]).fetchdf()
        prices = self._momentum_12_1(prices)
        # Add placeholder columns for other features
        prices["pe_rank"] = 0.0
        prices["pb_rank"] = 0.0
        prices["quality_score"] = 0.0
        prices["low_vol_score"] = 0.0
        prices["insider_score"] = 0.0
        prices["macro_regime"] = "Risk-On"
        prices["available_at"] = prices["date"] + pd.Timedelta(days=1)
        return prices[[
            "ticker", "date", "mom_12_1", "pe_rank", "pb_rank",
            "quality_score", "low_vol_score", "insider_score", "macro_regime", "available_at"
        ]]
