"""Integration tests for the full SME lead-gen pipeline.

Tests the pipeline with mocked external dependencies (Apify Google Maps Scraper,
DNS resolver, Apollo API) to verify end-to-end data flow across modules.
"""

import os

import pytest
from unittest.mock import patch, MagicMock

from scraper import scrape_city_category, filter_no_website, deduplicate_leads
from enricher import enrich_leads
from exporter import export_all_cities, sort_leads_for_outreach


# ── Fixtures ──────────────────────────────────────────────────────────────

# Sample Apify result items (matching the Apify Google Maps Scraper schema)
APIFY_ITEM_MUMBAI_CAFE_1 = {
    "title": "Test Cafe Mumbai",
    "phone": "+91-9876543210",
    "website": None,
    "address": "Bandstand, Mumbai",
    "url": "https://maps.google.com/test_place_1",
    "placeId": "test_place_1",
    "totalScore": 4.3,
    "reviewsCount": 150,
    "location": {"lat": 19.07, "lng": 72.87},
}

APIFY_ITEM_MUMBAI_CAFE_2 = {
    "title": "Cafe With Website",
    "phone": "+91-9876543211",
    "website": "https://cafewithwebsite.com",
    "address": "Andheri, Mumbai",
    "url": "https://maps.google.com/test_place_2",
    "placeId": "test_place_2",
    "totalScore": 4.0,
    "reviewsCount": 50,
    "location": {"lat": 19.12, "lng": 72.84},
}


def _make_mock_apify_client(items):
    """Create a mock ApifyClient that returns the given items from a dataset."""
    mock_dataset = MagicMock()
    mock_dataset.iterate_items = MagicMock(return_value=iter(items))

    mock_run = {"defaultDatasetId": "dataset_123"}

    mock_actor = MagicMock()
    mock_actor.call = MagicMock(return_value=mock_run)

    mock_client = MagicMock()
    mock_client.actor = MagicMock(return_value=mock_actor)
    mock_client.dataset = MagicMock(return_value=mock_dataset)

    return mock_client


# ── Single-city pipeline: scraper → filter ────────────────────────────────

class TestSingleCityPipeline:
    """Test pipeline with mocked Apify scraper for Mumbai cafes."""

    def test_scrape_city_category_returns_leads(self):
        """scrape_city_category should return leads with correct schema."""
        mock_client = _make_mock_apify_client([APIFY_ITEM_MUMBAI_CAFE_1])

        with patch("scraper.APIFY_TOKEN", "test_token"), \
             patch("apify_client.ApifyClient", return_value=mock_client):
            leads = scrape_city_category({
                "query": "cafe in Mumbai",
                "city": "Mumbai",
                "country": "india",
                "category": "cafe",
            })

        assert len(leads) == 1
        lead = leads[0]
        assert lead["business_name"] == "Test Cafe Mumbai"
        assert lead["phone"] == "+91-9876543210"
        assert lead["website"] is None
        assert lead["address"] == "Bandstand, Mumbai"
        assert lead["category"] == "cafe"
        assert lead["city"] == "Mumbai"
        assert lead["country"] == "india"
        assert lead["place_id"] == "test_place_1"
        assert lead["rating"] == 4.3
        assert lead["review_count"] == 150

    def test_scrape_city_category_handles_no_result(self):
        """scrape_city_category should return empty list when Apify returns no items."""
        mock_client = _make_mock_apify_client([])

        with patch("scraper.APIFY_TOKEN", "test_token"), \
             patch("apify_client.ApifyClient", return_value=mock_client):
            leads = scrape_city_category({
                "query": "cafe in Mumbai",
                "city": "Mumbai",
                "country": "india",
                "category": "cafe",
            })

        assert leads == []

    def test_filter_no_website_after_scraping(self):
        """Filter leads to find businesses without real websites."""
        mock_client = _make_mock_apify_client(
            [APIFY_ITEM_MUMBAI_CAFE_1, APIFY_ITEM_MUMBAI_CAFE_2]
        )

        with patch("scraper.APIFY_TOKEN", "test_token"), \
             patch("apify_client.ApifyClient", return_value=mock_client):
            all_leads = scrape_city_category({
                "query": "cafe in Mumbai",
                "city": "Mumbai",
                "country": "india",
                "category": "cafe",
            })

        no_website = filter_no_website(all_leads)
        assert len(no_website) == 1
        assert no_website[0]["business_name"] == "Test Cafe Mumbai"
        assert no_website[0]["phone"] == "+91-9876543210"

    def test_filter_excludes_social_only_websites(self):
        """Businesses with only social-media listings should be filtered out."""
        social_cafe_item = {
            "title": "Instagram Cafe",
            "phone": "+91-9876543212",
            "website": "https://instagram.com/instacafe",
            "address": "Juhu, Mumbai",
            "url": "https://maps.google.com/test_place_3",
            "placeId": "test_place_3",
            "totalScore": 3.8,
            "reviewsCount": 30,
            "location": {"lat": 19.10, "lng": 72.83},
        }
        mock_client = _make_mock_apify_client([social_cafe_item])

        with patch("scraper.APIFY_TOKEN", "test_token"), \
             patch("apify_client.ApifyClient", return_value=mock_client):
            leads = scrape_city_category({
                "query": "cafe in Mumbai",
                "city": "Mumbai",
                "country": "india",
                "category": "cafe",
            })

        no_website = filter_no_website(leads)
        assert len(no_website) == 1
        assert no_website[0]["business_name"] == "Instagram Cafe"


# ── Multi-step pipeline: scraper → enricher → exporter ───────────────────

class TestMultiStepPipeline:
    """Test the full pipeline flow with all mocked external dependencies."""

    def test_scraper_to_enricher_to_exporter(self, tmp_path):
        """End-to-end: scrape → enrich → export with mocked externals."""
        # Step 1: Produce leads via mocked Apify
        mock_client = _make_mock_apify_client(
            [APIFY_ITEM_MUMBAI_CAFE_1, APIFY_ITEM_MUMBAI_CAFE_2]
        )

        with patch("scraper.APIFY_TOKEN", "test_token"), \
             patch("apify_client.ApifyClient", return_value=mock_client):
            all_leads = scrape_city_category({
                "query": "cafe in Mumbai",
                "city": "Mumbai",
                "country": "india",
                "category": "cafe",
            })

        assert len(all_leads) == 2

        # Step 2: Enrich with mocked MX verification and no Apollo
        with patch("enricher.verify_email_mx", return_value=True), \
             patch("enricher.enrich_with_apollo", side_effect=lambda l, **kw: l):
            enriched = enrich_leads(all_leads)

        # Verify enrichment added fields
        for lead in enriched:
            assert "domain" in lead
            assert "mx_valid" in lead
            assert "guessed_emails" in lead

        # Cafe 1 has no website → no domain
        assert enriched[0]["domain"] is None
        assert enriched[0]["mx_valid"] is False
        assert enriched[0]["guessed_emails"] == []

        # Cafe 2 has a website → domain extracted
        assert enriched[1]["domain"] == "cafewithwebsite.com"
        assert enriched[1]["mx_valid"] is True
        assert "info@cafewithwebsite.com" in enriched[1]["guessed_emails"]

        # Step 3: Export to CSV
        export_dir = str(tmp_path / "exports")
        summaries = export_all_cities(enriched, output_dir=export_dir)

        assert "Mumbai" in summaries
        assert summaries["Mumbai"]["total_leads"] == 2
        assert summaries["Mumbai"]["with_phone"] == 2

        # Verify CSV file was created
        csv_path = os.path.join(export_dir, "leads_Mumbai.csv")
        assert os.path.isfile(csv_path)

    def test_sort_leads_priority(self):
        """Leads with both phone and email should be prioritized."""
        leads = [
            {"business_name": "No Contact", "phone": None, "email": None,
             "rating": 5.0, "review_count": 200},
            {"business_name": "Phone Only", "phone": "+91-123", "email": None,
             "rating": 4.0, "review_count": 50},
            {"business_name": "Both Contact", "phone": "+91-456", "email": "a@b.com",
             "rating": 4.5, "review_count": 100},
            {"business_name": "Email Only", "phone": None, "email": "c@d.com",
             "rating": 3.5, "review_count": 30},
        ]
        sorted_leads = sort_leads_for_outreach(leads)

        # Priority: both > phone > email > none
        assert sorted_leads[0]["business_name"] == "Both Contact"
        assert sorted_leads[1]["business_name"] == "Phone Only"
        assert sorted_leads[2]["business_name"] == "Email Only"
        assert sorted_leads[3]["business_name"] == "No Contact"

    def test_deduplication_in_pipeline(self):
        """Duplicate leads from different queries should be deduplicated."""
        leads = [
            {
                "business_name": "Test Cafe",
                "phone": "+91-123",
                "website": None,
                "address": "Mumbai",
                "place_id": "dup_1",
                "rating": 4.0,
                "review_count": 50,
                "category": "cafe",
                "city": "Mumbai",
                "country": "india",
            },
            {
                "business_name": "Test Cafe",
                "phone": "+91-123",
                "website": None,
                "address": "Mumbai",
                "place_id": "dup_1",
                "rating": 4.0,
                "review_count": 50,
                "category": "cafe",
                "city": "Mumbai",
                "country": "india",
            },
            {
                "business_name": "Other Cafe",
                "phone": "+91-456",
                "website": "https://other.com",
                "address": "Delhi",
                "place_id": "unique_1",
                "rating": 3.5,
                "review_count": 20,
                "category": "cafe",
                "city": "Delhi",
                "country": "india",
            },
        ]
        deduped = deduplicate_leads(leads)
        assert len(deduped) == 2
        assert deduped[0]["business_name"] == "Test Cafe"
        assert deduped[1]["business_name"] == "Other Cafe"

    def test_filter_then_enrich_then_export(self, tmp_path):
        """Integration: filter no-website leads → enrich → export."""
        # Simulated scraped leads (matching schema from _map_apify_item_to_lead)
        raw_leads = [
            {
                "business_name": "Cafe No Site",
                "phone": "+91-111",
                "website": None,
                "address": "Mumbai",
                "category": "cafe",
                "city": "Mumbai",
                "country": "india",
                "maps_url": "https://maps.google.com/1",
                "place_id": "p1",
                "rating": 4.5,
                "review_count": 100,
                "latitude": 19.07,
                "longitude": 72.87,
            },
            {
                "business_name": "Cafe With Site",
                "phone": "+91-222",
                "website": "https://cafesite.com",
                "address": "Mumbai",
                "category": "cafe",
                "city": "Mumbai",
                "country": "india",
                "maps_url": "https://maps.google.com/2",
                "place_id": "p2",
                "rating": 4.0,
                "review_count": 80,
                "latitude": 19.08,
                "longitude": 72.88,
            },
            {
                "business_name": "Cafe Facebook Only",
                "phone": "+91-333",
                "website": "https://facebook.com/cafeFB",
                "address": "Mumbai",
                "category": "cafe",
                "city": "Mumbai",
                "country": "india",
                "maps_url": "https://maps.google.com/3",
                "place_id": "p3",
                "rating": 3.8,
                "review_count": 40,
                "latitude": 19.09,
                "longitude": 72.89,
            },
        ]

        # Step 1: Filter
        hot_leads = filter_no_website(raw_leads)
        assert len(hot_leads) == 2
        assert hot_leads[0]["business_name"] == "Cafe No Site"
        assert hot_leads[1]["business_name"] == "Cafe Facebook Only"

        # Step 2: Enrich (with mocked MX and no Apollo)
        with patch("enricher.verify_email_mx", return_value=True), \
             patch("enricher.enrich_with_apollo", side_effect=lambda l, **kw: l):
            enriched = enrich_leads(hot_leads)

        # Cafe No Site has no website → no domain, no guessed emails
        assert enriched[0]["domain"] is None
        assert enriched[0]["mx_valid"] is False
        assert enriched[0]["guessed_emails"] == []

        # Cafe Facebook Only has social website → domain extracted but is
        # facebook.com; enricher doesn't filter social, filter_no_website does
        assert enriched[1]["domain"] == "facebook.com"

        # Step 3: Export
        export_dir = str(tmp_path / "exports")
        summaries = export_all_cities(enriched, output_dir=export_dir)

        assert "Mumbai" in summaries
        assert summaries["Mumbai"]["total_leads"] == 2

        csv_path = os.path.join(export_dir, "leads_Mumbai.csv")
        assert os.path.isfile(csv_path)

        # Verify CSV has content
        with open(csv_path, encoding="utf-8-sig") as f:
            lines = f.readlines()
        # Header + 2 data rows
        assert len(lines) == 3