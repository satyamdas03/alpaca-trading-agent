from aqra.live.monitor import PerformanceMonitor


def test_monitor_flags_coverage_break():
    mon = PerformanceMonitor()
    assert mon.should_retire({"coverage": 0.75, "drawdown": -0.05})
    assert not mon.should_retire({"coverage": 0.92, "drawdown": -0.05})
