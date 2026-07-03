"""EDGAR XBRL frames-based fundamentals for Lane S value/quality factors.

Uses the free, keyless SEC endpoints (User-Agent required):
  * https://www.sec.gov/files/company_tickers.json          — CIK <-> ticker map
  * https://data.sec.gov/api/xbrl/frames/{tax}/{concept}/{unit}/{period}.json
      — one request returns the concept value for EVERY filer in that period.

Concepts pulled per calendar quarter:
  us-gaap/EarningsPerShareDiluted   (USD-per-shares, duration)  -> eps_dil
  us-gaap/StockholdersEquity        (USD, instant)              -> equity
  us-gaap/GrossProfit               (USD, duration)             -> gross_profit
  us-gaap/Revenues (+ fallback RevenueFromContractWithCustomerExcludingAssessedTax)
                                    (USD, duration)             -> revenues
  dei/EntityCommonStockSharesOutstanding (shares, instant)      -> shares_out

Point-in-time: a quarter ending at `end` is marked available_at = end + 75 days
(10-Q deadline is 40-45 days for large filers; 75 is conservative).
"""
import logging
import time

import pandas as pd
import requests

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "AQRA research agent (satyamdas03@gmail.com)"}
TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
FRAMES_URL = "https://data.sec.gov/api/xbrl/frames/{tax}/{concept}/{unit}/{period}.json"

AVAILABILITY_LAG_DAYS = 75

# (tax, concept, unit, instantaneous?)
CONCEPTS = [
    ("us-gaap", "EarningsPerShareDiluted", "USD-per-shares", False, "eps_dil"),
    ("us-gaap", "StockholdersEquity", "USD", True, "equity"),
    ("us-gaap", "GrossProfit", "USD", False, "gross_profit"),
    ("us-gaap", "Revenues", "USD", False, "revenues"),
    ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", "USD", False,
     "revenues_fallback"),
    ("dei", "EntityCommonStockSharesOutstanding", "shares", True, "shares_out"),
]


class EDGARFundamentals:
    def __init__(self, sleep: float = 0.12):
        self.sleep = sleep  # SEC fair-use: <= 10 req/s
        self._cik_map: pd.DataFrame | None = None

    def cik_ticker_map(self) -> pd.DataFrame:
        if self._cik_map is None:
            r = requests.get(TICKER_MAP_URL, headers=HEADERS, timeout=30)
            r.raise_for_status()
            rows = [
                {"cik": int(v["cik_str"]), "ticker": str(v["ticker"]).upper()}
                for v in r.json().values()
            ]
            self._cik_map = pd.DataFrame(rows).drop_duplicates("cik")
        return self._cik_map

    def _fetch_frame(self, tax: str, concept: str, unit: str, period: str) -> pd.DataFrame:
        url = FRAMES_URL.format(tax=tax, concept=concept, unit=unit, period=period)
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 404:
                return pd.DataFrame()
            r.raise_for_status()
            data = r.json().get("data", [])
        except Exception as e:
            logger.warning("frame %s/%s %s failed: %s", tax, concept, period, e)
            return pd.DataFrame()
        finally:
            time.sleep(self.sleep)
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)[["cik", "end", "val"]]
        df["end"] = pd.to_datetime(df["end"])
        return df

    def fetch_quarter(self, year: int, quarter: int) -> pd.DataFrame:
        """All concepts for one calendar quarter, wide format keyed by cik."""
        merged: pd.DataFrame | None = None
        for tax, concept, unit, instant, name in CONCEPTS:
            period = f"CY{year}Q{quarter}" + ("I" if instant else "")
            df = self._fetch_frame(tax, concept, unit, period)
            if df.empty:
                continue
            df = df.rename(columns={"val": name})
            df = df.sort_values("end").groupby("cik", as_index=False).last()
            df = df.rename(columns={"end": f"end_{name}"})
            merged = df if merged is None else merged.merge(df, on="cik", how="outer")
        if merged is None:
            return pd.DataFrame()
        # unify revenue tags
        if "revenues_fallback" in merged.columns:
            if "revenues" in merged.columns:
                merged["revenues"] = merged["revenues"].fillna(merged["revenues_fallback"])
            else:
                merged["revenues"] = merged["revenues_fallback"]
            merged = merged.drop(columns=[c for c in merged.columns
                                          if c.startswith("revenues_fallback")
                                          or c == "end_revenues_fallback"],
                                 errors="ignore")
        end_cols = [c for c in merged.columns if c.startswith("end_")]
        merged["period_end"] = merged[end_cols].max(axis=1)
        merged = merged.drop(columns=end_cols)
        merged["available_at"] = merged["period_end"] + pd.Timedelta(days=AVAILABILITY_LAG_DAYS)
        merged["year"] = year
        merged["quarter"] = quarter
        return merged

    def build_panel(self, start_year: int, end_year: int,
                    tickers: list[str] | None = None) -> pd.DataFrame:
        """Quarterly fundamentals panel joined to tickers."""
        cmap = self.cik_ticker_map()
        if tickers is not None:
            wanted = {t.upper().replace("-", "").replace(".", "") for t in tickers}
            cmap = cmap[cmap["ticker"].str.replace("-", "").str.replace(".", "")
                        .isin(wanted)]
        frames = []
        for year in range(start_year, end_year + 1):
            for q in (1, 2, 3, 4):
                df = self.fetch_quarter(year, q)
                if df.empty:
                    continue
                df = df.merge(cmap, on="cik", how="inner")
                frames.append(df)
                logger.info("CY%dQ%d: %d matched filers", year, q, len(df))
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)
