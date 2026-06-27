import pandas as pd
from aqra.backtest.metrics import sharpe, max_drawdown, information_coefficient
from aqra.backtest.costs import apply_costs


class BacktestEngine:
    def run_single_signal(
        self,
        df: pd.DataFrame,
        holding_period: int = 21,
        cost_bps: float = 10.0,
    ) -> dict:
        df = df.sort_values(["ticker", "date"]).copy()
        df["position"] = df.groupby("ticker")["signal"].shift(1)
        df["strategy_return"] = df["position"] * df["forward_return"]
        # Aggregate to portfolio (equal-weight within day)
        daily = df.groupby("date")["strategy_return"].mean().dropna()
        daily_after_cost = pd.Series(apply_costs(daily.tolist(), cost_bps), index=daily.index)
        equity = (1 + daily_after_cost).cumprod()
        return {
            "sharpe": sharpe(daily_after_cost),
            "ic": information_coefficient(df["signal"], df["forward_return"]),
            "max_drawdown": max_drawdown(equity),
            "mean_return": daily_after_cost.mean(),
            "volatility": daily_after_cost.std(),
            "equity_curve": equity,
        }
