"""Pipeline Orchestrator — coordinates discovery, enrichment, and export.

Provides a Pipeline class that can run the full lead-gen flow or resume
from intermediate checkpoints (raw data, enriched data).
"""

import asyncio
import json
import logging
import os
import sys

from config import OUTPUT_DIR, RAW_DIR, ENRICHED_DIR, EXPORT_DIR
from scraper import run_all_scrapes
from enricher import enrich_leads
from exporter import export_all_cities

log = logging.getLogger(__name__)


class Pipeline:
    """Orchestrates the 3-step SME lead generation pipeline.

    Steps:
        1. Discovery  — scrape Google Maps for businesses without websites
        2. Enrichment — enrich leads with emails and verified contacts
        3. Export      — generate CSVs per city + outreach templates

    Each step saves results to disk so the pipeline can resume from
    any intermediate checkpoint.
    """

    def __init__(self):
        for d in [OUTPUT_DIR, RAW_DIR, ENRICHED_DIR, EXPORT_DIR]:
            os.makedirs(d, exist_ok=True)

    # ── Step 1: Discovery ────────────────────────────────────────────────

    def run_discovery(self):
        """Step 1: Scrape Google Maps for all city-category combos.

        Returns:
            list[dict]: Raw leads collected across all queries.
        """
        log.info("=== STEP 1: Discovery ===")
        leads = asyncio.run(run_all_scrapes())
        log.info("Discovery complete: %d leads", len(leads))
        return leads

    # ── Loaders ──────────────────────────────────────────────────────────

    def load_raw(self):
        """Load previously scraped raw leads from disk.

        Returns:
            list[dict]: Raw leads from RAW_DIR/all_leads_raw.json.

        Raises:
            FileNotFoundError: If the raw leads file does not exist.
        """
        raw_path = os.path.join(RAW_DIR, "all_leads_raw.json")
        with open(raw_path) as f:
            return json.load(f)

    def load_enriched(self):
        """Load previously enriched leads from disk.

        Returns:
            list[dict]: Enriched leads from ENRICHED_DIR/all_leads_enriched.json.

        Raises:
            FileNotFoundError: If the enriched leads file does not exist.
        """
        enriched_path = os.path.join(ENRICHED_DIR, "all_leads_enriched.json")
        with open(enriched_path) as f:
            return json.load(f)

    # ── Step 2: Enrichment ────────────────────────────────────────────────

    def run_enrichment(self, leads=None):
        """Step 2: Enrich leads with emails and verified contacts.

        Args:
            leads: Optional list of raw leads. If None, loads from disk.

        Returns:
            list[dict]: Enriched leads with email/domain/MX fields.
        """
        log.info("=== STEP 2: Enrichment ===")
        if leads is None:
            leads = self.load_raw()
        enriched = enrich_leads(leads)
        log.info("Enrichment complete: %d leads", len(enriched))
        return enriched

    # ── Step 3: Export ────────────────────────────────────────────────────

    def run_export(self, leads=None):
        """Step 3: Export CSVs per city + outreach templates.

        Args:
            leads: Optional list of enriched leads. If None, loads from disk.

        Returns:
            dict: Summary keyed by city name, each with total_leads,
                  with_phone, with_email, and by_category counts.
        """
        log.info("=== STEP 3: Export ===")
        if leads is None:
            leads = self.load_enriched()
        summaries = export_all_cities(leads)
        log.info("Export complete")
        for city, s in summaries.items():
            log.info("  %s: %s leads (%s phones, %s emails)",
                     city, s["total_leads"], s["with_phone"], s["with_email"])
        return summaries

    # ── Composite runners ────────────────────────────────────────────────

    def run_full(self):
        """Run all 3 steps sequentially: discovery -> enrichment -> export.

        Returns:
            dict: Export summaries keyed by city.
        """
        leads = self.run_discovery()
        enriched = self.run_enrichment(leads)
        summaries = self.run_export(enriched)
        return summaries

    def run_from_raw(self):
        """Run steps 2-3 using previously scraped raw data.

        Returns:
            dict: Export summaries keyed by city.
        """
        leads = self.load_raw()
        enriched = self.run_enrichment(leads)
        summaries = self.run_export(enriched)
        return summaries

    def run_from_enriched(self):
        """Run step 3 using previously enriched data.

        Returns:
            dict: Export summaries keyed by city.
        """
        leads = self.load_enriched()
        return self.run_export(leads)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

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