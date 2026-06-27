import pandas as pd
from typing import Iterator


def time_series_split(
    dates: pd.DatetimeIndex,
    n_splits: int = 5,
    purge_gap: int = 21,
    embargo_pct: float = 0.02,
) -> Iterator[tuple[pd.DatetimeIndex, pd.DatetimeIndex]]:
    """Purged k-fold split for time-series cross-validation.

    Splits the sorted date index into train/test blocks with a gap (purge)
    between them to prevent leakage.
    """
    dates = pd.to_datetime(dates).sort_values().drop_duplicates()
    n = len(dates)
    test_size = max(1, n // (n_splits + 1))
    embargo_size = max(0, int(test_size * embargo_pct))

    for i in range(n_splits):
        test_start = n - (i + 1) * test_size
        test_end = test_start + test_size
        train_end = max(0, test_start - purge_gap - embargo_size)
        if train_end <= 0:
            continue
        train_dates = dates[:train_end]
        test_dates = dates[test_start:test_end]
        yield train_dates, test_dates


def regime_split(
    dates: pd.DatetimeIndex,
    regimes: pd.Series,
    n_splits: int = 3,
) -> Iterator[tuple[pd.DatetimeIndex, pd.DatetimeIndex]]:
    """Split by regime: hold out the most recent block of each regime as test."""
    dates = pd.to_datetime(dates).sort_values()
    unique_regimes = regimes.dropna().unique()
    for regime in unique_regimes[:n_splits]:
        mask = regimes == regime
        regime_dates = dates[mask]
        if len(regime_dates) < 10:
            continue
        split_idx = int(len(regime_dates) * 0.8)
        yield regime_dates[:split_idx], regime_dates[split_idx:]
