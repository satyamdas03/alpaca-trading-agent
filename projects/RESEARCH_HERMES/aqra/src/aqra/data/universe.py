import logging
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class Universe:
    """S&P 500 constituents.

    Phase 1b: survivorship-bias-free historical membership reconstructed from
    the Wikipedia constituents page.  The page carries two tables:
      table[0] — current constituents,
      table[1] — "Selected changes" with Date / Added / Removed columns.
    Walking the changes backwards from the current list yields the membership
    on any past date (accurate back to roughly 2000; changes before the table's
    horizon are unrecoverable and the earliest reconstructed list is used).
    """

    URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    HEADERS = {
        "User-Agent": "AQRA/0.1.0 (research; satyamdas03@gmail.com) pandas-read-html"
    }

    def __init__(self, cache_path: Path | None = None):
        self.cache_path = cache_path
        self._current: list[str] | None = None
        self._changes: pd.DataFrame | None = None

    def _fetch_tables(self) -> tuple[list[str], pd.DataFrame]:
        response = requests.get(self.URL, headers=self.HEADERS, timeout=30)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        current = sorted(tables[0]["Symbol"].astype(str).tolist())

        changes = tables[1].copy()
        # Flatten the two-level header (Date, Added/Ticker, Removed/Ticker, ...)
        if isinstance(changes.columns, pd.MultiIndex):
            changes.columns = [
                "_".join(str(part) for part in col if str(part) != "nan").strip()
                for col in changes.columns
            ]
        # Pick the FIRST column matching each role (Added/Removed appear twice:
        # once as Ticker, once as Security — we want the ticker column).
        picked: dict[str, str] = {}
        for col in changes.columns:
            low = str(col).lower()
            if (low.startswith("date") or low.startswith("effective")) and "date" not in picked:
                picked["date"] = col
                continue
            for role in ("added", "removed"):
                if low.startswith(role) and role not in picked:
                    picked[role] = col
        changes = pd.DataFrame({role: changes[col] for role, col in picked.items()})
        changes["date"] = pd.to_datetime(changes["date"], errors="coerce")
        changes = changes.dropna(subset=["date"]).sort_values("date", ascending=False)
        return current, changes

    def _ensure_loaded(self):
        if self._current is None or self._changes is None:
            self._current, self._changes = self._fetch_tables()

    def current(self) -> list[str]:
        self._ensure_loaded()
        return list(self._current)

    def at_date(self, date: str | pd.Timestamp) -> list[str]:
        """Membership on `date`, reconstructed by unwinding changes newest-first."""
        self._ensure_loaded()
        target = pd.Timestamp(date).normalize()
        members = set(self._current)
        # Unwind every change that happened AFTER the target date:
        # an addition after target means the ticker was not yet in;
        # a removal after target means the ticker was still in.
        for _, row in self._changes.iterrows():
            if row["date"] <= target:
                break
            added = row.get("added")
            removed = row.get("removed")
            if isinstance(added, str) and added and added.lower() != "nan":
                members.discard(added.strip())
            if isinstance(removed, str) and removed and removed.lower() != "nan":
                members.add(removed.strip())
        return sorted(m for m in members if m and m.lower() != "nan")

    def membership_intervals(self) -> pd.DataFrame:
        """Long-format record of changes for storage/audit: date, added, removed."""
        self._ensure_loaded()
        return self._changes.copy()
