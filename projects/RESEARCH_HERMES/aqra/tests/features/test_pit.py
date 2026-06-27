import pandas as pd
from aqra.features.pit import PITGuard


def test_pit_guard_lags_fundamentals():
    guard = PITGuard()
    # Fundamental data announced on t should be available t+1 (skip weekend)
    assert guard.available_lag("fundamentals", pd.Timestamp("2024-01-05")) == pd.Timestamp("2024-01-08")
    # Prices available same day
    assert guard.available_lag("price", pd.Timestamp("2024-01-05")) == pd.Timestamp("2024-01-05")
