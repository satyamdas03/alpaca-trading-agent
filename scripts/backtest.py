#!/usr/bin/env python3
"""Walk-forward backtest CLI.

Pulls historical data from Alpaca, runs the Bull strategy through
walk-forward validation, and outputs performance metrics.

Usage:
    python scripts/backtest.py --years 10 --tickers SPY,XLU,XLV,XLE --output results/
    python scripts/backtest.py --years 1 --tickers SPY  # quick smoke test
    python scripts/backtest.py --data-dir data/historical --tickers SPY,XLU  # offline mode
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd

from src.data.alpaca_fetcher import AlpacaFetcher
from src.data.edgar_fetcher import EdgarFetcher
from src.data.finra_fetcher import FinraFetcher
from src.strategy.bull_strategy import BullStrategy
from src.backtest.runner import WalkForwardConfig, run_backtest
from src.backtest.report import print_report, save_csv


def fetch_historical_data(tickers: list[str], years: int, cache_dir: Path):
    """Fetch historical price data for all tickers via Alpaca SDK."""
    alpaca = AlpacaFetcher(cache_dir / "bars", ttl_hours=24 * 365)
    edgar = EdgarFetcher(cache_dir / "fundamentals", ttl_hours=2160)
    finra = FinraFetcher(cache_dir / "darkpool", ttl_hours=672)

    start_date = f"{2026 - years}-01-01"
    end_date = "2026-04-22"

    price_data = {}
    fundamentals = {}
    dark_pool = {}

    for ticker in tickers:
        print(f"  Fetching {ticker} bars ({start_date} to {end_date})...")
        try:
            df = alpaca.fetch_bars_batch(ticker, start_date, end_date)
            if df.empty:
                print(f"  WARNING: No data for {ticker}, skipping")
                continue
            print(f"  Got {len(df)} bars for {ticker}")
            price_data[ticker] = df
        except Exception as e:
            print(f"  WARNING: Failed to fetch {ticker}: {e}")
            continue

        try:
            fund = edgar.fetch_fundamentals(ticker)
            if fund:
                fundamentals[ticker] = fund
        except Exception:
            pass

        try:
            dp = finra.fetch_dark_pool(ticker)
            if dp:
                dark_pool[ticker] = dp
        except Exception:
            pass

    return price_data, fundamentals, dark_pool


def load_offline_data(tickers: list[str], data_dir: Path, cache_dir: Path):
    """Load pre-saved historical data from a directory."""
    alpaca = AlpacaFetcher(cache_dir / "bars", ttl_hours=24 * 365)
    edgar = EdgarFetcher(cache_dir / "fundamentals", ttl_hours=2160)

    price_data = {}
    fundamentals = {}

    for ticker in tickers:
        print(f"  Loading {ticker} from {data_dir}...")
        df = alpaca.load_from_directory(data_dir, ticker)
        if df.empty:
            print(f"  WARNING: No offline data for {ticker}, skipping")
            continue
        print(f"  Got {len(df)} bars for {ticker}")
        price_data[ticker] = df

        try:
            fund = edgar.fetch_fundamentals(ticker)
            if fund:
                fundamentals[ticker] = fund
        except Exception:
            pass

    return price_data, fundamentals, {}


def compute_benchmark(price_data: dict, benchmark_ticker: str = "SPY") -> float | None:
    """Compute buy-and-hold return for benchmark ticker."""
    if benchmark_ticker not in price_data:
        return None
    df = price_data[benchmark_ticker]
    if len(df) < 2 or "close" not in df.columns:
        return None
    return (df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]


def main():
    parser = argparse.ArgumentParser(description="Walk-forward backtest for Bull strategy")
    parser.add_argument("--years", type=int, default=10, help="Number of years to backtest")
    parser.add_argument("--tickers", type=str, default="SPY,XLU,XLV,XLE,AAPL,MSFT",
                        help="Comma-separated ticker list")
    parser.add_argument("--data-dir", type=str, default=None,
                        help="Directory with pre-saved parquet/CSV files (offline mode)")
    parser.add_argument("--output", type=str, default="results/backtest.csv",
                        help="Output CSV path")
    parser.add_argument("--capital", type=float, default=100_000, help="Initial capital")
    parser.add_argument("--train-bars", type=int, default=504, help="Training window (bars)")
    parser.add_argument("--test-bars", type=int, default=63, help="Test window (bars)")
    parser.add_argument("--embargo", type=int, default=5, help="Embargo bars between windows")
    parser.add_argument("--cost", type=float, default=0.001, help="Transaction cost (fraction)")
    parser.add_argument("--slippage", type=float, default=0.0005, help="Slippage (fraction)")
    args = parser.parse_args()

    tickers = [t.strip() for t in args.tickers.split(",")]
    cache_dir = project_root / "data" / "cache"

    print(f"\nBull Walk-Forward Backtest")
    print(f"  Period: {args.years} years")
    print(f"  Tickers: {tickers}")
    print(f"  Capital: ${args.capital:,.0f}")
    print(f"  Train/Test: {args.train_bars}/{args.test_bars} bars")
    if args.data_dir:
        print(f"  Mode: Offline (data-dir: {args.data_dir})")
    print()

    # Fetch or load data
    print("Loading historical data...")
    if args.data_dir:
        data_dir = Path(args.data_dir)
        price_data, fundamentals, dark_pool = load_offline_data(tickers, data_dir, cache_dir)
    else:
        price_data, fundamentals, dark_pool = fetch_historical_data(tickers, args.years, cache_dir)

    if not price_data:
        print("ERROR: No price data available.")
        print("  Tip: Use --data-dir to load pre-saved files, or set APCA_API_KEY_ID env var")
        sys.exit(1)

    print(f"\nRunning walk-forward backtest...")
    print(f"  Tickers with data: {list(price_data.keys())}")

    config = WalkForwardConfig(
        train_bars=args.train_bars,
        test_bars=args.test_bars,
        embargo_bars=args.embargo,
    )

    result = run_backtest(
        strategy_factory=lambda vix: BullStrategy(vix=vix),
        price_data=price_data,
        fundamentals=fundamentals,
        dark_pool=dark_pool,
        config=config,
        initial_capital=args.capital,
        transaction_cost=args.cost,
        slippage=args.slippage,
    )

    benchmark = compute_benchmark(price_data)

    print_report(result, benchmark_return=benchmark)

    output_path = project_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_csv(result, str(output_path))
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()