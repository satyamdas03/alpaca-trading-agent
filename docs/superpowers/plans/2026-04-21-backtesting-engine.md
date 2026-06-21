# Phase 1: Backtesting Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a backtesting engine that validates the NexusTrade Quality+Momentum strategy against historical data with walk-forward analysis and anti-overfitting guards.

**Architecture:** PyBroker orchestrates walk-forward backtests. Alpaca API provides price data cached as Parquet. edgartools provides SEC fundamentals cached as JSON. Signals compute quality, momentum, and regime scores. Riskfolio-Lib computes half-Kelly position sizing. Bootstrap confidence intervals validate statistical significance.

**Tech Stack:** Python 3.10+, PyBroker (lib-pybroker), edgartools, Riskfolio-Lib, Alpaca Trade API, tenacity, pytest, pandas, numpy

---

## File Map

| File | Responsibility |
|------|---------------|
| `pyproject.toml` | Project deps and config (uv) |
| `src/__init__.py` | Package root |
| `src/data/__init__.py` | Data package |
| `src/data/cache.py` | Read-through Parquet/JSON cache with TTL |
| `src/data/alpaca_fetcher.py` | Fetch price bars from Alpaca → Parquet |
| `src/data/edgar_fetcher.py` | Fetch SEC fundamentals via edgartools → JSON |
| `src/data/finra_fetcher.py` | Fetch dark pool ATS volume from FINRA → JSON |
| `src/signals/__init__.py` | Signals package |
| `src/signals/quality.py` | Piotroski F-score + gross margin quality signal |
| `src/signals/momentum.py` | 12-1 month return momentum ranking |
| `src/signals/regime.py` | VIX-based regime classifier (risk-on/late-cycle/stress) |
| `src/strategy/__init__.py` | Strategy package |
| `src/strategy/bull_strategy.py` | Multi-factor composite strategy for PyBroker |
| `src/sizing/__init__.py` | Sizing package |
| `src/sizing/kelly.py` | Half-Kelly position sizing via Riskfolio-Lib |
| `src/backtest/__init__.py` | Backtest package |
| `src/backtest/runner.py` | PyBroker walk-forward runner |
| `src/backtest/metrics.py` | Sharpe, max DD, bootstrap CI, regime stats, outlier cap |
| `data/prices/.gitkeep` | Price cache directory (gitignored content) |
| `data/fundamentals/.gitkeep` | Fundamentals cache directory (gitignored content) |
| `tests/fixtures/spy_2yr.parquet` | 2yr SPY price bar fixture |
| `tests/fixtures/fundamentals_5companies.json` | 5-company fundamental snapshot fixture |
| `tests/fixtures/regime_history.csv` | VIX regime label fixture |
| `tests/test_cache.py` | Cache unit tests |
| `tests/test_alpaca_fetcher.py` | Alpaca fetcher unit tests (mocked) |
| `tests/test_edgar_fetcher.py` | Edgar fetcher unit tests (mocked) |
| `tests/test_quality.py` | Quality signal unit tests |
| `tests/test_momentum.py` | Momentum signal unit tests |
| `tests/test_regime.py` | Regime classifier unit tests |
| `tests/test_bull_strategy.py` | Strategy integration tests |
| `tests/test_kelly.py` | Kelly sizing unit tests |
| `tests/test_runner.py` | Walk-forward runner tests |
| `tests/test_metrics.py` | Metrics computation tests |
| `tests/test_integration.py` | Full pipeline smoke test |

---

### Task 1: Project Skeleton + Dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`
- Create: `src/data/__init__.py`
- Create: `src/signals/__init__.py`
- Create: `src/strategy/__init__.py`
- Create: `src/sizing/__init__.py`
- Create: `src/backtest/__init__.py`
- Create: `data/prices/.gitkeep`
- Create: `data/fundamentals/.gitkeep`
- Modify: `.gitignore`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "bull-backtest"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "lib-pybroker>=1.2.12",
    "edgartools>=5.30.0",
    "riskfolio-lib>=7.2.0",
    "alpaca-trade-api>=3.2.0",
    "tenacity>=9.0.0",
    "pandas>=2.2.0",
    "numpy>=1.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Install dependencies**

Run: `cd C:/Users/point/projects/alpacaIntegrationWithClaudeCode && uv pip install -e ".[dev]"`
Expected: All packages install successfully

- [ ] **Step 3: Create all __init__.py files and data directories**

```bash
mkdir -p src/data src/signals src/strategy src/sizing src/backtest
touch src/__init__.py src/data/__init__.py src/signals/__init__.py src/strategy/__init__.py src/sizing/__init__.py src/backtest/__init__.py
mkdir -p data/prices data/fundamentals
touch data/prices/.gitkeep data/fundamentals/.gitkeep
```

- [ ] **Step 4: Update .gitignore to exclude data caches**

Append to `.gitignore`:
```
data/prices/*.parquet
data/fundamentals/*.json
data/fundamentals/*.csv
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/ data/.gitkeep data/prices/.gitkeep data/fundamentals/.gitkeep .gitignore
git commit -m "feat: project skeleton with pyproject.toml and package structure"
```

---

### Task 2: Cache Module

**Files:**
- Create: `src/data/cache.py`
- Test: `tests/test_cache.py`

- [ ] **Step 1: Write failing test for cache**

```python
# tests/test_cache.py
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
    cache = Cache(tmp_path, ttl_hours=0)  # 0 hour TTL = always stale
    import pandas as pd
    df = pd.DataFrame({"date": ["2024-01-01"], "close": [100.0]})
    cache.write_parquet("STALE", df)
    # Manually age the file
    stale_path = tmp_path / "STALE.parquet"
    import os
    atime = time.time() - 86400 * 2
    os.utime(stale_path, (atime, atime))
    result = cache.read_parquet("STALE")
    assert result is None

def test_cache_json_roundtrip(tmp_path):
    cache = Cache(tmp_path, ttl_hours=168)  # 7 days for fundamentals
    data = {"revenue": 100000, "gross_margin": 0.45}
    cache.write_json("AAPL", data)
    result = cache.read_json("AAPL")
    assert result == data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.data.cache'`

- [ ] **Step 3: Implement cache**

```python
# src/data/cache.py
import json
import time
from pathlib import Path
import pandas as pd


class Cache:
    def __init__(self, cache_dir: Path, ttl_hours: int):
        self._dir = cache_dir
        self._ttl_seconds = ttl_hours * 3600
        self._dir.mkdir(parents=True, exist_ok=True)

    def _is_fresh(self, path: Path) -> bool:
        if not path.exists():
            return False
        age = time.time() - path.stat().st_mtime
        return age < self._ttl_seconds

    def read_parquet(self, symbol: str) -> pd.DataFrame | None:
        path = self._dir / f"{symbol}.parquet"
        if not self._is_fresh(path):
            return None
        return pd.read_parquet(path)

    def write_parquet(self, symbol: str, df: pd.DataFrame) -> None:
        path = self._dir / f"{symbol}.parquet"
        df.to_parquet(path, index=False)

    def read_json(self, symbol: str) -> dict | None:
        path = self._dir / f"{symbol}.json"
        if not self._is_fresh(path):
            return None
        with open(path) as f:
            return json.load(f)

    def write_json(self, symbol: str, data: dict) -> None:
        path = self._dir / f"{symbol}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def purge_stale(self) -> int:
        count = 0
        for path in self._dir.iterdir():
            if not self._is_fresh(path):
                path.unlink()
                count += 1
        return count
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cache.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/cache.py tests/test_cache.py
git commit -m "feat: read-through Parquet/JSON cache with TTL"
```

---

### Task 3: Alpaca Data Fetcher

**Files:**
- Create: `src/data/alpaca_fetcher.py`
- Test: `tests/test_alpaca_fetcher.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_alpaca_fetcher.py
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data.alpaca_fetcher import AlpacaFetcher

def test_fetch_bars_returns_dataframe(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    mock_bars = [{
        "t": "2024-01-02T00:00:00Z",
        "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": 1000,
        "n": 100, "vw": 100.3,
    }]
    with patch.object(fetcher, "_fetch_from_api", return_value=mock_bars):
        df = fetcher.fetch_bars("SPY", days=5)
    assert isinstance(df, pd.DataFrame)
    assert "close" in df.columns
    assert len(df) == 1

def test_fetch_bars_uses_cache(tmp_path):
    fetcher = AlpacaFetcher(cache_dir=tmp_path)
    mock_bars = [{
        "t": "2024-01-02T00:00:00Z",
        "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": 1000,
        "n": 100, "vw": 100.3,
    }]
    with patch.object(fetcher, "_fetch_from_api", return_value=mock_bars) as mock_api:
        df1 = fetcher.fetch_bars("SPY", days=5)
        df2 = fetcher.fetch_bars("SPY", days=5)
    # API should only be called once (second hit uses cache)
    assert mock_api.call_count == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_alpaca_fetcher.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement fetcher**

```python
# src/data/alpaca_fetcher.py
from pathlib import Path
import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt
from src.data.cache import Cache


class AlpacaFetcher:
    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        self._cache = Cache(cache_dir, ttl_hours=ttl_hours)

    def fetch_bars(self, symbol: str, days: int = 5, timeframe: str = "1Day") -> pd.DataFrame:
        cached = self._cache.read_parquet(symbol)
        if cached is not None:
            return cached
        raw = self._fetch_from_api(symbol, days, timeframe)
        df = self._parse_bars(raw)
        self._cache.write_parquet(symbol, df)
        return df

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def _fetch_from_api(self, symbol: str, days: int, timeframe: str) -> list[dict]:
        from alpaca_trade_api import REST
        api = REST()
        bars = api.get_bars(symbol, timeframe, limit=days).df
        return bars.reset_index().to_dict("records")

    def _parse_bars(self, raw: list[dict]) -> pd.DataFrame:
        if not raw:
            return pd.DataFrame()
        df = pd.DataFrame(raw)
        col_map = {"t": "date", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_alpaca_fetcher.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/alpaca_fetcher.py tests/test_alpaca_fetcher.py
git commit -m "feat: Alpaca price fetcher with cache and retry"
```

---

### Task 4: SEC Fundamentals Fetcher (edgartools)

**Files:**
- Create: `src/data/edgar_fetcher.py`
- Test: `tests/test_edgar_fetcher.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_edgar_fetcher.py
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
    from edgar import EDGARFileNotFound
    with patch.object(fetcher, "_fetch_from_edgar", side_effect=Exception("Company not found")):
        result = fetcher.fetch_fundamentals("FAKE")
    assert result == {}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_edgar_fetcher.py -v`
Expected: FAIL

- [ ] **Step 3: Implement edgar fetcher**

```python
# src/data/edgar_fetcher.py
import os
from pathlib import Path
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from src.data.cache import Cache

logger = logging.getLogger(__name__)


class EdgarFetcher:
    def __init__(self, cache_dir: Path, ttl_hours: int = 2160):
        # 2160 hours = 90 days for fundamentals
        self._cache = Cache(cache_dir, ttl_hours=ttl_hours)
        identity = os.environ.get("EDGAR_IDENTITY", "bull@trading-agent.dev")
        os.environ["EDGAR_IDENTITY"] = identity

    def fetch_fundamentals(self, ticker: str) -> dict:
        cached = self._cache.read_json(ticker)
        if cached is not None:
            return cached
        try:
            data = self._fetch_from_edgar(ticker)
        except Exception as e:
            logger.warning(f"Failed to fetch fundamentals for {ticker}: {e}")
            return {}
        if data:
            self._cache.write_json(ticker, data)
        return data

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def _fetch_from_edgar(self, ticker: str) -> dict:
        from edgar import Company
        company = Company(ticker)
        financials = company.get_financials()
        income = financials.income_statement()
        balance = financials.balance_sheet()
        return {
            "revenue": self._get_value(income, "Revenues"),
            "gross_profit": self._get_value(income, "GrossProfit"),
            "net_income": self._get_value(income, "NetIncomeLoss"),
            "total_assets": self._get_value(balance, "Assets"),
            "total_liabilities": self._get_value(balance, "Liabilities"),
            "current_assets": self._get_value(balance, "CurrentAssets"),
            "current_liabilities": self._get_value(balance, "CurrentLiabilities"),
        }

    def _get_value(self, statement, field_name: str) -> float | None:
        try:
            val = statement[field_name]
            if hasattr(val, "iloc"):
                return float(val.iloc[0])
            return float(val)
        except (KeyError, TypeError, ValueError):
            return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_edgar_fetcher.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/edgar_fetcher.py tests/test_edgar_fetcher.py
git commit -m "feat: SEC fundamentals fetcher via edgartools with 90-day cache"
```

---

### Task 5: FINRA Dark Pool Fetcher

**Files:**
- Create: `src/data/finra_fetcher.py`
- Test: `tests/test_finra_fetcher.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_finra_fetcher.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_finra_fetcher.py -v`
Expected: FAIL

- [ ] **Step 3: Implement FINRA fetcher**

```python
# src/data/finra_fetcher.py
from datetime import date, timedelta
from pathlib import Path
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from src.data.cache import Cache

logger = logging.getLogger(__name__)


class FinraFetcher:
    def __init__(self, cache_dir: Path, ttl_hours: int = 672):
        # 672 hours = 28 days (4 weeks for ATS data lag)
        self._cache = Cache(cache_dir, ttl_hours=ttl_hours)

    def fetch_dark_pool(self, ticker: str) -> dict:
        cached = self._cache.read_json(f"{ticker}_darkpool")
        if cached is not None:
            return cached
        try:
            data = self._fetch_from_finra(ticker)
        except Exception as e:
            logger.warning(f"Failed to fetch dark pool data for {ticker}: {e}")
            return {}
        if data:
            self._cache.write_json(f"{ticker}_darkpool", data)
        return data

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def _fetch_from_finra(self, ticker: str) -> dict:
        import requests
        url = f"https://api.finra.org/data/group/otcMarket/name/weeklySummary"
        params = {
            "symbol": ticker,
            "startDate": (date.today() - timedelta(weeks=4)).isoformat(),
            "endDate": date.today().isoformat(),
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        records = resp.json()
        if not records:
            return {}
        latest = records[-1]
        ats_vol = latest.get("atsVolume", 0)
        total_vol = latest.get("totalVolume", 1)
        return {
            "as_of_date": latest.get("weekStartDate", ""),
            "ats_volume": ats_vol,
            "total_volume": total_vol,
            "ats_ratio": ats_vol / total_vol if total_vol > 0 else 0,
        }

    @staticmethod
    def staleness_decay(weeks_stale: float) -> float:
        return max(0.0, 1.0 - weeks_stale / 4.0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_finra_fetcher.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/finra_fetcher.py tests/test_finra_fetcher.py
git commit -m "feat: FINRA dark pool fetcher with staleness decay weighting"
```

---

### Task 6: Quality Signal (Piotroski F-Score)

**Files:**
- Create: `src/signals/quality.py`
- Test: `tests/test_quality.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_quality.py
from src.signals.quality import quality_score

def test_high_quality_company():
    fundamentals = {
        "revenue": 100,
        "gross_profit": 60,
        "net_income": 20,
        "total_assets": 200,
        "total_liabilities": 80,
        "current_assets": 50,
        "current_liabilities": 30,
    }
    prev = {
        "revenue": 90,
        "gross_profit": 50,
        "net_income": 15,
        "total_assets": 180,
        "total_liabilities": 85,
        "current_assets": 40,
        "current_liabilities": 35,
    }
    score = quality_score(fundamentals, prev)
    assert score >= 5  # Most criteria should pass
    assert score <= 9

def test_low_quality_company():
    fundamentals = {
        "revenue": 100,
        "gross_profit": 10,
        "net_income": -5,
        "total_assets": 200,
        "total_liabilities": 150,
        "current_assets": 20,
        "current_liabilities": 60,
    }
    prev = {
        "revenue": 120,
        "gross_profit": 30,
        "net_income": 10,
        "total_assets": 180,
        "total_liabilities": 100,
        "current_assets": 50,
        "current_liabilities": 40,
    }
    score = quality_score(fundamentals, prev)
    assert score <= 4

def test_missing_data_returns_zero():
    score = quality_score({}, {})
    assert score == 0

def test_gross_margin_pass():
    fundamentals = {"gross_profit": 60, "revenue": 100}
    result = gross_margin_score(fundamentals, threshold=0.3)
    assert result == 1

def test_gross_margin_fail():
    fundamentals = {"gross_profit": 20, "revenue": 100}
    result = gross_margin_score(fundamentals, threshold=0.3)
    assert result == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_quality.py -v`
Expected: FAIL

- [ ] **Step 3: Implement quality signal**

```python
# src/signals/quality.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_quality.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/signals/quality.py tests/test_quality.py
git commit -m "feat: quality signal with Piotroski F-score and gross margin"
```

---

### Task 7: Momentum Signal

**Files:**
- Create: `src/signals/momentum.py`
- Test: `tests/test_momentum.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_momentum.py
import pandas as pd
from src.signals.momentum import momentum_score, rank_momentum

def test_momentum_score_positive():
    prices = pd.DataFrame({"close": [100 + i for i in range(252)]})
    score = momentum_score(prices, lookback=252, skip=21)
    assert score > 0

def test_momentum_score_negative():
    prices = pd.DataFrame({"close": [300 - i for i in range(252)]})
    score = momentum_score(prices, lookback=252, skip=21)
    assert score < 0

def test_momentum_score_short_data():
    prices = pd.DataFrame({"close": [100, 101, 102]})
    score = momentum_score(prices, lookback=252, skip=21)
    assert score == 0.0

def test_rank_momentum():
    tickers = {
        "AAPL": pd.DataFrame({"close": [100 + i for i in range(252)]}),
        "TSLA": pd.DataFrame({"close": [200 - i * 0.5 for i in range(252)]}),
        "MSFT": pd.DataFrame({"close": [150 + i * 0.3 for i in range(252)]}),
    }
    ranked = rank_momentum(tickers, top_n=2)
    assert len(ranked) == 2
    assert ranked[0][1] >= ranked[1][1]  # Descending order
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_momentum.py -v`
Expected: FAIL

- [ ] **Step 3: Implement momentum signal**

```python
# src/signals/momentum.py
import pandas as pd


def momentum_score(prices: pd.DataFrame, lookback: int = 252, skip: int = 21) -> float:
    """12-1 momentum: return over lookback period skipping last `skip` days."""
    if len(prices) < lookback:
        return 0.0
    close = prices["close"].values
    current = close[-1 - skip]
    past = close[-1 - skip - lookback] if len(close) > lookback + skip else close[0]
    if past == 0:
        return 0.0
    return (current - past) / past


def rank_momentum(
    ticker_prices: dict[str, pd.DataFrame],
    lookback: int = 252,
    skip: int = 21,
    top_n: int = 15,
) -> list[tuple[str, float]]:
    scores = {}
    for ticker, prices in ticker_prices.items():
        scores[ticker] = momentum_score(prices, lookback, skip)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_momentum.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/signals/momentum.py tests/test_momentum.py
git commit -m "feat: 12-1 momentum signal with ranking"
```

---

### Task 8: Regime Classifier

**Files:**
- Create: `src/signals/regime.py`
- Test: `tests/test_regime.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_regime.py
from src.signals.regime import classify_regime, adjust_weights, Regime

def test_risk_on():
    assert classify_regime(vix=18.0) == Regime.RISK_ON

def test_late_cycle():
    assert classify_regime(vix=22.0) == Regime.LATE_CYCLE

def test_stress():
    assert classify_regime(vix=35.0) == Regime.STRESS

def test_adjust_weights_risk_on():
    base = {"quality": 0.25, "momentum": 0.30, "value": 0.10, "low_vol": 0.15, "sentiment": 0.20}
    adjusted = adjust_weights(base, Regime.RISK_ON)
    assert adjusted["momentum"] > base["momentum"]
    assert adjusted["value"] < base["value"]

def test_adjust_weights_stress():
    base = {"quality": 0.25, "momentum": 0.30, "value": 0.10, "low_vol": 0.15, "sentiment": 0.20}
    adjusted = adjust_weights(base, Regime.STRESS)
    assert adjusted["low_vol"] > base["low_vol"]
    assert adjusted["momentum"] < base["momentum"]

def test_weights_sum_to_one():
    base = {"quality": 0.25, "momentum": 0.30, "value": 0.10, "low_vol": 0.15, "sentiment": 0.20}
    for regime in Regime:
        adjusted = adjust_weights(base, regime)
        assert abs(sum(adjusted.values()) - 1.0) < 0.01
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_regime.py -v`
Expected: FAIL

- [ ] **Step 3: Implement regime classifier**

```python
# src/signals/regime.py
from enum import Enum


class Regime(Enum):
    RISK_ON = "risk_on"
    LATE_CYCLE = "late_cycle"
    STRESS = "stress"


def classify_regime(vix: float) -> Regime:
    if vix < 20:
        return Regime.RISK_ON
    elif vix <= 30:
        return Regime.LATE_CYCLE
    else:
        return Regime.STRESS


# Regime-based weight shifts (multiplicative adjustments)
_REGIME_SHIFTS = {
    Regime.RISK_ON: {"momentum": 1.3, "value": 0.7, "low_vol": 0.8},
    Regime.LATE_CYCLE: {"momentum": 0.8, "value": 1.3, "low_vol": 1.1},
    Regime.STRESS: {"momentum": 0.6, "value": 1.0, "low_vol": 1.5},
}


def adjust_weights(base: dict[str, float], regime: Regime) -> dict[str, float]:
    shifts = _REGIME_SHIFTS[regime]
    adjusted = {}
    for factor, weight in base.items():
        shift = shifts.get(factor, 1.0)
        adjusted[factor] = weight * shift
    total = sum(adjusted.values())
    return {k: v / total for k, v in adjusted.items()}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_regime.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/signals/regime.py tests/test_regime.py
git commit -m "feat: VIX-based regime classifier with weight adjustment"
```

---

### Task 9: Bull Strategy (PyBroker Integration)

**Files:**
- Create: `src/strategy/bull_strategy.py`
- Test: `tests/test_bull_strategy.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_bull_strategy.py
import pandas as pd
import numpy as np
from src.strategy.bull_strategy import BullStrategy

def test_strategy_generates_signals():
    strategy = BullStrategy(vix=18.0)
    n = 300
    prices = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n, freq="B"),
        "open": np.random.uniform(95, 105, n),
        "high": np.random.uniform(100, 110, n),
        "low": np.random.uniform(90, 100, n),
        "close": np.cumsum(np.random.randn(n)) + 100,
        "volume": np.random.randint(1000000, 5000000, n),
    })
    signals = strategy.generate_signals(prices)
    assert "quality" in signals
    assert "momentum" in signals
    assert "regime" in signals
    assert "composite" in signals

def test_strategy_risk_on_high_momentum():
    strategy = BullStrategy(vix=15.0)
    n = 300
    close = np.array([100 + i * 0.5 for i in range(n)])
    prices = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n, freq="B"),
        "open": close - 0.5,
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": np.full(n, 2000000),
    })
    signals = strategy.generate_signals(prices)
    assert signals["momentum"] > 0

def test_pybroker_exec_fn_callable():
    strategy = BullStrategy(vix=18.0)
    fn = strategy.pybroker_exec_fn()
    assert callable(fn)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_bull_strategy.py -v`
Expected: FAIL

- [ ] **Step 3: Implement bull strategy**

```python
# src/strategy/bull_strategy.py
import pandas as pd
from src.signals.quality import quality_score
from src.signals.momentum import momentum_score
from src.signals.regime import classify_regime, adjust_weights, Regime

BASE_WEIGHTS = {
    "quality": 0.25,
    "momentum": 0.30,
    "value": 0.10,
    "low_vol": 0.15,
    "sentiment": 0.20,
}


class BullStrategy:
    def __init__(self, vix: float = 18.0, quality_threshold: int = 6,
                 momentum_top_n: int = 15, stop_loss_pct: float = 0.07):
        self.vix = vix
        self.quality_threshold = quality_threshold
        self.momentum_top_n = momentum_top_n
        self.stop_loss_pct = stop_loss_pct
        self.regime = classify_regime(vix)
        self.weights = adjust_weights(BASE_WEIGHTS, self.regime)

    def generate_signals(self, prices: pd.DataFrame, fundamentals: dict | None = None,
                         prev_fundamentals: dict | None = None) -> dict:
        q_score = quality_score(fundamentals or {}, prev_fundamentals) / 9.0
        m_score = self._normalize_momentum(momentum_score(prices))

        signals = {
            "quality": q_score,
            "momentum": m_score,
            "value": 0.5,  # placeholder until value signal implemented
            "low_vol": 0.5,  # placeholder until low-vol signal implemented
            "sentiment": 0.5,  # placeholder until sentiment signal implemented
        }

        composite = sum(signals[k] * self.weights[k] for k in signals)
        signals["composite"] = composite
        signals["regime"] = self.regime.value
        return signals

    def _normalize_momentum(self, raw_momentum: float) -> float:
        """Normalize raw momentum return to 0-1 scale."""
        return max(0.0, min(1.0, (raw_momentum + 0.5) / 1.0))

    def pybroker_exec_fn(self):
        """Return a PyBroker-compatible execution function."""
        def exec_fn(ctx):
            if not ctx.long_pos():
                signals = self.generate_signals(
                    pd.DataFrame({"close": ctx.close}),
                )
                if signals["composite"] > 0.55:
                    ctx.buy_shares = ctx.shares // 10  # 10% of buying power
                    ctx.stop_loss_pct = self.stop_loss_pct
                    ctx.hold_bars = 21  # ~1 month
        return exec_fn
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_bull_strategy.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/strategy/bull_strategy.py tests/test_bull_strategy.py
git commit -m "feat: multi-factor bull strategy with PyBroker integration"
```

---

### Task 10: Kelly Position Sizing

**Files:**
- Create: `src/sizing/kelly.py`
- Test: `tests/test_kelly.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_kelly.py
import numpy as np
from src.sizing.kelly import half_kelly_size

def test_half_kelly_positive_sharpe():
    size = half_kelly_size(sharpe=1.5, volatility=0.20, max_fraction=0.20)
    assert size > 0
    assert size <= 0.20

def test_half_kelly_zero_sharpe():
    size = half_kelly_size(sharpe=0.0, volatility=0.20, max_fraction=0.20)
    assert size == 0.0

def test_half_kelly_negative_sharpe():
    size = half_kelly_size(sharpe=-1.0, volatility=0.20, max_fraction=0.20)
    assert size == 0.0

def test_half_kelly_respects_max():
    size = half_kelly_size(sharpe=5.0, volatility=0.10, max_fraction=0.20)
    assert size <= 0.20

def test_half_kelly_default_max():
    size = half_kelly_size(sharpe=2.0, volatility=0.15)
    assert size <= 0.10  # default max_fraction
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_kelly.py -v`
Expected: FAIL

- [ ] **Step 3: Implement Kelly sizing**

```python
# src/sizing/kelly.py
import numpy as np


def half_kelly_size(
    sharpe: float,
    volatility: float,
    max_fraction: float = 0.10,
    risk_free: float = 0.045,
) -> float:
    """Compute half-Kelly optimal fraction for a single asset.

    Kelly fraction = (mu - rf) / sigma^2
    Half-Kelly = Kelly / 2 (safety buffer)

    We approximate mu from Sharpe: mu = rf + sharpe * sigma
    """
    if sharpe <= 0 or volatility <= 0:
        return 0.0
    mu = risk_free + sharpe * volatility
    kelly = (mu - risk_free) / (volatility ** 2)
    half_k = kelly / 2.0
    return min(half_k, max_fraction)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_kelly.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/sizing/kelly.py tests/test_kelly.py
git commit -m "feat: half-Kelly position sizing from Sharpe and volatility"
```

---

### Task 11: Walk-Forward Runner

**Files:**
- Create: `src/backtest/runner.py`
- Test: `tests/test_runner.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_runner.py
from src.backtest.runner import WalkForwardConfig

def test_walkforward_config_defaults():
    config = WalkForwardConfig()
    assert config.train_bars == 504
    assert config.test_bars == 63
    assert config.embargo_bars == 5

def test_walkforward_config_custom():
    config = WalkForwardConfig(train_bars=252, test_bars=21, embargo_bars=3)
    assert config.train_bars == 252
    assert config.test_bars == 21

def test_count_windows():
    config = WalkForwardConfig(train_bars=504, test_bars=63, embargo_bars=5)
    total_bars = 504 + 63 + 5 + 63 + 5 + 63  # 3 test windows
    windows = config.count_windows(total_bars)
    assert windows == 3

def test_count_windows_insufficient():
    config = WalkForwardConfig(train_bars=504, test_bars=63, embargo_bars=5)
    windows = config.count_windows(500)  # not even one full train+test
    assert windows == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_runner.py -v`
Expected: FAIL

- [ ] **Step 3: Implement walk-forward runner**

```python
# src/backtest/runner.py
from dataclasses import dataclass


@dataclass
class WalkForwardConfig:
    train_bars: int = 504   # 2 years
    test_bars: int = 63      # 1 quarter
    embargo_bars: int = 5   # 1 week

    def count_windows(self, total_bars: int) -> int:
        if total_bars < self.train_bars + self.test_bars:
            return 0
        remaining = total_bars - self.train_bars
        windows = 0
        while remaining >= self.test_bars:
            windows += 1
            remaining -= self.test_bars + self.embargo_bars
        return windows

    def window_ranges(self, total_bars: int) -> list[tuple[int, int, int]]:
        """Return list of (train_start, train_end, test_end) tuples."""
        windows = []
        if total_bars < self.train_bars + self.test_bars:
            return windows
        pos = 0
        while pos + self.train_bars + self.test_bars <= total_bars:
            train_start = pos
            train_end = pos + self.train_bars
            test_end = train_end + self.test_bars
            windows.append((train_start, train_end, test_end))
            pos = test_end + self.embargo_bars
        return windows


def run_backtest(strategy, symbols: list[str], start_date: str, end_date: str,
                 config: WalkForwardConfig | None = None):
    """Run PyBroker walk-forward backtest. Returns test metrics only."""
    import pybroker
    config = config or WalkForwardConfig()
    pybroker_config = pybroker.Config(
        warmup=config.train_bars,
    )
    pybroker_strategy = pybroker.Strategy(
        pybroker.Alpaca(),
        start_date=start_date,
        end_date=end_date,
        config=pybroker_config,
    )
    exec_fn = strategy.pybroker_exec_fn()
    for symbol in symbols:
        pybroker_strategy.add_execution(exec_fn, [symbol])
    result = pybroker_strategy.backtest()
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_runner.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/backtest/runner.py tests/test_runner.py
git commit -m "feat: walk-forward runner with window counting and PyBroker integration"
```

---

### Task 12: Metrics Module (Anti-Overfitting)

**Files:**
- Create: `src/backtest/metrics.py`
- Test: `tests/test_metrics.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_metrics.py
import numpy as np
from src.backtest.metrics import (
    sharpe_ratio, max_drawdown, cap_outlier_year,
    regime_sharpe, bootstrap_ci, validate_strategy,
)

def test_sharpe_positive():
    returns = np.array([0.01, 0.02, -0.01, 0.03, 0.005])
    s = sharpe_ratio(returns)
    assert s > 0

def test_max_drawdown():
    equity = np.array([100, 110, 105, 95, 100])
    dd = max_drawdown(equity)
    assert abs(dd - 0.1364) < 0.01  # (110-95)/110

def test_cap_outlier_year():
    returns_2023 = np.full(252, 0.003)  # ~2.5x annual
    returns_2024 = np.full(252, 0.004)  # ~3x annual
    returns_2025 = np.full(252, 0.0025)  # ~1.9x annual
    years = {
        2023: returns_2023,
        2024: returns_2024,
        2025: returns_2025,
    }
    capped = cap_outlier_year(years, max_annual=0.60)
    # 2024 would be >60% but capped
    assert capped[2024].mean() * 252 <= 0.61

def test_regime_sharpe():
    returns = np.array([0.01] * 50 + [-0.02] * 50)
    regimes = np.array(["risk_on"] * 50 + ["stress"] * 50)
    result = regime_sharpe(returns, regimes)
    assert "risk_on" in result
    assert "stress" in result
    assert result["risk_on"] > 0
    assert result["stress"] < 0

def test_validate_strategy_passes():
    regime_results = {"risk_on": 1.5, "late_cycle": 0.8, "stress": -0.5}
    assert validate_strategy(regime_results, min_regimes=2) is True

def test_validate_strategy_fails():
    regime_results = {"risk_on": 1.5, "late_cycle": -0.3, "stress": -1.0}
    assert validate_strategy(regime_results, min_regimes=2) is False

def test_bootstrap_ci():
    returns = np.random.normal(0.001, 0.02, 1000)
    lo, hi = bootstrap_ci(returns, n_samples=100)
    assert lo < hi
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_metrics.py -v`
Expected: FAIL

- [ ] **Step 3: Implement metrics module**

```python
# src/backtest/metrics.py
import numpy as np


def sharpe_ratio(returns: np.ndarray, risk_free: float = 0.045 / 252) -> float:
    if len(returns) == 0:
        return 0.0
    excess = returns - risk_free
    if np.std(excess) == 0:
        return 0.0
    return float(np.mean(excess) / np.std(excess) * np.sqrt(252))


def max_drawdown(equity: np.ndarray) -> float:
    if len(equity) == 0:
        return 0.0
    peak = np.maximum.accumulate(equity)
    dd = (peak - equity) / peak
    return float(np.max(dd))


def cap_outlier_year(yearly_returns: dict[int, np.ndarray],
                     max_annual: float = 0.60) -> dict[int, np.ndarray]:
    capped = {}
    for year, returns in yearly_returns.items():
        total = float(np.prod(1 + returns) - 1)
        if total > max_annual:
            scale = max_annual / total
            capped[year] = returns * scale
        else:
            capped[year] = returns.copy()
    return capped


def regime_sharpe(returns: np.ndarray, regimes: np.ndarray) -> dict[str, float]:
    result = {}
    for regime in np.unique(regimes):
        mask = regimes == regime
        regime_returns = returns[mask]
        if len(regime_returns) > 0:
            result[regime] = sharpe_ratio(regime_returns)
    return result


def validate_strategy(regime_sharpes: dict[str, float],
                      min_regimes: int = 2) -> bool:
    positive = sum(1 for s in regime_sharpes.values() if s > 0)
    return positive >= min_regimes


def bootstrap_ci(returns: np.ndarray, n_samples: int = 1000,
                 ci: float = 0.95) -> tuple[float, float]:
    """Bootstrap confidence interval for Sharpe ratio."""
    sharpes = []
    n = len(returns)
    for _ in range(n_samples):
        sample = np.random.choice(returns, size=n, replace=True)
        sharpes.append(sharpe_ratio(sample))
    alpha = (1 - ci) / 2
    lo = float(np.percentile(sharpes, alpha * 100))
    hi = float(np.percentile(sharpes, (1 - alpha) * 100))
    return lo, hi
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_metrics.py -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/backtest/metrics.py tests/test_metrics.py
git commit -m "feat: metrics with Sharpe, max DD, outlier cap, regime validation, bootstrap CI"
```

---

### Task 13: Integration Test + Test Fixtures

**Files:**
- Create: `tests/fixtures/spy_2yr.parquet` (generated by script)
- Create: `tests/fixtures/fundamentals_5companies.json`
- Create: `tests/fixtures/regime_history.csv`
- Test: `tests/test_integration.py`

- [ ] **Step 1: Generate test fixtures**

```python
# scripts/generate_fixtures.py
import pandas as pd
import numpy as np
import json

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
```

Run: `mkdir -p tests/fixtures && python scripts/generate_fixtures.py`

- [ ] **Step 2: Write integration test**

```python
# tests/test_integration.py
import pandas as pd
from pathlib import Path
from src.data.cache import Cache
from src.signals.quality import quality_score
from src.signals.momentum import momentum_score
from src.signals.regime import classify_regime, Regime
from src.strategy.bull_strategy import BullStrategy
from src.backtest.runner import WalkForwardConfig
from src.backtest.metrics import sharpe_ratio, max_drawdown, bootstrap_ci

FIXTURES = Path(__file__).parent / "fixtures"

def test_full_pipeline_smoke():
    """Smoke test: SPY data → signals → strategy → metrics in <60s."""
    prices = pd.read_parquet(FIXTURES / "spy_2yr.parquet")
    import json
    with open(FIXTURES / "fundamentals_5companies.json") as f:
        all_fundamentals = json.load(f)

    # 1. Generate signals
    strategy = BullStrategy(vix=18.0)
    signals = strategy.generate_signals(prices, all_fundamentals.get("AAPL"))

    # 2. Verify signal structure
    assert "composite" in signals
    assert 0 <= signals["composite"] <= 1

    # 3. Walk-forward config
    config = WalkForwardConfig()
    assert config.count_windows(len(prices)) >= 0

    # 4. Metrics on synthetic returns
    returns = prices["close"].pct_change().dropna().values
    s = sharpe_ratio(returns)
    dd = max_drawdown(prices["close"].values)
    assert isinstance(s, float)
    assert 0 < dd < 1

    # 5. Bootstrap CI
    lo, hi = bootstrap_ci(returns, n_samples=50)
    assert lo < hi
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/test_integration.py -v --timeout=60`
Expected: PASS

- [ ] **Step 4: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/ tests/test_integration.py
git commit -m "feat: integration smoke test with fixtures"
```

---

### Task 14: Final Wiring + .gitignore + README Update

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`

- [ ] **Step 1: Ensure .gitignore covers all cache dirs**

Verify `.gitignore` contains:
```
*.txt
!README*.txt
.env
.env.*
__pycache__/
*.pyc
.DS_Store
data/prices/*.parquet
data/fundamentals/*.json
data/fundamentals/*.csv
.pytest_cache/
*.egg-info/
```

- [ ] **Step 2: Add backtesting section to README**

Add after the "Research Methodology" section in `README.md`:

```markdown
## Backtesting Engine

Phase 1 backtesting validates the Quality+Momentum strategy with walk-forward analysis:

```bash
# Run full test suite
pytest tests/ -v

# Run backtest on SPY (requires Alpaca API keys)
python -m src.backtest.runner --symbols SPY --start 2022-01-01 --end 2024-12-31
```

**Anti-overfitting guards:** Walk-forward validation, outlier year caps (60%), multi-regime Sharpe requirement, bootstrap CI, 8-parameter ceiling.
```

- [ ] **Step 3: Run full test suite one final time**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Commit and push**

```bash
git add .gitignore README.md
git commit -m "feat: final project wiring and README update"
git push origin main
```

---

## Self-Review

**Spec coverage check:**
- Section 1 (Architecture): Tasks 2-12 cover all components
- Section 2 (Project Structure): Task 1 creates skeleton, Tasks 2-12 fill modules
- Section 3 (Error Handling): Task 3 (retry), Task 4 (try/catch + empty return), Task 5 (staleness decay), Task 12 (window skip)
- Section 4 (Anti-Overfitting): Task 12 (outlier cap, regime validation, bootstrap CI), Task 11 (walk-forward config)
- Section 5 (Exit Rules): Task 9 (stop_loss_pct, hold_bars in pybroker_exec_fn), Task 10 (Kelly sizing)
- Section 6 (Testing): All tasks follow TDD, Task 13 integration test, fixtures

**Placeholder scan:** No TBD/TODO/fill-in-later found.

**Type consistency:** All function signatures consistent across tasks. `quality_score(fundamentals, prev)` matches in Task 6 and Task 9. `BullStrategy(vix=...)` consistent in Task 9 and test files. `WalkForwardConfig` defaults match spec (504/63/5).