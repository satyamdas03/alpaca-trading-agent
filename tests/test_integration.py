import pandas as pd
import json
from pathlib import Path
from src.data.cache import Cache
from src.signals.quality import quality_score
from src.signals.momentum import momentum_score
from src.signals.regime import classify_regime, Regime
from src.strategy.bull_strategy import BullStrategy
from src.backtest.runner import WalkForwardConfig
from src.backtest.metrics import sharpe_ratio, max_drawdown, bootstrap_ci

FIXTURES = Path(__file__).parent / "fixtures"

def test_full_pipeline_smoke():
    """Smoke test: SPY data -> signals -> strategy -> metrics in <60s."""
    prices = pd.read_parquet(FIXTURES / "spy_2yr.parquet")
    with open(FIXTURES / "fundamentals_5companies.json") as f:
        all_fundamentals = json.load(f)

    # 1. Generate signals
    strategy = BullStrategy(vix=18.0)
    signals = strategy.generate_signals(prices, all_fundamentals.get("AAPL"))

    # 2. Verify signal structure
    assert "composite" in signals
    assert 0 <= signals["composite"] <= 1

    # 3. Walk-forward config
    config = WalkForwardConfig()
    assert config.count_windows(len(prices)) >= 0

    # 4. Metrics on synthetic returns
    returns = prices["close"].pct_change().dropna().values
    s = sharpe_ratio(returns)
    dd = max_drawdown(prices["close"].values)
    assert isinstance(s, float)
    assert 0 < dd < 1

    # 5. Bootstrap CI
    lo, hi = bootstrap_ci(returns, n_samples=50)
    assert lo < hi