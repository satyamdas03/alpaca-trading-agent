"""Sentiment signal: dark pool flow and staleness-adjusted scoring.

Uses FINRA ATS data (dark pool volume ratio) as a sentiment proxy.
High ATS ratio = institutional activity → can be bullish or bearish depending on context.
Staleness decay reduces signal weight when data is old.
"""

from datetime import datetime, date
from src.data.finra_fetcher import FinraFetcher


def sentiment_score(dark_pool_data: dict, max_weeks_stale: float = 4.0) -> float:
    """Compute sentiment score from dark pool data.

    Args:
        dark_pool_data: Dict from FinraFetcher.fetch_dark_pool().
            Expected keys: ats_ratio, as_of_date, ats_volume, total_volume.
        max_weeks_stale: Weeks before data decays to zero weight.

    Returns:
        Float 0-1, where higher = more positive sentiment.
        Returns 0.5 (neutral) if no data available.
    """
    if not dark_pool_data:
        return 0.5

    ats_ratio = dark_pool_data.get("ats_ratio", 0)
    as_of_date = dark_pool_data.get("as_of_date", "")

    # Staleness decay
    staleness = _compute_staleness(as_of_date, max_weeks_stale)
    if staleness <= 0:
        return 0.5

    # ATS ratio interpretation:
    # High ATS ratio (>0.3) = heavy institutional dark pool activity
    # Moderate ATS ratio (0.1-0.3) = normal activity
    # Low ATS ratio (<0.1) = low institutional participation
    # We treat high institutional activity as slightly bullish (informed flow)
    # but with diminishing returns
    raw_score = _ats_ratio_to_score(ats_ratio)

    # Apply staleness decay
    return raw_score * staleness + 0.5 * (1 - staleness)


def _compute_staleness(as_of_date: str, max_weeks: float) -> float:
    """Compute staleness factor: 1.0 when fresh, 0.0 when max_weeks old."""
    if not as_of_date:
        return 0.0
    try:
        data_date = datetime.strptime(as_of_date[:10], "%Y-%m-%d").date()
    except (ValueError, IndexError):
        return 0.0
    weeks_stale = (date.today() - data_date).days / 7.0
    return max(0.0, 1.0 - weeks_stale / max_weeks)


def _ats_ratio_to_score(ratio: float) -> float:
    """Convert ATS ratio to a 0-1 sentiment score.

    Very low (<0.05) → 0.3 (low participation, slightly bearish)
    Low (0.05-0.15) → 0.5 (normal)
    Medium (0.15-0.30) → 0.7 (above average institutional interest)
    High (>0.30) → 0.8 (heavy institutional flow, bullish bias)
    """
    if ratio <= 0:
        return 0.3
    if ratio < 0.05:
        return 0.3 + ratio * 4.0  # 0 to 0.5
    if ratio < 0.15:
        return 0.5 + (ratio - 0.05) * 2.0  # 0.5 to 0.7
    if ratio < 0.30:
        return 0.7 + (ratio - 0.15) * 0.67  # 0.7 to 0.8
    return min(0.9, 0.8 + (ratio - 0.30) * 0.5)  # 0.8 to 0.9