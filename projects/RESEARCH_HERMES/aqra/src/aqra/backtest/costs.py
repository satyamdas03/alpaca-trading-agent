def apply_costs(returns: list[float], bps_round_trip: float) -> list[float]:
    cost = bps_round_trip / 10000.0
    return [r - cost for r in returns]
