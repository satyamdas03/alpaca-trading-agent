from unittest.mock import patch, MagicMock
from src.data.edgar_fetcher import EdgarFetcher

def test_fetch_fundamentals_returns_dict(tmp_path):
    fetcher = EdgarFetcher(cache_dir=tmp_path)
    mock_financials = {
        "revenue": 394328000000,
        "gross_profit": 170782000000,
        "net_income": 99803000000,
        "total_assets": 352583000000,
        "total_liabilities": 290437000000,
        "current_assets": 134973000000,
        "current_liabilities": 108829000000,
    }
    with patch.object(fetcher, "_fetch_from_edgar", return_value=mock_financials):
        result = fetcher.fetch_fundamentals("AAPL")
    assert isinstance(result, dict)
    assert "revenue" in result
    assert result["revenue"] == 394328000000

def test_fetch_fundamentals_handles_missing_filing(tmp_path):
    fetcher = EdgarFetcher(cache_dir=tmp_path)
    with patch.object(fetcher, "_fetch_from_edgar", side_effect=Exception("Company not found")):
        result = fetcher.fetch_fundamentals("FAKE")
    assert result == {}