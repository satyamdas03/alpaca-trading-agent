from unittest.mock import patch
from src.data.finra_fetcher import FinraFetcher

def test_fetch_dark_pool_returns_dict(tmp_path):
    fetcher = FinraFetcher(cache_dir=tmp_path)
    mock_data = {
        "as_of_date": "2024-04-01",
        "ats_volume": 5000000,
        "total_volume": 50000000,
        "ats_ratio": 0.10,
    }
    with patch.object(fetcher, "_fetch_from_finra", return_value=mock_data):
        result = fetcher.fetch_dark_pool("AAPL")
    assert isinstance(result, dict)
    assert "ats_ratio" in result

def test_staleness_decay(tmp_path):
    fetcher = FinraFetcher(cache_dir=tmp_path)
    weight = fetcher.staleness_decay(weeks_stale=2)
    assert weight == 0.5

def test_fully_stale(tmp_path):
    fetcher = FinraFetcher(cache_dir=tmp_path)
    weight = fetcher.staleness_decay(weeks_stale=4)
    assert weight == 0.0