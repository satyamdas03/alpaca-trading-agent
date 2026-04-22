from src.backtest.runner import WalkForwardConfig

def test_walkforward_config_defaults():
    config = WalkForwardConfig()
    assert config.train_bars == 504
    assert config.test_bars == 63
    assert config.embargo_bars == 5

def test_walkforward_config_custom():
    config = WalkForwardConfig(train_bars=252, test_bars=21, embargo_bars=3)
    assert config.train_bars == 252
    assert config.test_bars == 21

def test_count_windows():
    config = WalkForwardConfig(train_bars=504, test_bars=63, embargo_bars=5)
    total_bars = 504 + 63 + 5 + 63 + 5 + 63
    windows = config.count_windows(total_bars)
    assert windows == 3

def test_count_windows_insufficient():
    config = WalkForwardConfig(train_bars=504, test_bars=63, embargo_bars=5)
    windows = config.count_windows(500)
    assert windows == 0