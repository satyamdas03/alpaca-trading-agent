import pandas as pd
import requests
from io import StringIO
from pathlib import Path


class Universe:
    """S&P 500 historical constituents approximated by current list for Phase 1.
    Phase 2 upgrades to Wikipedia historical lists or dedicated constituent data.
    """

    URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    def __init__(self, cache_path: Path | None = None):
        self.cache_path = cache_path
        self._current = None

    def _fetch_current(self) -> list[str]:
        headers = {
            "User-Agent": "AQRA/0.1.0 (research; satyamdas03@gmail.com) pandas-read-html"
        }
        response = requests.get(self.URL, headers=headers, timeout=30)
        response.raise_for_status()
        table = pd.read_html(StringIO(response.text))[0]
        return sorted(table["Symbol"].tolist())

    def at_date(self, date: str | pd.Timestamp) -> list[str]:
        # Phase 1: assume current universe (survivorship bias acknowledged in paper).
        if self._current is None:
            self._current = self._fetch_current()
        return self._current
