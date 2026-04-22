"""Value signal: P/E and P/B relative to sector average, inverted.

Lower P/E and P/B = better value score (0-1 scale).
Uses EDGAR fundamentals for earnings and book value, current price from market data.
"""

import numpy as np


def value_score(fundamentals: dict, current_price: float | None = None,
                sector_pe: float | None = None, sector_pb: float | None = None) -> float:
    """Compute value score from fundamentals and market data.

    Args:
        fundamentals: Dict from EdgarFetcher with revenue, net_income, total_assets, total_liabilities.
        current_price: Current stock price. If None, returns 0.5 (neutral).
        sector_pe: Sector average P/E for relative comparison. Defaults to 20.
        sector_pb: Sector average P/B for relative comparison. Defaults to 2.0.

    Returns:
        Float 0-1, where higher = better value (cheaper relative to sector).
    """
    if not fundamentals or current_price is None or current_price <= 0:
        return 0.5

    net_income = fundamentals.get("net_income")
    total_assets = fundamentals.get("total_assets")
    total_liabilities = fundamentals.get("total_liabilities")
    shares_outstanding = fundamentals.get("shares_outstanding")

    # Default sector averages if not provided
    if sector_pe is None:
        sector_pe = 20.0
    if sector_pb is None:
        sector_pb = 2.0

    pe_score = 0.5
    pb_score = 0.5

    # P/E calculation (need earnings and share count)
    if net_income and net_income > 0 and shares_outstanding and shares_outstanding > 0:
        eps = net_income / shares_outstanding
        if eps > 0:
            pe = current_price / eps
            # Lower P/E relative to sector = better value
            # Ratio < 1 means cheaper than sector
            pe_ratio = pe / sector_pe
            pe_score = _ratio_to_score(pe_ratio)
    elif net_income and net_income > 0:
        # Approximate: use earnings yield (E/P) as inverse P/E
        earnings_yield = net_income / (current_price * (total_assets or 1))
        if total_assets and total_assets > 0:
            market_cap_approx = current_price * (total_assets / 100)  # rough scaling
            pe_approx = market_cap_approx / net_income if net_income > 0 else None
            if pe_approx and pe_approx > 0:
                pe_ratio = pe_approx / sector_pe
                pe_score = _ratio_to_score(pe_ratio)

    # P/B calculation
    book_value = (total_assets or 0) - (total_liabilities or 0)
    if book_value and book_value > 0 and shares_outstanding and shares_outstanding > 0:
        book_per_share = book_value / shares_outstanding
        if book_per_share > 0:
            pb = current_price / book_per_share
            pb_ratio = pb / sector_pb
            pb_score = _ratio_to_score(pb_ratio)
    elif book_value and book_value > 0 and total_assets and total_assets > 0:
        # Approximate P/B using book value / total assets as proxy
        pb_approx = current_price / (book_value / (total_assets / current_price))
        if pb_approx > 0:
            pb_ratio = pb_approx / sector_pb
            pb_score = _ratio_to_score(pb_ratio)

    # Weight P/E and P/B equally
    return 0.5 * pe_score + 0.5 * pb_score


def _ratio_to_score(ratio: float) -> float:
    """Convert a price ratio (lower = better) to a 0-1 score.

    ratio < 0.5 → score 1.0 (very cheap)
    ratio = 1.0 → score 0.5 (fair value)
    ratio > 2.0 → score 0.0 (expensive)
    """
    if ratio <= 0:
        return 0.5
    # Linear mapping: ratio 0.5→1.0, ratio 1.0→0.5, ratio 2.0→0.0
    score = max(0.0, min(1.0, 1.5 - ratio))
    return score