import pandas as pd
import numpy as np
import json
from pathlib import Path

np.random.seed(42)

# SPY 2yr price bars
n = 504
dates = pd.bdate_range("2022-01-03", periods=n)
close = 400 + np.cumsum(np.random.randn(n) * 2)
prices = pd.DataFrame({
    "date": dates,
    "open": close - np.random.uniform(0, 2, n),
    "high": close + np.random.uniform(0, 3, n),
    "low": close - np.random.uniform(0, 3, n),
    "close": close,
    "volume": np.random.randint(50000000, 150000000, n),
})
prices.to_parquet("tests/fixtures/spy_2yr.parquet", index=False)

# 5 company fundamentals
fundamentals = {
    "AAPL": {"revenue": 394328, "gross_profit": 170782, "net_income": 99803,
             "total_assets": 352583, "total_liabilities": 290437,
             "current_assets": 134973, "current_liabilities": 108829},
    "MSFT": {"revenue": 211915, "gross_profit": 147518, "net_income": 72361,
             "total_assets": 411976, "total_liabilities": 191791,
             "current_assets": 169684, "current_liabilities": 95082},
    "GOOG": {"revenue": 307394, "gross_profit": 156633, "net_income": 73795,
             "total_assets": 365764, "total_liabilities": 119098,
             "current_assets": 152655, "current_liabilities": 84526},
    "TSLA": {"revenue": 96773, "gross_profit": 17699, "net_income": 14997,
             "total_assets": 106158, "total_liabilities": 53913,
             "current_assets": 43787, "current_liabilities": 32215},
    "AMZN": {"revenue": 574785, "gross_profit": 246695, "net_income": 30425,
             "total_assets": 420548, "total_liabilities": 324243,
             "current_assets": 172749, "current_liabilities": 189567},
}
with open("tests/fixtures/fundamentals_5companies.json", "w") as f:
    json.dump(fundamentals, f, indent=2)

# Regime history
regime = pd.DataFrame({
    "date": pd.bdate_range("2022-01-03", periods=n),
    "vix": np.random.uniform(15, 35, n),
})
regime.to_csv("tests/fixtures/regime_history.csv", index=False)

print("Fixtures generated.")