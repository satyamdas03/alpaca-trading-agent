# SME Lead Generation Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a free pipeline that discovers SMEs without websites in India/Australia, enriches contacts, and exports CSV for outreach.

**Architecture:** 3-layer pipeline — Python Maps scraper for discovery, Apollo + social scraping for enrichment, CSV exporter for outreach. All open-source, $0 cost.

**Tech Stack:** Python 3.11+, google-maps-scraper (noworneverev), playwright, apify-client, pandas

---

### Task 1: Project Setup + Config

**Files:**
- Create: `config.py`
- Create: `requirements.txt`
- Create: `__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
google-maps-scraper[stealth]>=0.5.0
playwright>=1.40.0
pandas>=2.0.0
requests>=2.31.0
dnspython>=2.4.0
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -r requirements.txt && playwright install firefox`
Expected: All packages installed, Firefox browser downloaded

- [ ] **Step 3: Create config.py with cities, categories, search queries**

```python
CITIES = {
    "india": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
    "australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
}

CATEGORIES = [
    "cafe",
    "bakery",
    "salon",
    "gym",
    "retail shop",
    "plumber",
    "electrician",
    "restaurant",
]

# Maps search query format per category
SEARCH_TEMPLATES = {
    "cafe": "{category} in {city}",
    "bakery": "{category} in {city}",
    "salon": "hair {category} in {city}",
    "gym": "{category} in {city}",
    "retail shop": "{category} in {city}",
    "plumber": "{category} in {city}",
    "electrician": "{category} in {city}",
    "restaurant": "{category} in {city}",
}

MAX_RESULTS_PER_QUERY = 120  # per city-category combo

APOLLO_API_KEY = ""  # Set via env var APOLLO_API_KEY

OUTPUT_DIR = "output"
RAW_DIR = f"{OUTPUT_DIR}/raw"
ENRICHED_DIR = f"{OUTPUT_DIR}/enriched"
EXPORT_DIR = f"{OUTPUT_DIR}/exports"
```

- [ ] **Step 4: Create __init__.py (empty)**

```python
```

- [ ] **Step 5: Create output directory structure**

Run: `mkdir -p output/raw output/enriched output/exports`
Expected: Directories created

- [ ] **Step 6: Commit**

```bash
git add config.py requirements.txt __init__.py
git commit -m "feat: project setup with config, requirements, directory structure"
```

---

### Task 2: Scraper — Discovery Layer

**Files:**
- Create: `scraper.py`
- Create: `tests/test_scraper.py`

- [ ] **Step 1: Write failing test for scraper**

```python
import pytest
from scraper import build_queries, filter_no_website, deduplicate_leads

def test_build_queries_generates_all_combinations():
    queries = build_queries()
    # 11 cities x 8 categories = 88
    assert len(queries) == 88
    assert any("cafe" in q["query"] and "Mumbai" in q["query"] for q in queries)
    assert any("electrician" in q["query"] and "Sydney" in q["query"] for q in queries)

def test_filter_no_website_removes_businesses_with_websites():
    leads = [
        {"name": "Cafe A", "website": "https://cafea.com"},
        {"name": "Cafe B", "website": None},
        {"name": "Cafe C", "website": ""},
        {"name": "Cafe D", "website": "https://facebook.com/cafed"},
    ]
    result = filter_no_website(leads)
    assert len(result) == 2
    assert all(r["name"] in ["Cafe B", "Cafe C"] for r in result)

def test_deduplicate_leads_removes_duplicates():
    leads = [
        {"place_id": "abc", "name": "Cafe A"},
        {"place_id": "abc", "name": "Cafe A"},
        {"place_id": "def", "name": "Cafe B"},
    ]
    result = deduplicate_leads(leads)
    assert len(result) == 2

def test_filter_excludes_social_only_websites():
    leads = [
        {"name": "Cafe E", "website": "https://instagram.com/cafee"},
        {"name": "Cafe F", "website": "https://facebook.com/cafeF"},
        {"name": "Cafe G", "website": "https://www.yelp.com/cafeG"},
        {"name": "Cafe H", "website": None},
    ]
    result = filter_no_website(leads)
    assert len(result) == 4  # all 4 are "no real website"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_scraper.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scraper'`

- [ ] **Step 3: Implement scraper.py**

```python
import json
import os
import asyncio
import logging
from pathlib import Path

from config import (
    CITIES, CATEGORIES, SEARCH_TEMPLATES, MAX_RESULTS_PER_QUERY,
    RAW_DIR, OUTPUT_DIR,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SOCIAL_DOMAINS = [
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "yelp.com", "justdial.com", "zomato.com",
    "swiggy.com", "uber.com", "google.com", "maps.google.com",
    "tripadvisor.com", "foursquare.com", "burpy.com",
    "bookmyshow.com", "indiamart.com", "sulekha.com",
    "gumtree.com", "truelocal.com.au", "yellowpages.com.au",
]


def build_queries():
    """Generate search queries for all city-category combinations."""
    queries = []
    for country, city_list in CITIES.items():
        for city in city_list:
            for category in CATEGORIES:
                template = SEARCH_TEMPLATES.get(category, "{category} in {city}")
                query = template.format(category=category, city=city)
                queries.append({
                    "query": query,
                    "city": city,
                    "country": country,
                    "category": category,
                })
    return queries


def is_social_website(url):
    """Check if URL is a social/directory listing, not a real business website."""
    if not url:
        return True
    url_lower = url.lower()
    return any(domain in url_lower for domain in SOCIAL_DOMAINS)


def filter_no_website(leads):
    """Filter leads that have no website or only social/directory listings."""
    return [
        lead for lead in leads
        if is_social_website(lead.get("website"))
    ]


def deduplicate_leads(leads):
    """Remove duplicate leads based on place_id."""
    seen = set()
    unique = []
    for lead in leads:
        pid = lead.get("place_id") or lead.get("name", "") + lead.get("address", "")
        if pid not in seen:
            seen.add(pid)
            unique.append(lead)
    return unique


async def scrape_city_category(query_info, max_results=MAX_RESULTS_PER_QUERY):
    """Scrape Google Maps for a single city-category query."""
    try:
        from gmaps_scraper import scrape_search

        results = await scrape_search(
            query=query_info["query"],
            max_results=max_results,
        )
        leads = []
        for r in results:
            lead = {
                "business_name": r.get("name", ""),
                "phone": r.get("phone", ""),
                "website": r.get("website", None),
                "address": r.get("address", ""),
                "category": query_info["category"],
                "city": query_info["city"],
                "country": query_info["country"],
                "maps_url": r.get("url", ""),
                "place_id": r.get("place_id", ""),
                "rating": r.get("rating", None),
                "review_count": r.get("reviews", None),
                "latitude": r.get("latitude", None),
                "longitude": r.get("longitude", None),
            }
            leads.append(lead)
        log.info(f"Scraped {len(leads)} results for '{query_info['query']}'")
        return leads
    except Exception as e:
        log.error(f"Scraping failed for '{query_info['query']}': {e}")
        return []


async def run_all_scrapes():
    """Run scraper for all city-category combinations."""
    queries = build_queries()
    all_leads = []
    os.makedirs(RAW_DIR, exist_ok=True)

    for i, qi in enumerate(queries):
        log.info(f"[{i+1}/{len(queries)}] Scraping: {qi['query']}")
        leads = await scrape_city_category(qi)
        leads = deduplicate_leads(leads)
        leads = filter_no_website(leads)

        # Save per-query raw results
        safe_name = qi["query"].replace(" ", "_").replace(",", "")
        out_path = os.path.join(RAW_DIR, f"{safe_name}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)

        all_leads.extend(leads)
        log.info(f"  → {len(leads)} no-website leads found")

        # Rate limit between queries
        await asyncio.sleep(3)

    # Save combined raw results
    all_leads = deduplicate_leads(all_leads)
    combined_path = os.path.join(RAW_DIR, "all_leads_raw.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_leads, f, ensure_ascii=False, indent=2)

    log.info(f"Total no-website leads: {len(all_leads)}")
    return all_leads


if __name__ == "__main__":
    asyncio.run(run_all_scrapes())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_scraper.py -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add scraper.py tests/test_scraper.py
git commit -m "feat: add scraper with query builder, no-website filter, dedup"
```

---

### Task 3: Enricher — Contact Enrichment Layer

**Files:**
- Create: `enricher.py`
- Create: `tests/test_enricher.py`

- [ ] **Step 1: Write failing tests for enricher**

```python
import pytest
from enricher import guess_email, verify_email_mx, enrich_with_apollo

def test_guess_email_generates_common_patterns():
    patterns = guess_email("Blue Sky Cafe", "blueskycafe.com")
    assert "info@blueskycafe.com" in patterns
    assert "contact@blueskycafe.com" in patterns
    assert "hello@blueskycafe.com" in patterns

def test_guess_email_handles_empty_domain():
    patterns = guess_email("Blue Sky Cafe", None)
    assert patterns == []

def test_verify_email_mx_returns_bool():
    # This test may vary by network, just check it returns bool
    result = verify_email_mx("gmail.com")
    assert isinstance(result, bool)

def test_enrich_with_apollo_handles_missing_key():
    leads = [{"business_name": "Test Cafe", "phone": "123456"}]
    result = enrich_with_apollo(leads, api_key="")
    # Should return leads unchanged when no API key
    assert result == leads
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_enricher.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'enricher'`

- [ ] **Step 3: Implement enricher.py**

```python
import json
import logging
import os
import re

import dns.resolver
import requests

from config import ENRICHED_DIR, APOLLO_API_KEY

log = logging.getLogger(__name__)

COMMON_EMAIL_PREFIXES = ["info", "contact", "hello", "bookings", "admin", "support", "enquiry"]


def guess_email(business_name, domain):
    """Generate common email patterns for a business domain."""
    if not domain:
        return []
    clean_domain = domain.lower().strip()
    if clean_domain.startswith("www."):
        clean_domain = clean_domain[4:]
    if not clean_domain or "." not in clean_domain:
        return []
    return [f"{prefix}@{clean_domain}" for prefix in COMMON_EMAIL_PREFIXES]


def verify_email_mx(domain):
    """Check if domain has valid MX records (email-capable)."""
    try:
        records = dns.resolver.resolve(domain, "MX")
        return len(records) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, Exception):
        return False


def extract_domain_from_website(url):
    """Extract registrable domain from a URL."""
    if not url:
        return None
    # Remove protocol
    domain = re.sub(r"^https?://(www\.)?", "", url)
    # Remove path
    domain = domain.split("/")[0]
    return domain if "." in domain else None


def enrich_with_apollo(leads, api_key=None):
    """Enrich top leads using Apollo People/Company Match API.
    Uses free tier: 100 lead credits + 160 phone credits.
    Only enriches leads that lack email.
    """
    key = api_key or APOLLO_API_KEY or os.environ.get("APOLLO_API_KEY", "")
    if not key:
        log.warning("No Apollo API key — skipping Apollo enrichment")
        return leads

    needs_email = [l for l in leads if not l.get("email")]
    # Free tier: max 100 credits — pick top leads by rating
    top_leads = sorted(needs_email, key=lambda x: x.get("rating") or 0, reverse=True)[:100]

    for lead in top_leads:
        try:
            resp = requests.post(
                "https://api.apollo.io/v1/people/match",
                headers={"Cache-Control": "no-cache", "Content-Type": "application/json"},
                params={"api_key": key},
                json={
                    "name": lead.get("business_name", ""),
                    "organization_name": lead.get("business_name", ""),
                    "domain": extract_domain_from_website(lead.get("website", "")),
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json().get("person", {})
                if data.get("email"):
                    lead["email"] = data["email"]
                    lead["email_source"] = "apollo"
                if data.get("phone") and not lead.get("phone"):
                    lead["phone"] = data.get("phone")
                    lead["phone_source"] = "apollo"
        except Exception as e:
            log.warning(f"Apollo enrichment failed for {lead.get('business_name')}: {e}")

    return leads


def enrich_leads(leads):
    """Full enrichment pipeline: guess emails, verify MX, Apollo enrichment."""
    os.makedirs(ENRICHED_DIR, exist_ok=True)
    enriched = []

    for lead in leads:
        domain = extract_domain_from_website(lead.get("website", ""))
        if domain and verify_email_mx(domain):
            lead["guessed_emails"] = guess_email(lead.get("business_name", ""), domain)
            lead["domain_has_mx"] = True
        else:
            lead["guessed_emails"] = []
            lead["domain_has_mx"] = False
        enriched.append(lead)

    # Apollo enrichment for top leads without email
    enriched = enrich_with_apollo(enriched)

    # Save enriched results
    out_path = os.path.join(ENRICHED_DIR, "all_leads_enriched.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    log.info(f"Enriched {len(enriched)} leads")
    return enriched


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raw_path = os.path.join("output", "raw", "all_leads_raw.json")
    if os.path.exists(raw_path):
        with open(raw_path) as f:
            leads = json.load(f)
        enrich_leads(leads)
    else:
        log.error("No raw leads found. Run scraper first.")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_enricher.py -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add enricher.py tests/test_enricher.py
git commit -m "feat: add enricher with email guessing, MX verify, Apollo integration"
```

---

### Task 4: Exporter — CSV Export + Outreach Templates

**Files:**
- Create: `exporter.py`
- Create: `tests/test_exporter.py`
- Create: `templates/cold_call.txt`
- Create: `templates/email.txt`

- [ ] **Step 1: Write failing tests for exporter**

```python
import os
import pytest
import pandas as pd
from exporter import export_csv, generate_city_summary

def test_export_csv_creates_file(tmp_path):
    leads = [
        {"business_name": "Cafe A", "phone": "123", "email": "a@b.com", "city": "Mumbai",
         "category": "cafe", "address": "Addr A", "maps_url": "http://maps/a",
         "has_website": False, "rating": 4.5, "review_count": 100},
        {"business_name": "Cafe B", "phone": "456", "email": "", "city": "Mumbai",
         "category": "cafe", "address": "Addr B", "maps_url": "http://maps/b",
         "has_website": False, "rating": 3.0, "review_count": 20},
    ]
    out_dir = str(tmp_path)
    filepath = export_csv(leads, "Mumbai", out_dir)
    assert os.path.exists(filepath)
    df = pd.read_csv(filepath)
    assert len(df) == 2
    # Sorted: phone+email leads first
    assert df.iloc[0]["business_name"] == "Cafe A"

def test_generate_city_summary_returns_dict():
    leads = [
        {"business_name": "Cafe A", "phone": "123", "email": "a@b.com",
         "city": "Mumbai", "category": "cafe", "has_website": False, "rating": 4.5},
        {"business_name": "Cafe B", "phone": "", "email": "",
         "city": "Mumbai", "category": "bakery", "has_website": False, "rating": None},
    ]
    summary = generate_city_summary(leads, "Mumbai")
    assert summary["city"] == "Mumbai"
    assert summary["total_leads"] == 2
    assert summary["with_phone"] == 1
    assert summary["with_email"] == 1
    assert "cafe" in summary["by_category"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_exporter.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'exporter'`

- [ ] **Step 3: Implement exporter.py**

```python
import json
import logging
import os
from collections import Counter

import pandas as pd

from config import EXPORT_DIR

log = logging.getLogger(__name__)

CSV_COLUMNS = [
    "business_name", "phone", "email", "guessed_emails", "city", "category",
    "address", "maps_url", "has_website", "rating", "review_count",
    "domain_has_mx", "email_source", "phone_source",
]


def sort_leads_for_outreach(leads):
    """Sort leads: phone+email first, then phone only, then email only, then neither."""
    def score(lead):
        has_phone = 1 if lead.get("phone") else 0
        has_email = 1 if lead.get("email") else 0
        rating = lead.get("rating") or 0
        reviews = lead.get("review_count") or 0
        return (has_phone * 1000) + (has_email * 500) + (rating * 10) + min(reviews, 100)

    return sorted(leads, key=score, reverse=True)


def export_csv(leads, city, output_dir=None):
    """Export leads for a city to CSV, sorted by outreach priority."""
    out_dir = output_dir or EXPORT_DIR
    os.makedirs(out_dir, exist_ok=True)

    city_leads = [l for l in leads if l.get("city") == city]
    city_leads = sort_leads_for_outreach(city_leads)

    # Normalize: ensure all columns exist, flatten guessed_emails
    rows = []
    for lead in city_leads:
        row = {}
        for col in CSV_COLUMNS:
            val = lead.get(col, "")
            if col == "guessed_emails" and isinstance(val, list):
                val = "; ".join(val) if val else ""
            if col == "has_website":
                val = bool(lead.get("website"))
            row[col] = val
        rows.append(row)

    df = pd.DataFrame(rows, columns=CSV_COLUMNS)
    safe_city = city.lower().replace(" ", "_")
    filepath = os.path.join(out_dir, f"leads_{safe_city}.csv")
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    log.info(f"Exported {len(rows)} leads to {filepath}")
    return filepath


def generate_city_summary(leads, city):
    """Generate summary stats for a city's leads."""
    city_leads = [l for l in leads if l.get("city") == city]
    by_category = dict(Counter(l.get("category", "unknown") for l in city_leads))

    return {
        "city": city,
        "total_leads": len(city_leads),
        "with_phone": sum(1 for l in city_leads if l.get("phone")),
        "with_email": sum(1 for l in city_leads if l.get("email")),
        "by_category": by_category,
    }


def export_all_cities(leads):
    """Export CSV per city + summary file."""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    cities = set(l.get("city") for l in leads)
    summaries = []

    for city in sorted(cities):
        export_csv(leads, city)
        summaries.append(generate_city_summary(leads, city))

    # Save summary
    summary_path = os.path.join(EXPORT_DIR, "pipeline_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summaries, f, indent=2)

    log.info(f"Exported {len(cities)} city files. Summary: {summary_path}")
    return summaries


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    enriched_path = os.path.join("output", "enriched", "all_leads_enriched.json")
    if os.path.exists(enriched_path):
        with open(enriched_path) as f:
            leads = json.load(f)
        export_all_cities(leads)
    else:
        log.error("No enriched leads found. Run enricher first.")
```

- [ ] **Step 4: Create outreach templates**

`templates/cold_call.txt`:

```
COLD CALL SCRIPT — [CATEGORY] — [CITY]

Hi, is this [BUSINESS_NAME]?

I'm [YOUR_NAME] from ShashankIdea. I noticed you don't have a website
for your [CATEGORY] business — a lot of customers search online before
visiting, and without a site you're invisible to them.

We build simple, fast websites for local businesses like yours.
No complicated setup, you get a professional site with your menu,
hours, contact info, and a Google Maps link — all in 3-5 days.

It starts at [PRICE]. Can I send you a few examples of what
we've built for other [CATEGORY] businesses in [CITY]?

[If yes]: Great, what's the best email to send that to?
[If no]: No problem! Here's my number — [YOUR_PHONE].
         Feel free to call if you change your mind.
         Have a great day!
```

`templates/email.txt`:

```
Subject: Get your [CATEGORY] business online — simple website in 3 days

Hi [BUSINESS_NAME] team,

I noticed your [CATEGORY] in [CITY] doesn't have a website yet.
Customers are searching for businesses like yours online every day —
without a site, they're finding your competitors instead.

We build clean, fast websites for local businesses:
- Your menu / services, hours, and contact info
- Google Maps integration so customers find you easily
- Mobile-friendly design that looks great on any phone
- Live in 3-5 business days

Packages start at [PRICE] — no ongoing fees, no complicated setup.

See examples of our work: [PORTFOLIO_LINK]

Interested? Reply to this email or call me at [YOUR_PHONE].

Best,
[YOUR_NAME]
ShashankIdea
[YOUR_PHONE] | [YOUR_EMAIL]
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_exporter.py -v`
Expected: 2 PASSED

- [ ] **Step 6: Commit**

```bash
git add exporter.py tests/test_exporter.py templates/
git commit -m "feat: add exporter with CSV export, outreach priority sort, templates"
```

---

### Task 5: Pipeline Orchestrator

**Files:**
- Create: `pipeline.py`
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing test for pipeline**

```python
import pytest
from pipeline import Pipeline

def test_pipeline_init_creates_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr("config.OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setattr("config.RAW_DIR", str(tmp_path / "output" / "raw"))
    monkeypatch.setattr("config.ENRICHED_DIR", str(tmp_path / "output" / "enriched"))
    monkeypatch.setattr("config.EXPORT_DIR", str(tmp_path / "output" / "exports"))
    p = Pipeline()
    assert os.path.exists(str(tmp_path / "output"))

def test_pipeline_load_raw_leads(tmp_path, monkeypatch):
    import json, os
    raw_dir = str(tmp_path / "raw")
    os.makedirs(raw_dir)
    leads = [{"business_name": "Test", "phone": "123"}]
    with open(os.path.join(raw_dir, "all_leads_raw.json"), "w") as f:
        json.dump(leads, f)
    monkeypatch.setattr("config.RAW_DIR", raw_dir)
    p = Pipeline()
    loaded = p.load_raw()
    assert len(loaded) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_pipeline.py -v`
Expected: FAIL

- [ ] **Step 3: Implement pipeline.py**

```python
import asyncio
import json
import logging
import os

from config import OUTPUT_DIR, RAW_DIR, ENRICHED_DIR, EXPORT_DIR
from scraper import run_all_scrapes, filter_no_website, deduplicate_leads
from enricher import enrich_leads
from exporter import export_all_cities

log = logging.getLogger(__name__)


class Pipeline:
    def __init__(self):
        for d in [OUTPUT_DIR, RAW_DIR, ENRICHED_DIR, EXPORT_DIR]:
            os.makedirs(d, exist_ok=True)

    def run_discovery(self):
        """Step 1: Scrape Google Maps for all city-category combos."""
        log.info("=== STEP 1: Discovery ===")
        leads = asyncio.run(run_all_scrapes())
        log.info(f"Discovery complete: {len(leads)} no-website leads")
        return leads

    def load_raw(self):
        """Load previously scraped raw leads."""
        raw_path = os.path.join(RAW_DIR, "all_leads_raw.json")
        with open(raw_path) as f:
            return json.load(f)

    def run_enrichment(self, leads=None):
        """Step 2: Enrich leads with emails and verified contacts."""
        log.info("=== STEP 2: Enrichment ===")
        if leads is None:
            leads = self.load_raw()
        enriched = enrich_leads(leads)
        log.info(f"Enrichment complete: {len(enriched)} leads")
        return enriched

    def load_enriched(self):
        """Load previously enriched leads."""
        enriched_path = os.path.join(ENRICHED_DIR, "all_leads_enriched.json")
        with open(enriched_path) as f:
            return json.load(f)

    def run_export(self, leads=None):
        """Step 3: Export CSVs per city + outreach templates."""
        log.info("=== STEP 3: Export ===")
        if leads is None:
            leads = self.load_enriched()
        summaries = export_all_cities(leads)
        log.info("Export complete")
        for s in summaries:
            log.info(f"  {s['city']}: {s['total_leads']} leads "
                     f"({s['with_phone']} phones, {s['with_email']} emails)")
        return summaries

    def run_full(self):
        """Run all 3 steps sequentially."""
        leads = self.run_discovery()
        enriched = self.run_enrichment(leads)
        summaries = self.run_export(enriched)
        return summaries

    def run_from_raw(self):
        """Run steps 2-3 using previously scraped data."""
        leads = self.load_raw()
        enriched = self.run_enrichment(leads)
        summaries = self.run_export(enriched)
        return summaries

    def run_from_enriched(self):
        """Run step 3 using previously enriched data."""
        leads = self.load_enriched()
        return self.run_export(leads)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    import sys

    p = Pipeline()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "discover":
            p.run_discovery()
        elif cmd == "enrich":
            p.run_from_raw()
        elif cmd == "export":
            p.run_from_enriched()
        elif cmd == "full":
            p.run_full()
        else:
            print("Usage: python pipeline.py [discover|enrich|export|full]")
    else:
        print("Usage: python pipeline.py [discover|enrich|export|full]")
        print("  discover  — Scrape Google Maps (takes 30-60 min)")
        print("  enrich    — Enrich raw leads with emails")
        print("  export    — Export CSVs from enriched data")
        print("  full      — Run all 3 steps")
```

- [ ] **Step 4: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline.py tests/test_pipeline.py
git commit -m "feat: add pipeline orchestrator with discover/enrich/export steps"
```

---

### Task 6: Integration Test + First Run (Single City)

**Files:**
- Modify: `tests/test_integration.py` (create)

- [ ] **Step 1: Write integration test for single-city scrape**

```python
import pytest
from unittest.mock import patch, AsyncMock
from pipeline import Pipeline


@pytest.mark.asyncio
async def test_single_city_pipeline():
    """Test pipeline with mocked scraper for Mumbai cafes only."""
    mock_results = [
        {
            "name": "Test Cafe Mumbai",
            "phone": "+91-9876543210",
            "website": None,
            "address": "Bandstand, Mumbai",
            "url": "https://maps.google.com/test",
            "place_id": "test_place_1",
            "rating": 4.3,
            "reviews": 150,
            "latitude": 19.07,
            "longitude": 72.87,
        },
        {
            "name": "Cafe With Website",
            "phone": "+91-9876543211",
            "website": "https://cafewithwebsite.com",
            "address": "Andheri, Mumbai",
            "url": "https://maps.google.com/test2",
            "place_id": "test_place_2",
            "rating": 4.0,
            "reviews": 50,
            "latitude": 19.12,
            "longitude": 72.84,
        },
    ]

    with patch("scraper.scrape_search", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = mock_results
        from scraper import scrape_city_category
        leads = await scrape_city_category({
            "query": "cafe in Mumbai",
            "city": "Mumbai",
            "country": "india",
            "category": "cafe",
        })

    # Only the no-website lead should survive after filtering
    from scraper import filter_no_website
    no_website = filter_no_website(leads)
    assert len(no_website) == 1
    assert no_website[0]["business_name"] == "Test Cafe Mumbai"
    assert no_website[0]["phone"] == "+91-9876543210"
```

- [ ] **Step 2: Run integration test**

Run: `pytest tests/test_integration.py -v`
Expected: 1 PASSED

- [ ] **Step 3: Test single-city live scrape (manual, Mumbai cafes only)**

```bash
python -c "
import asyncio
from scraper import scrape_city_category
leads = asyncio.run(scrape_city_category({'query': 'cafe in Mumbai', 'city': 'Mumbai', 'country': 'india', 'category': 'cafe'}, max_results=10))
from scraper import filter_no_website
no_web = filter_no_website(leads)
print(f'Total scraped: {len(leads)}, No website: {len(no_web)}')
for l in no_web[:5]:
    print(f'  {l[\"business_name\"]} | {l[\"phone\"]} | {l.get(\"website\", \"NONE\")}')
"
```

Expected: Prints 5-10 leads, most with phone numbers, website=None

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test for single-city pipeline"
```

---

### Task 7: Full Pipeline Run + Verification

**Files:**
- Modify: `config.py` (tune max_results if needed)

- [ ] **Step 1: Run full discovery pipeline**

Run: `python pipeline.py discover`
Expected: Scrapes all 88 queries, saves raw JSON to `output/raw/all_leads_raw.json`. Takes 30-60 minutes due to rate limiting.

- [ ] **Step 2: Check raw lead counts**

```bash
python -c "
import json
with open('output/raw/all_leads_raw.json') as f:
    leads = json.load(f)
print(f'Total leads: {len(leads)}')
from collections import Counter
by_city = Counter(l['city'] for l in leads)
for city, count in sorted(by_city.items()):
    print(f'  {city}: {count}')
by_cat = Counter(l['category'] for l in leads)
for cat, count in sorted(by_cat.items()):
    print(f'  {cat}: {count}')
with_phone = sum(1 for l in leads if l.get('phone'))
print(f'With phone: {with_phone}/{len(leads)} ({100*with_phone//max(len(leads),1)}%)')
"
```

Expected: 2,200-5,500 total leads, 200-500 per city, 70%+ with phone

- [ ] **Step 3: Run enrichment**

Run: `python pipeline.py enrich`
Expected: Adds guessed emails, verifies MX records, enriches top 100 via Apollo

- [ ] **Step 4: Run export**

Run: `python pipeline.py export`
Expected: Generates CSV per city in `output/exports/`, prints summary

- [ ] **Step 5: Verify CSV output**

```bash
head -5 output/exports/leads_mumbai.csv
```

Expected: CSV with columns: business_name, phone, email, city, category, etc.

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "feat: full pipeline verified — discovery, enrichment, export working"
```