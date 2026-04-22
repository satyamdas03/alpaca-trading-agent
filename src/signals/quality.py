def _safe_div(num, denom):
    if denom is None or denom == 0 or num is None:
        return None
    return num / denom


def gross_margin_score(fundamentals: dict, threshold: float = 0.3) -> int:
    gm = _safe_div(fundamentals.get("gross_profit"), fundamentals.get("revenue"))
    if gm is None:
        return 0
    return 1 if gm > threshold else 0


def quality_score(fundamentals: dict, prev: dict | None = None) -> int:
    if not fundamentals:
        return 0
    if prev is None:
        prev = {}

    score = 0

    # 1. ROA > 0
    roa = _safe_div(fundamentals.get("net_income"), fundamentals.get("total_assets"))
    if roa is not None and roa > 0:
        score += 1

    # 2. Operating cash flow > 0 (proxy: net_income > 0)
    if fundamentals.get("net_income") and fundamentals["net_income"] > 0:
        score += 1

    # 3. ROA change > 0
    prev_roa = _safe_div(prev.get("net_income"), prev.get("total_assets"))
    if roa is not None and prev_roa is not None and roa > prev_roa:
        score += 1

    # 4. Accruals: ROA > cash-flow/assets ratio (simplified: net_income > 0 already counted)

    # 5. Leverage decreasing
    lev = _safe_div(fundamentals.get("total_liabilities"), fundamentals.get("total_assets"))
    prev_lev = _safe_div(prev.get("total_liabilities"), prev.get("total_assets"))
    if lev is not None and prev_lev is not None and lev < prev_lev:
        score += 1

    # 6. Current ratio increasing
    cr = _safe_div(fundamentals.get("current_assets"), fundamentals.get("current_liabilities"))
    prev_cr = _safe_div(prev.get("current_assets"), prev.get("current_liabilities"))
    if cr is not None and prev_cr is not None and cr > prev_cr:
        score += 1

    # 7. Gross margin > threshold
    score += gross_margin_score(fundamentals, threshold=0.3)

    # 8. Revenue growth
    rev = fundamentals.get("revenue")
    prev_rev = prev.get("revenue")
    if rev and prev_rev and rev > prev_rev:
        score += 1

    # 9. Gross margin improvement
    gm = _safe_div(fundamentals.get("gross_profit"), fundamentals.get("revenue"))
    prev_gm = _safe_div(prev.get("gross_profit"), prev.get("revenue"))
    if gm is not None and prev_gm is not None and gm > prev_gm:
        score += 1

    return score