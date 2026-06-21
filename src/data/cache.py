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