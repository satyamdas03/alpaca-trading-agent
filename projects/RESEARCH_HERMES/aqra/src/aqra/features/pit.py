import pandas as pd


class PITGuard:
    """Enforce point-in-time availability rules for different data types."""

    LAGS = {
        "price": 0,
        "volume": 0,
        "technical": 0,
        "fundamentals": 1,  # next trading day
        "insider": 1,
        "macro": 1,
        "news": 0,
        "earnings": 0,  # announced after close, usable next open
    }

    def __init__(self, calendar: pd.DatetimeIndex | None = None):
        self.calendar = calendar

    def _advance_trading_day(self, ts: pd.Timestamp, lag_days: int) -> pd.Timestamp:
        """Add lag_days calendar days, then skip weekends for Phase 1 approximation."""
        result = ts.normalize() + pd.Timedelta(days=lag_days)
        while result.weekday() >= 5:  # Saturday=5, Sunday=6
            result += pd.Timedelta(days=1)
        return result

    def available_lag(self, data_type: str, as_of: pd.Timestamp) -> pd.Timestamp:
        lag_days = self.LAGS.get(data_type, 1)
        if lag_days == 0:
            return pd.Timestamp(as_of).normalize()
        return self._advance_trading_day(pd.Timestamp(as_of), lag_days)

    def lag_series(self, df: pd.DataFrame, data_type: str, date_col: str = "date") -> pd.DataFrame:
        """Shift each row's effective date forward by the data-type lag."""
        df = df.copy()
        lag_days = self.LAGS.get(data_type, 1)
        df[date_col] = pd.to_datetime(df[date_col])
        if lag_days == 0:
            df[date_col] = df[date_col].dt.normalize()
        else:
            df[date_col] = df[date_col].apply(lambda d: self._advance_trading_day(pd.Timestamp(d), lag_days))
        return df
