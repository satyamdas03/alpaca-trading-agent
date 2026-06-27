from aqra.constants import CONFORMAL_COVERAGE_TARGET


class PerformanceMonitor:
    def should_retire(self, stats: dict) -> bool:
        if stats.get("coverage", 1.0) < CONFORMAL_COVERAGE_TARGET - 0.10:
            return True
        if stats.get("drawdown", 0) < -0.20:
            return True
        if stats.get("half_life", 99) < 1.0:
            return True
        return False
