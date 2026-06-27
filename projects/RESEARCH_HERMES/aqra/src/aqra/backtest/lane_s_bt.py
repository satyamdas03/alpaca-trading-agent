import pandas as pd
from aqra.backtest.engine import BacktestEngine
from aqra.utils import rank_pct


class LaneSBacktest:
    """Backtest runner for Lane S (structural alpha) signal candidates."""

    def __init__(self, db):
        self.db = db
        self.engine = BacktestEngine()

    def _signal(self, df: pd.DataFrame, candidate_id: str) -> pd.Series:
        if candidate_id == "S_MOM_12_1":
            return rank_pct(df["mom_12_1"])
        if candidate_id == "S_VALUE":
            return rank_pct(df["pe_rank"] + df["pb_rank"])
        if candidate_id == "S_QUALITY":
            return rank_pct(df["quality_score"])
        return pd.Series(0.0, index=df.index)

    def _forward_returns(self, start: str, end: str, holding_period: int) -> pd.DataFrame:
        # Extend end date to capture forward returns for dates near the end.
        query = """
            SELECT ticker, date, close
            FROM raw_prices
            WHERE date BETWEEN ? AND ?
            ORDER BY ticker, date
        """
        end_dt = pd.Timestamp(end) + pd.Timedelta(days=holding_period + 5)
        prices = self.db.conn.execute(query, [start, end_dt.strftime("%Y-%m-%d")]).fetchdf()
        prices = prices.sort_values(["ticker", "date"])
        prices["forward_return"] = prices.groupby("ticker")["close"].transform(
            lambda x: x.shift(-holding_period) / x - 1
        )
        return prices[["ticker", "date", "forward_return"]].dropna()

    def run(self, signal_candidate, start: str, end: str, holding_period: int = 21, cost_bps: float = 10.0) -> dict:
        query = """
            SELECT ticker, date, mom_12_1, pe_rank, pb_rank, quality_score,
                   low_vol_score, insider_score, macro_regime
            FROM lane_s_features
            WHERE date BETWEEN ? AND ?
            ORDER BY ticker, date
        """
        features = self.db.conn.execute(query, [start, end]).fetchdf()
        if features.empty:
            return {}
        features["signal"] = self._signal(features, signal_candidate.id)
        fwd = self._forward_returns(start, end, holding_period)
        df = features.merge(fwd, on=["ticker", "date"], how="inner")
        if df.empty:
            return {}
        return self.engine.run_single_signal(df, holding_period=holding_period, cost_bps=cost_bps)
