import pandas as pd
from aqra.features.lane_i import LaneIFeatureBuilder


def test_overnight_gap():
    builder = LaneIFeatureBuilder(None)
    prices = pd.DataFrame({
        "ticker": ["AAPL"] * 10,
        "date": pd.date_range("2024-01-01", periods=10, freq="B"),
        "open": [100.0] * 10,
        "adjusted_close": [99.0, 101.0, 100.0, 102.0, 100.0, 103.0, 100.0, 104.0, 100.0, 105.0],
    })
    df = builder._overnight_gap(prices)
    assert "overnight_gap" in df.columns
    assert df["overnight_gap"].notna().any()
