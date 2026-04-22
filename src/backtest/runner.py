from dataclasses import dataclass


@dataclass
class WalkForwardConfig:
    train_bars: int = 504   # 2 years
    test_bars: int = 63      # 1 quarter
    embargo_bars: int = 5   # 1 week

    def count_windows(self, total_bars: int) -> int:
        if total_bars < self.train_bars + self.test_bars:
            return 0
        remaining = total_bars - self.train_bars
        windows = 0
        while remaining >= self.test_bars:
            windows += 1
            remaining -= self.test_bars + self.embargo_bars
        return windows

    def window_ranges(self, total_bars: int) -> list[tuple[int, int, int]]:
        """Return list of (train_start, train_end, test_end) tuples."""
        windows = []
        if total_bars < self.train_bars + self.test_bars:
            return windows
        pos = 0
        while pos + self.train_bars + self.test_bars <= total_bars:
            train_start = pos
            train_end = pos + self.train_bars
            test_end = train_end + self.test_bars
            windows.append((train_start, train_end, test_end))
            pos = test_end + self.embargo_bars
        return windows


def run_backtest(strategy, symbols: list[str], start_date: str, end_date: str,
                 config: WalkForwardConfig | None = None):
    """Run PyBroker walk-forward backtest. Returns test metrics only."""
    import pybroker
    config = config or WalkForwardConfig()
    pybroker_config = pybroker.Config(
        warmup=config.train_bars,
    )
    pybroker_strategy = pybroker.Strategy(
        pybroker.Alpaca(),
        start_date=start_date,
        end_date=end_date,
        config=pybroker_config,
    )
    exec_fn = strategy.pybroker_exec_fn()
    for symbol in symbols:
        pybroker_strategy.add_execution(exec_fn, [symbol])
    result = pybroker_strategy.backtest()
    return result