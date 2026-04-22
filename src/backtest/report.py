"""Backtest results reporting.

Generates summary tables and CSV output from BacktestResult.
"""

import pandas as pd
from src.backtest.runner import BacktestResult


def print_report(result: BacktestResult, benchmark_return: float | None = None):
    """Print a formatted backtest results table to console."""
    print("\n" + "=" * 60)
    print("  WALK-FORWARD BACKTEST RESULTS")
    print("=" * 60)
    print(f"  Total Return:      {result.total_return:>10.2%}")
    print(f"  CAGR:              {result.cagr:>10.2%}")
    print(f"  Sharpe Ratio:      {result.sharpe:>10.2f}")
    print(f"  Max Drawdown:      {result.max_dd:>10.2%}")
    print(f"  Win Rate:          {result.win_rate:>10.2%}")
    print(f"  Num Trades:        {result.num_trades:>10d}")
    print(f"  Sharpe 95% CI:     [{result.sharpe_ci[0]:.2f}, {result.sharpe_ci[1]:.2f}]")
    print(f"  Strategy Valid:    {'YES' if result.strategy_valid else 'NO':>10}")

    if benchmark_return is not None:
        alpha = result.total_return - benchmark_return
        print(f"  Benchmark Return:  {benchmark_return:>10.2%}")
        print(f"  Alpha:             {alpha:>10.2%}")

    print("\n  Regime Breakdown:")
    for regime, sharpe in result.regime_sharpes.items():
        print(f"    {regime:<15} Sharpe: {sharpe:.2f}")

    print("=" * 60 + "\n")


def save_csv(result: BacktestResult, output_path: str):
    """Save backtest results to CSV files."""
    # Save equity curve
    eq_df = pd.DataFrame({
        "day": range(len(result.equity_curve)),
        "equity": result.equity_curve.values,
        "daily_return": result.daily_returns.values,
    })
    eq_path = output_path.replace(".csv", "_equity.csv")
    eq_df.to_csv(eq_path, index=False)

    # Save trade log
    if result.trades:
        trades_df = pd.DataFrame(result.trades)
        tr_path = output_path.replace(".csv", "_trades.csv")
        trades_df.to_csv(tr_path, index=False)

    # Save summary
    summary = {
        "total_return": result.total_return,
        "cagr": result.cagr,
        "sharpe": result.sharpe,
        "max_drawdown": result.max_dd,
        "win_rate": result.win_rate,
        "num_trades": result.num_trades,
        "strategy_valid": result.strategy_valid,
        "sharpe_ci_lo": result.sharpe_ci[0],
        "sharpe_ci_hi": result.sharpe_ci[1],
    }
    for regime, sharpe in result.regime_sharpes.items():
        summary[f"sharpe_{regime}"] = sharpe
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(output_path, index=False)