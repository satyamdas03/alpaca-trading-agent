import os
import logging

import pandas as pd
import requests
from lxml import etree

logger = logging.getLogger(__name__)


class EDGARSource:
    def fetch_form4(
        self, ticker: str, start: str, end: str
    ) -> pd.DataFrame:
        user_agent = os.getenv("EDGAR_API_KEY") or os.getenv("SEC_USER_AGENT")
        if not user_agent:
            logger.warning("EDGAR_API_KEY/SEC_USER_AGENT not set; returning empty Form 4 data")
            return pd.DataFrame(
                columns=[
                    "ticker",
                    "filing_date",
                    "form",
                    "issuer",
                    "reporting_owner",
                    "transaction_date",
                    "transaction_type",
                    "shares",
                    "price",
                ]
            )

        url = (
            "https://www.sec.gov/cgi-bin/browse-edgar"
            f"?action=getcompany&CIK={ticker.upper()}"
            f"&type=4&dateb={end.replace('-', '')}"
            f"&datea={start.replace('-', '')}"
            "&count=100&output=xml"
        )
        headers = {"User-Agent": user_agent}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()

        try:
            root = etree.fromstring(r.content)
        except etree.XMLSyntaxError:
            return pd.DataFrame(
                columns=[
                    "ticker",
                    "filing_date",
                    "form",
                    "issuer",
                    "reporting_owner",
                    "transaction_date",
                    "transaction_type",
                    "shares",
                    "price",
                ]
            )

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        rows = []
        for entry in entries:
            title = entry.findtext("atom:title", default="", namespaces=ns)
            updated = entry.findtext("atom:updated", default="", namespaces=ns)
            link_el = entry.find("atom:link", ns)
            href = link_el.get("href") if link_el is not None else ""
            rows.append(
                {
                    "ticker": ticker,
                    "filing_date": pd.to_datetime(updated, errors="coerce"),
                    "form": "4",
                    "issuer": title,
                    "reporting_owner": "",
                    "transaction_date": pd.NaT,
                    "transaction_type": "",
                    "shares": pd.NA,
                    "price": pd.NA,
                    "link": href,
                }
            )

        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(
                columns=[
                    "ticker",
                    "filing_date",
                    "form",
                    "issuer",
                    "reporting_owner",
                    "transaction_date",
                    "transaction_type",
                    "shares",
                    "price",
                ]
            )
        return df
