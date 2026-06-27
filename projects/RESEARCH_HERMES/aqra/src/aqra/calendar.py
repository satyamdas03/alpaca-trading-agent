import pandas as pd


def is_trading_day(date: pd.Timestamp, calendar: pd.DatetimeIndex | None = None) -> bool:
    """Return True if date is a trading day. Uses provided calendar or defaults to NYSE via pandas."""
    if calendar is not None:
        return date.normalize() in calendar
    # Fallback: Monday-Friday, not common US holidays (approximate)
    return date.weekday() < 5


def trading_days_between(start: pd.Timestamp, end: pd.Timestamp, calendar: pd.DatetimeIndex) -> int:
    return len(calendar[(calendar >= start) & (calendar <= end)])
