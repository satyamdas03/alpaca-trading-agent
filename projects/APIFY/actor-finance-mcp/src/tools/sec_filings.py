"""SEC filings tool — search and retrieve EDGAR filings."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

import requests

logger = logging.getLogger(__name__)

EDGAR_BASE = "https://efts.sec.gov/LATEST/search-index?q=%22{TICKER}%22&dateRange=custom&startdt={START}&enddt={END}&forms={FORM}"
EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"

# Simpler: use SEC EDGAR full-text search API
SEC_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"

# Even simpler: use SEC EDGAR browse API
SEC_FILING_URL = "https://data.sec.gov/submissions/CIK{CIK}.json"
SEC_COMPANY_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={TICKER}&type={TYPE}&dateb=&owner=include&count={LIMIT}"

# Use the EDGAR full-text search API (modern)
EDGAR_FTS_URL = "https://efts.sec.gov/LATEST/search-index"

# Actually use the simplest working endpoint
EDGAR_API = "https://efts.sec.gov/LATEST/search-index"


def fetch_sec_filings(
    tickers: list[str],
    filing_type: str = "ALL",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Fetch recent SEC filings for given tickers."""
    tickers = tickers[:limit]
    now = datetime.now(timezone.utc).isoformat()
    results = []

    for ticker in tickers:
        try:
            filings = _get_filings_for_ticker(ticker, filing_type, limit)
            results.append({
                "tool": "sec_filings",
                "ticker": ticker,
                "data": {
                    "filings": filings,
                    "filing_count": len(filings),
                    "filing_type_filter": filing_type,
                },
                "source": "sec_edgar",
                "fetched_at": now,
                "cache_ttl": 86400,
            })
        except Exception as e:
            logger.warning(f"SEC filings failed for {ticker}: {e}")
            results.append({
                "tool": "sec_filings",
                "ticker": ticker,
                "data": {"error": f"SEC filing lookup failed for {ticker}: {str(e)}"},
                "source": "error",
                "fetched_at": now,
                "cache_ttl": 300,
            })

    return results


def _get_filings_for_ticker(ticker: str, filing_type: str, limit: int) -> list[dict[str, Any]]:
    """Get filings for a single ticker using SEC EDGAR submissions API."""
    headers = {
        "User-Agent": "FinanceDataMCP/1.0 (contact@finance-mcp.dev)",
        "Accept": "application/json",
    }

    # First, get CIK for the ticker
    cik = _get_cik(ticker, headers)
    if not cik:
        return []

    # Get submissions
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    filings = []
    recent = data.get("recentFilings", data)  # Handle both formats

    # Extract filing lists
    if isinstance(recent, dict):
        accession_list = recent.get("accessionNumber", [])
        filing_date_list = recent.get("filingDate", [])
        form_list = recent.get("form", [])
        doc_list = recent.get("primaryDocument", [])
        desc_list = recent.get("primaryDocDescription", [])
    else:
        return []

    count = 0
    for i in range(len(accession_list)):
        if count >= limit:
            break

        form = form_list[i] if i < len(form_list) else ""

        # Filter by filing type if specified
        if filing_type != "ALL" and form != filing_type:
            # Also match with dash variants (10-K includes 10-K/A)
            if not form.startswith(filing_type.replace("-", "")):
                continue

        accession = accession_list[i]
        accession_no_dashes = accession.replace("-", "")

        filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{doc_list[i] if i < len(doc_list) else 'index.json'}"

        filings.append({
            "form": form,
            "filing_date": filing_date_list[i] if i < len(filing_date_list) else "",
            "accession_number": accession,
            "description": desc_list[i] if i < len(desc_list) else "",
            "url": filing_url,
        })
        count += 1

    return filings


def _get_cik(ticker: str, headers: dict) -> str | None:
    """Get CIK number for a ticker using SEC's company search."""
    try:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={ticker}&output=json"
        resp = requests.get(url, headers=headers, timeout=10)
        # Fallback: use company_tickers.json mapping
        return _cik_from_mapping(ticker)
    except Exception:
        return _cik_from_mapping(ticker)


def _cik_from_mapping(ticker: str) -> str | None:
    """Get CIK from SEC's company_tickers.json (cached file)."""
    headers = {
        "User-Agent": "FinanceDataMCP/1.0 (contact@finance-mcp.dev)",
        "Accept": "application/json",
    }
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        ticker_upper = ticker.upper()
        # Remove .NS / .BSE suffixes for SEC lookup
        ticker_clean = re.sub(r'\.(NS|BSE|BO)$', '', ticker_upper)

        for cik_str, info in data.items():
            if info.get("ticker", "").upper() == ticker_clean:
                return str(info.get("cik_str", "")).zfill(10)
    except Exception as e:
        logger.warning(f"CIK lookup failed for {ticker}: {e}")

    return None