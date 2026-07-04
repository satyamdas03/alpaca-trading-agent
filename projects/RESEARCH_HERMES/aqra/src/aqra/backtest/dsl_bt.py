"""Backtest runner for DSL candidates (generated or library-as-DSL)."""

import logging

import numpy as np
import pandas as pd

from aqra.backtest.engine import BacktestEngine
from aqra.backtest.universe_filter import membership_join
from aqra.signals.dsl import evaluate, features_for_lane

logger = logging.getLogger(__name__)

LANE_TABLES = {
    "S": ("lane_s_features",
          ["mom_12_1", "pe_rank", "pb_rank", "quality_score",
           "low_vol_score", "insider_score"]),
    "I": ("lane_i_features",
          ["overnight_gap", "volume_zscore", "news_sentiment_zscore",
           "earnings_surprise", "insider_event_score"]),
}


class DSLBacktest:
    """Evaluates a DSL AST into a signal and runs the cross-sectional engine."""

    def __init__(self, db):
        self.db = db
        self.engine = BacktestEngine()

    def _features(self, lane: str, start: str, end: str) -> pd.DataFrame:
        table, cols = LANE_TABLES[lane]
        col_sql = ", ".join(f"f.{c}" for c in cols)
        query = f"""
            SELECT f.ticker, f.date, {col_sql}
            FROM {table} f {membership_join(self.db, alias="f")}
            WHERE f.date BETWEEN ? AND ?
            ORDER BY f.ticker, f.date
        """
        return self.db.conn.execute(query, [start, end]).fetchdf()

    def _daily_returns(self, start: str, end: str, holding_period: int) -> pd.DataFrame:
        query = f"""
            SELECT p.ticker, p.date, p.adjusted_close
            FROM raw_prices p {membership_join(self.db)}
            WHERE p.date BETWEEN ? AND ?
            ORDER BY p.ticker, p.date
        """
        end_dt = pd.Timestamp(end) + pd.Timedelta(days=2 * holding_period + 10)
        prices = self.db.conn.execute(query, [start, end_dt.strftime("%Y-%m-%d")]).fetchdf()
        prices = prices.sort_values(["ticker", "date"])
        prices["ret_1d"] = prices.groupby("ticker")["adjusted_close"].pct_change()
        return prices[["ticker", "date", "ret_1d"]].dropna()

    @staticmethod
    def _signal_half_life(df: pd.DataFrame) -> float:
        """Half-life in days of the signal's cross-sectional rank persistence."""
        panel = df.pivot_table(index="date", columns="ticker", values="signal")
        ranks = panel.rank(axis=1, pct=True)
        rho = ranks.corrwith(ranks.shift(1), axis=1).mean()
        if not np.isfinite(rho) or rho <= 0 or rho >= 1:
            return 0.0
        return float(np.log(0.5) / np.log(rho))

    def run(self, cand, start: str, end: str, holding_period: int = 21,
            cost_bps: float = 10.0) -> dict:
        features = self._features(cand.lane, start, end)
        if features.empty:
            return {}
        features["signal"] = evaluate(cand.ast, features,
                                      features_for_lane(cand.lane))
        rets = self._daily_returns(start, end, holding_period)
        df = features.merge(rets, on=["ticker", "date"], how="inner")
        if df.empty or df["signal"].dropna().nunique() <= 1:
            return {}
        metrics = self.engine.run_single_signal(
            df, holding_period=holding_period, cost_bps=cost_bps)
        if metrics and cand.lane == "I":
            metrics["half_life"] = self._signal_half_life(df)
        return metrics
