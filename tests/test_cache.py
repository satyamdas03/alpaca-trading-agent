import json
import time
import tempfile
from pathlib import Path
from src.data.cache import Cache

def test_cache_returns_fresh_parquet(tmp_path):
    cache = Cache(tmp_path, ttl_hours=24)
    df_data = {"date": ["2024-01-01"], "close": [100.0]}
    import pandas as pd
    df = pd.DataFrame(df_data)
    cache.write_parquet("SPY", df)
    result = cache.read_parquet("SPY")
    assert result is not None
    assert result["close"].iloc[0] == 100.0

def test_cache_returns_none_for_missing(tmp_path):
    cache = Cache(tmp_path, ttl_hours=24)
    result = cache.read_parquet("NONEXISTENT")
    assert result is None

def test_cache_returns_none_for_stale(tmp_path):
    cache = Cache(tmp_path, ttl_hours=0)
    import pandas as pd
    df = pd.DataFrame({"date": ["2024-01-01"], "close": [100.0]})
    cache.write_parquet("STALE", df)
    stale_path = tmp_path / "STALE.parquet"
    import os
    atime = time.time() - 86400 * 2
    os.utime(stale_path, (atime, atime))
    result = cache.read_parquet("STALE")
    assert result is None

def test_cache_json_roundtrip(tmp_path):
    cache = Cache(tmp_path, ttl_hours=168)
    data = {"revenue": 100000, "gross_margin": 0.45}
    cache.write_json("AAPL", data)
    result = cache.read_json("AAPL")
    assert result == data