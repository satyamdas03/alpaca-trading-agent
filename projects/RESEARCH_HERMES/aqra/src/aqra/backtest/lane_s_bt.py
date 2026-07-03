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

    def _daily_returns(self, start: str, end: str, holding_period: int) -> pd.DataFrame:
        # Extend end date so the trailing holding window has data for IC.
        query = """
            SELECT ticker, date, adjusted_close
            FROM raw_prices
            WHERE date BETWEEN ? AND ?
            ORDER BY ticker, date
        """
        end_dt = pd.Timestamp(end) + pd.Timedelta(days=2 * holding_period + 10)
        prices = self.db.conn.execute(query, [start, end_dt.strftime("%Y-%m-%d")]).fetchdf()
        prices = prices.sort_values(["ticker", "date"])
        prices["ret_1d"] = prices.groupby("ticker")["adjusted_close"].pct_change()
        return prices[["ticker", "date", "ret_1d"]].dropna()

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
        rets = self._daily_returns(start, end, holding_period)
        df = features.merge(rets, on=["ticker", "date"], how="inner")
        if df.empty:
            return {}
        return self.engine.run_single_signal(df, holding_period=holding_period, cost_bps=cost_bps)
