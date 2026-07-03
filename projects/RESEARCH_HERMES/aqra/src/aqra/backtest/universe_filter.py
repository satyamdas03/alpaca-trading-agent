"""Point-in-time universe membership filter for backtest queries."""


def membership_join(db, alias: str = "p") -> str:
    """SQL JOIN clause restricting rows to in-universe (ticker, date) pairs.

    Returns an empty string when the universe_membership table is empty so
    synthetic-data tests and pre-Phase-1b databases keep working unfiltered.
    end_date is exclusive.
    """
    n = db.conn.execute("SELECT COUNT(*) FROM universe_membership").fetchone()[0]
    if n == 0:
        return ""
    return (
        f"JOIN universe_membership um ON {alias}.ticker = um.ticker "
        f"AND {alias}.date >= um.start_date AND {alias}.date < um.end_date"
    )
