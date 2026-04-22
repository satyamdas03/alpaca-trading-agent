"""Backtest simulation engine.

Core daily simulation loop that applies strategy signals to generate trades,
track positions, and compute portfolio returns. Uses the same signal/sizing
pipeline as the live trading path.
"""

import numpy as np
import pandas as pd

from src.sizing.kelly import half_kelly_size


class BacktestEngine:
    def __init__(self, initial_capital: float = 100_000,
                 transaction_cost: float = 0.001,
                 slippage: float = 0.0005,
                 max_position_pct: float = 0.10,
                 stop_loss_pct: float = 0.10,
                 take_profit_pct: float = 0.20,
                 trailing_stop_pct: float = 0.12,
                 cooldown_bars: int = 21):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.max_position_pct = max_position_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trailing_stop_pct = trailing_stop_pct
        self.cooldown_bars = cooldown_bars

    def simulate_window(
        self,
        strategy,
        price_data: dict[str, pd.DataFrame],
        fundamentals: dict[str, dict] | None = None,
        dark_pool: dict[str, dict] | None = None,
        train_bars: int = 0,
    ) -> tuple[list[float], list[dict]]:
        """Simulate one walk-forward test window.

        Args:
            strategy: BullStrategy instance with generate_signals().
            price_data: Dict of {ticker: DataFrame} with 'close' column.
                Includes train+test history; signals use trailing data,
                but trading only happens in the test period (after train_bars).
            fundamentals: Dict of {ticker: fundamentals dict}.
            dark_pool: Dict of {ticker: dark pool data dict}.
            train_bars: Number of leading bars that are training (no trading).

        Returns:
            Tuple of (daily_returns, trades) for the window.
        """
        if fundamentals is None:
            fundamentals = {}
        if dark_pool is None:
            dark_pool = {}

        tickers = list(price_data.keys())
        if not tickers:
            return [], []

        # Determine window length from first ticker
        ref_df = price_data[tickers[0]]
        n_days = len(ref_df)

        capital = self.initial_capital
        prev_equity = float(self.initial_capital)
        positions = {}  # {ticker: {"shares", "entry_price", "entry_day", "high_water"}}
        cooldowns = {}  # {ticker: day_idx when cooldown expires}
        daily_returns = []
        trades = []

        # Start from train_bars (skip training period), or day 1 if no train
        start_idx = max(train_bars, 1)

        for day_idx in range(start_idx, n_days):
            # Calculate current portfolio value
            portfolio_value = capital
            for ticker, pos in positions.items():
                if ticker in price_data and day_idx < len(price_data[ticker]):
                    current_price = price_data[ticker]["close"].iloc[day_idx]
                    portfolio_value += pos["shares"] * current_price

            # Update high-water marks and check exit conditions
            positions_to_close = []
            for ticker, pos in list(positions.items()):
                if ticker not in price_data or day_idx >= len(price_data[ticker]):
                    continue
                current_price = price_data[ticker]["close"].iloc[day_idx]
                pnl_pct = (current_price - pos["entry_price"]) / pos["entry_price"]

                # Update high-water mark
                if current_price > pos["high_water"]:
                    pos["high_water"] = current_price

                # Hard stop loss: -7% from entry
                if pnl_pct <= -self.stop_loss_pct:
                    positions_to_close.append((ticker, "stop_loss"))
                    continue

                # Trailing stop: -10% from high-water mark (locks in gains)
                trail_pct = (current_price - pos["high_water"]) / pos["high_water"]
                if pos["high_water"] > pos["entry_price"] and trail_pct <= -self.trailing_stop_pct:
                    positions_to_close.append((ticker, "trailing_stop"))
                    continue

                # Take profit: +15% from entry
                if pnl_pct >= self.take_profit_pct:
                    positions_to_close.append((ticker, "take_profit"))
                    continue

            # Execute exits
            for ticker, reason in positions_to_close:
                pos = positions.pop(ticker)
                if ticker in price_data and day_idx < len(price_data[ticker]):
                    exit_price = price_data[ticker]["close"].iloc[day_idx] * (1 - self.slippage)
                    proceeds = pos["shares"] * exit_price * (1 - self.transaction_cost)
                    pnl = proceeds - (pos["shares"] * pos["entry_price"])
                    capital += proceeds
                    # Set cooldown after stop loss to prevent re-entry into falling knife
                    if reason == "stop_loss":
                        cooldowns[ticker] = day_idx + self.cooldown_bars
                    trades.append({
                        "ticker": ticker,
                        "side": "sell",
                        "price": exit_price,
                        "shares": pos["shares"],
                        "pnl": pnl,
                        "reason": reason,
                    })

            # Generate signals for each ticker
            signal_scores = {}
            for ticker in tickers:
                if ticker not in price_data:
                    continue
                df = price_data[ticker]
                if len(df) < day_idx + 1:
                    continue

                current_price = df["close"].iloc[day_idx]
                fund = fundamentals.get(ticker, {})
                dp = dark_pool.get(ticker, {})

                signals = strategy.generate_signals(
                    prices=df.iloc[:day_idx + 1],
                    fundamentals=fund,
                    current_price=current_price,
                    dark_pool_data=dp,
                )
                signal_scores[ticker] = {
                    "composite": signals["composite"],
                    "momentum": signals.get("momentum", 0.5),
                    "low_vol": signals.get("low_vol", 0.5),
                    "price": current_price,
                }

            # Close positions with weak signals (composite < 0.35) or negative momentum
            for ticker in list(positions.keys()):
                if ticker in signal_scores:
                    scores = signal_scores[ticker]
                    if scores["composite"] < 0.35 or scores["momentum"] < 0.3:
                        pos = positions.pop(ticker)
                        if ticker in price_data and day_idx < len(price_data[ticker]):
                            exit_price = price_data[ticker]["close"].iloc[day_idx] * (1 - self.slippage)
                            proceeds = pos["shares"] * exit_price * (1 - self.transaction_cost)
                            pnl = proceeds - (pos["shares"] * pos["entry_price"])
                            capital += proceeds
                            trades.append({
                                "ticker": ticker,
                                "side": "sell",
                                "price": exit_price,
                                "shares": pos["shares"],
                                "pnl": pnl,
                                "reason": "weak_signal",
                            })

            # Generate target portfolio: buy if composite > 0.45 AND above 200-day MA
            target_positions = {}
            for ticker, scores in sorted(
                signal_scores.items(), key=lambda x: x[1]["composite"], reverse=True
            ):
                # Skip if already in position or in cooldown
                if ticker in positions:
                    continue
                if ticker in cooldowns and day_idx < cooldowns[ticker]:
                    continue
                # Trend filter: only buy when price > 200-day MA
                if ticker in price_data:
                    df = price_data[ticker]
                    if day_idx >= 200 and "close" in df.columns:
                        ma200 = df["close"].iloc[day_idx-200:day_idx].mean()
                        if scores["price"] < ma200:
                            continue
                # Momentum filter: only buy with positive momentum
                if scores.get("momentum", 0.5) < 0.4:
                    continue
                if scores["composite"] > 0.45:
                    approx_sharpe = scores["composite"] * 2 - 1
                    vol = max(0.01, 1.0 - scores["low_vol"])
                    size_pct = half_kelly_size(
                        sharpe=approx_sharpe,
                        volatility=vol,
                        max_fraction=self.max_position_pct,
                    )
                    if size_pct > 0.01:
                        target_positions[ticker] = size_pct

            # Execute new buys
            for ticker, size_pct in target_positions.items():
                if ticker in positions:
                    continue
                if ticker not in price_data:
                    continue
                current_price = price_data[ticker]["close"].iloc[day_idx]
                buy_price = current_price * (1 + self.slippage)
                dollar_amount = portfolio_value * size_pct
                shares = int(dollar_amount / buy_price)
                if shares <= 0:
                    continue
                cost = shares * buy_price * (1 + self.transaction_cost)
                if cost <= capital:
                    capital -= cost
                    positions[ticker] = {
                        "shares": shares,
                        "entry_price": buy_price,
                        "entry_day": day_idx,
                        "high_water": buy_price,
                    }
                    trades.append({
                        "ticker": ticker,
                        "side": "buy",
                        "price": buy_price,
                        "shares": shares,
                        "pnl": 0,
                        "reason": "signal",
                    })

            # Calculate daily return
            new_equity = capital
            for ticker, pos in positions.items():
                if ticker in price_data and day_idx < len(price_data[ticker]):
                    new_equity += pos["shares"] * price_data[ticker]["close"].iloc[day_idx]

            daily_ret = (new_equity - prev_equity) / prev_equity if prev_equity > 0 else 0.0
            prev_equity = new_equity

            daily_returns.append(daily_ret)

        return daily_returns, trades