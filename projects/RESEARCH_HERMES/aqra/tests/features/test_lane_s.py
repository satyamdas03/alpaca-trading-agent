import pandas as pd
from aqra.features.lane_s import LaneSFeatureBuilder


def test_momentum_feature():
    builder = LaneSFeatureBuilder(None)  # pass None db for unit test
    prices = pd.DataFrame({
        "ticker": ["AAPL"] * 500,
        "date": pd.date_range("2023-01-01", periods=500, freq="B"),
        "adjusted_close": range(500),
    })
    df = builder._momentum_12_1(prices)
    assert "mom_12_1" in df.columns
    assert df["mom_12_1"].notna().any()
