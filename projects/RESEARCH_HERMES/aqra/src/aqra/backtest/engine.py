import numpy as np
import pandas as pd

from aqra.backtest.metrics import sharpe, max_drawdown, information_coefficient


class BacktestEngine:
    """Cross-sectional long-short backtest.

    Input frame columns: ticker, date, signal, ret_1d (close-to-close daily
    return realized ON that date).  Weights are set on each rebalance date
    from the cross-sectionally demeaned signal rank (dollar-neutral, gross
    exposure 1) and applied from the NEXT trading day onward.  Transaction
    costs are charged on turnover at each rebalance.
    """

    def run_single_signal(
        self,
        df: pd.DataFrame,
        holding_period: int = 21,
        cost_bps: float = 10.0,
    ) -> dict:
        sig = df.pivot_table(index="date", columns="ticker", values="signal")
        ret = df.pivot_table(index="date", columns="ticker", values="ret_1d")
        sig, ret = sig.align(ret, join="inner")
        if sig.empty or len(sig) < holding_period + 2:
            return {}

        dates = sig.index
        rebalance_dates = dates[::holding_period]

        # weights decided on rebalance date d, applied from d+1 until next rebal
        w_rebal = sig.loc[rebalance_dates]
        demeaned = w_rebal.sub(w_rebal.mean(axis=1), axis=0)
        gross = demeaned.abs().sum(axis=1).replace(0, np.nan)
        w_rebal = demeaned.div(gross, axis=0).fillna(0.0)

        # daily weight panel: forward-fill, then shift 1 day (applied next day)
        w_daily = w_rebal.reindex(dates).ffill().shift(1).fillna(0.0)

        pnl = (w_daily * ret.fillna(0.0)).sum(axis=1)

        # costs: turnover at each rebalance (charged on the day weights apply)
        turn = w_rebal.diff().abs().sum(axis=1)
        if len(w_rebal) > 0:
            turn.iloc[0] = w_rebal.iloc[0].abs().sum()
        cost_series = pd.Series(0.0, index=dates)
        applied = [d for d in rebalance_dates if d in cost_series.index]
        cost_series.loc[applied] = turn.reindex(applied).fillna(0.0) * cost_bps / 10000.0
        cost_series = cost_series.shift(1).fillna(0.0)

        daily = (pnl - cost_series).dropna()
        if daily.std() == 0 or daily.empty:
            return {}
        equity = (1 + daily).cumprod()

        # Non-overlapping IC: signal on rebalance date vs holding-period forward return
        fwd = ret.add(1).rolling(holding_period).apply(np.prod, raw=True).shift(
            -holding_period
        ) - 1
        ic_vals = []
        for d in rebalance_dates:
            if d not in fwd.index:
                continue
            s_row = sig.loc[d]
            f_row = fwd.loc[d]
            valid = s_row.notna() & f_row.notna()
            if valid.sum() >= 10 and s_row[valid].nunique() > 1:
                ic_vals.append(s_row[valid].corr(f_row[valid], method="spearman"))
        ic = float(np.nanmean(ic_vals)) if ic_vals else np.nan

        # annualized turnover: gross weight change per year
        ann_turnover = float(turn.sum() / max(len(dates) / 252.0, 1e-9))

        return {
            "sharpe": sharpe(daily),
            "ic": ic,
            "max_drawdown": max_drawdown(equity),
            "mean_return": daily.mean(),
            "volatility": daily.std(),
            "turnover": ann_turnover,
            "equity_curve": equity,
        }
