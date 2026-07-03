import numpy as np
import pandas as pd

from aqra.features.pit import PITGuard


class LaneSFeatureBuilder:
    """Structural-alpha features: 12-1 momentum, value (P/E, P/B), quality
    (TTM gross margin), low-volatility — built from raw_prices plus the EDGAR
    fundamentals table when it exists (real data), placeholders otherwise.
    """

    def __init__(self, db):
        self.db = db
        self.guard = PITGuard()

    def _momentum_12_1(self, prices: pd.DataFrame) -> pd.DataFrame:
        prices = prices.sort_values(["ticker", "date"])
        prices["mom_12_1"] = prices.groupby("ticker")["adjusted_close"].transform(
            lambda x: x.shift(21) / x.shift(252) - 1
        )
        return prices

    def _low_vol(self, prices: pd.DataFrame, window: int = 60) -> pd.DataFrame:
        prices = prices.sort_values(["ticker", "date"])
        rets = prices.groupby("ticker")["adjusted_close"].pct_change()
        prices["vol_60d"] = rets.groupby(prices["ticker"]).transform(
            lambda x: x.shift(1).rolling(window).std()
        )
        return prices

    def _fundamentals_ttm(self) -> pd.DataFrame:
        """TTM fundamentals per ticker with point-in-time availability."""
        tables = {r[0] for r in self.db.conn.execute("SHOW TABLES").fetchall()}
        if "fundamentals" not in tables:
            return pd.DataFrame()
        f = self.db.conn.execute("""
            SELECT ticker, period_end, available_at,
                   eps_dil, equity, gross_profit, revenues, shares_out
            FROM fundamentals
            ORDER BY ticker, period_end
        """).fetchdf()
        if f.empty:
            return f
        f["period_end"] = pd.to_datetime(f["period_end"])
        f["available_at"] = pd.to_datetime(f["available_at"])
        g = f.groupby("ticker")
        f["eps_ttm"] = g["eps_dil"].transform(lambda x: x.rolling(4, min_periods=4).sum())
        f["gp_ttm"] = g["gross_profit"].transform(lambda x: x.rolling(4, min_periods=4).sum())
        f["rev_ttm"] = g["revenues"].transform(lambda x: x.rolling(4, min_periods=4).sum())
        f["bvps"] = f["equity"] / f["shares_out"].replace(0, np.nan)
        f["gross_margin_ttm"] = f["gp_ttm"] / f["rev_ttm"].replace(0, np.nan)
        return f[["ticker", "available_at", "eps_ttm", "bvps", "gross_margin_ttm"]].dropna(
            subset=["available_at"]
        )

    def _asof_join_fundamentals(self, prices: pd.DataFrame,
                                fund: pd.DataFrame) -> pd.DataFrame:
        """Attach the latest fundamentals with available_at <= date per ticker."""
        prices = prices.sort_values("date")
        fund = fund.sort_values("available_at")
        joined = pd.merge_asof(
            prices,
            fund,
            left_on="date",
            right_on="available_at",
            by="ticker",
            direction="backward",
        )
        return joined

    def build(self, start: str, end: str) -> pd.DataFrame:
        query = """
            SELECT ticker, date, adjusted_close, volume
            FROM raw_prices
            WHERE date BETWEEN ? AND ?
            ORDER BY ticker, date
        """
        prices = self.db.conn.execute(query, [start, end]).fetchdf()
        prices["date"] = pd.to_datetime(prices["date"])
        prices = self._momentum_12_1(prices)
        prices = self._low_vol(prices)

        fund = self._fundamentals_ttm()
        if not fund.empty:
            prices = self._asof_join_fundamentals(prices, fund)
            pe = prices["adjusted_close"] / prices["eps_ttm"]
            pe[prices["eps_ttm"] <= 0] = np.nan  # negative earnings: no P/E
            pb = prices["adjusted_close"] / prices["bvps"]
            pb[prices["bvps"] <= 0] = np.nan
            # Cross-sectional daily ranks. ascending=False: cheap (low P/E, low
            # P/B) -> high pct, so S_VALUE = rank(pe_rank + pb_rank) is long-cheap.
            prices["pe_rank"] = pe.groupby(prices["date"]).rank(pct=True, ascending=False)
            prices["pb_rank"] = pb.groupby(prices["date"]).rank(pct=True, ascending=False)
            prices["quality_score"] = prices.groupby("date")["gross_margin_ttm"].rank(pct=True)
        else:
            prices["pe_rank"] = 0.0
            prices["pb_rank"] = 0.0
            prices["quality_score"] = 0.0

        prices["low_vol_score"] = prices.groupby("date")["vol_60d"].rank(
            pct=True, ascending=False
        )
        prices["insider_score"] = 0.0
        prices["macro_regime"] = "Risk-On"
        prices["available_at"] = prices["date"] + pd.Timedelta(days=1)
        return prices[[
            "ticker", "date", "mom_12_1", "pe_rank", "pb_rank",
            "quality_score", "low_vol_score", "insider_score", "macro_regime", "available_at"
        ]]
