import logging

import pandas as pd
import requests
from lxml import etree

logger = logging.getLogger(__name__)


class RSSSource:
    def fetch_feed(self, url: str) -> pd.DataFrame:
        columns = ["title", "link", "published", "summary"]
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            root = etree.fromstring(r.content)
        except Exception as e:
            logger.warning("Failed to fetch/parse RSS feed %s: %s", url, e)
            return pd.DataFrame(columns=columns)

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        rss_items = root.findall(".//item")
        atom_entries = root.findall(".//atom:entry", ns)
        items = rss_items or atom_entries

        rows = []
        for item in items:
            if item in rss_items:
                title = item.findtext("title", default="")
                link = item.findtext("link", default="")
                published = item.findtext("pubDate", default="")
                summary = item.findtext("description", default="")
            else:
                title = item.findtext("atom:title", default="", namespaces=ns)
                link_el = item.find("atom:link", ns)
                link = link_el.get("href") if link_el is not None else ""
                published = item.findtext("atom:updated", default="", namespaces=ns)
                summary = item.findtext("atom:summary", default="", namespaces=ns)
            rows.append(
                {"title": title, "link": link, "published": published, "summary": summary}
            )

        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            df["published"] = pd.to_datetime(df["published"], errors="coerce")
        return df
