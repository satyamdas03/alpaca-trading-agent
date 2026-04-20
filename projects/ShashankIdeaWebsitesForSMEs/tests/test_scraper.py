import pytest
from unittest.mock import patch, MagicMock

from scraper import (
    build_queries, filter_no_website, deduplicate_leads,
    is_social_website, SOCIAL_DOMAINS, scrape_city_category,
    _map_apify_item_to_lead, _build_location_string,
)


def test_build_queries_generates_all_combinations():
    queries = build_queries()
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
    # Cafe B (None), Cafe C (empty), Cafe D (social-only) are all "no real website"
    assert len(result) == 3
    assert all(r["name"] in ["Cafe B", "Cafe C", "Cafe D"] for r in result)


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


def test_is_social_website_detects_known_domains():
    """is_social_website returns True for all SOCIAL_DOMAINS."""
    for domain in SOCIAL_DOMAINS:
        assert is_social_website(f"https://{domain}/somepage"), f"Failed for {domain}"
        assert is_social_website(f"https://www.{domain}/somepage"), f"Failed for www.{domain}"
        assert is_social_website(f"http://m.{domain}/page"), f"Failed for m.{domain}"


def test_is_social_website_rejects_real_websites():
    """is_social_website returns False for real business domains."""
    assert not is_social_website("https://cafea.com")
    assert not is_social_website("https://www.mybakery.in")
    assert not is_social_website("http://plumberjoe.com.au")


def test_is_social_website_handles_edge_cases():
    """is_social_website handles None, empty, whitespace correctly."""
    assert not is_social_website(None)
    assert not is_social_website("")
    assert not is_social_website("   ")


def test_build_queries_structure():
    """Each query dict has required keys."""
    queries = build_queries()
    for q in queries:
        assert "query" in q
        assert "city" in q
        assert "category" in q
        assert "country" in q


def test_build_queries_city_counts():
    """6 Indian cities + 5 Australian cities = 11 total cities."""
    queries = build_queries()
    cities = set(q["city"] for q in queries)
    assert len(cities) == 11


def test_deduplicate_leads_fallback_to_name_address():
    """Deduplication falls back to name+address when place_id is missing."""
    leads = [
        {"place_id": None, "name": "Cafe A", "address": "123 Main St"},
        {"place_id": None, "name": "Cafe A", "address": "123 Main St"},
        {"place_id": None, "name": "Cafe A", "address": "456 Other St"},
    ]
    result = deduplicate_leads(leads)
    assert len(result) == 2  # same name+addr deduped, different addr kept


def test_build_location_string_india():
    """Location string for Indian cities includes country name."""
    assert _build_location_string("Mumbai", "india") == "Mumbai, India"
    assert _build_location_string("Delhi", "india") == "Delhi, India"


def test_build_location_string_australia():
    """Location string for Australian cities includes country name."""
    assert _build_location_string("Sydney", "australia") == "Sydney, Australia"


def test_map_apify_item_to_lead_full_fields():
    """Map a full Apify result item to our lead schema."""
    item = {
        "title": "Test Cafe",
        "phone": "+91-9876543210",
        "website": "https://testcafe.com",
        "address": "123 Main St, Mumbai",
        "url": "https://maps.google.com/test_place_1",
        "placeId": "ChIJ_test_place_1",
        "totalScore": 4.3,
        "reviewsCount": 150,
        "location": {"lat": 19.07, "lng": 72.87},
    }
    lead = _map_apify_item_to_lead(item, "Mumbai", "cafe", "india")
    assert lead["business_name"] == "Test Cafe"
    assert lead["phone"] == "+91-9876543210"
    assert lead["website"] == "https://testcafe.com"
    assert lead["address"] == "123 Main St, Mumbai"
    assert lead["category"] == "cafe"
    assert lead["city"] == "Mumbai"
    assert lead["country"] == "india"
    assert lead["maps_url"] == "https://maps.google.com/test_place_1"
    assert lead["place_id"] == "ChIJ_test_place_1"
    assert lead["rating"] == 4.3
    assert lead["review_count"] == 150
    assert lead["latitude"] == 19.07
    assert lead["longitude"] == 72.87


def test_map_apify_item_to_lead_minimal_fields():
    """Map an Apify result with minimal/missing fields."""
    item = {
        "title": "Unknown Place",
    }
    lead = _map_apify_item_to_lead(item, "Sydney", "gym", "australia")
    assert lead["business_name"] == "Unknown Place"
    assert lead["phone"] == ""
    assert lead["website"] is None  # empty string from Apify becomes None
    assert lead["address"] == ""
    assert lead["place_id"] == ""
    assert lead["rating"] is None
    assert lead["review_count"] is None
    assert lead["latitude"] is None
    assert lead["longitude"] is None


def test_scrape_city_category_no_apify_token():
    """scrape_city_category returns empty list with warning when APIFY_TOKEN is not set."""
    with patch("scraper.APIFY_TOKEN", ""):
        result = scrape_city_category({
            "query": "cafe in Mumbai",
            "city": "Mumbai",
            "country": "india",
            "category": "cafe",
        })
    assert result == []


def test_scrape_city_category_with_apify():
    """scrape_city_category calls Apify actor and returns mapped leads."""
    mock_items = [
        {
            "title": "Test Cafe",
            "phone": "+91-9876543210",
            "website": None,
            "address": "Bandstand, Mumbai",
            "url": "https://maps.google.com/test1",
            "placeId": "test_place_1",
            "totalScore": 4.3,
            "reviewsCount": 150,
            "location": {"lat": 19.07, "lng": 72.87},
        },
    ]

    mock_dataset = MagicMock()
    mock_dataset.iterate_items = MagicMock(return_value=iter(mock_items))

    mock_run = {"defaultDatasetId": "dataset_123"}

    mock_actor = MagicMock()
    mock_actor.call = MagicMock(return_value=mock_run)

    mock_client = MagicMock()
    mock_client.actor = MagicMock(return_value=mock_actor)
    mock_client.dataset = MagicMock(return_value=mock_dataset)

    with patch("scraper.APIFY_TOKEN", "test_token"), \
         patch("apify_client.ApifyClient", return_value=mock_client):
        result = scrape_city_category({
            "query": "cafe in Mumbai",
            "city": "Mumbai",
            "country": "india",
            "category": "cafe",
        })

    assert len(result) == 1
    lead = result[0]
    assert lead["business_name"] == "Test Cafe"
    assert lead["phone"] == "+91-9876543210"
    assert lead["website"] is None
    assert lead["address"] == "Bandstand, Mumbai"
    assert lead["category"] == "cafe"
    assert lead["city"] == "Mumbai"
    assert lead["country"] == "india"
    assert lead["place_id"] == "test_place_1"
    assert lead["rating"] == 4.3
    assert lead["review_count"] == 150

    # Verify Apify was called with correct parameters
    mock_actor.call.assert_called_once()
    call_args = mock_actor.call.call_args
    run_input = call_args[1]["run_input"]
    assert run_input["searchStringsArray"] == ["cafe in Mumbai"]
    assert run_input["locationQuery"] == "Mumbai, India"
    assert run_input["countryCode"] == "IN"
    assert run_input["maxCrawledPlacesPerSearch"] == 120


def test_scrape_city_category_handles_apify_error():
    """scrape_city_category returns empty list when Apify raises an error."""
    mock_actor = MagicMock()
    mock_actor.call = MagicMock(side_effect=Exception("Apify API error"))

    mock_client = MagicMock()
    mock_client.actor = MagicMock(return_value=mock_actor)

    with patch("scraper.APIFY_TOKEN", "test_token"), \
         patch("apify_client.ApifyClient", return_value=mock_client):
        result = scrape_city_category({
            "query": "cafe in Mumbai",
            "city": "Mumbai",
            "country": "india",
            "category": "cafe",
        })

    assert result == []


def test_scrape_city_category_respects_max_results():
    """scrape_city_category truncates results to max_results."""
    # Create 5 mock items
    mock_items = [
        {"title": f"Cafe {i}", "phone": "", "website": None, "address": "",
         "url": "", "placeId": f"p{i}", "totalScore": 4.0,
         "reviewsCount": 10, "location": {"lat": 0, "lng": 0}}
        for i in range(5)
    ]

    mock_dataset = MagicMock()
    mock_dataset.iterate_items = MagicMock(return_value=iter(mock_items))

    mock_run = {"defaultDatasetId": "dataset_123"}

    mock_actor = MagicMock()
    mock_actor.call = MagicMock(return_value=mock_run)

    mock_client = MagicMock()
    mock_client.actor = MagicMock(return_value=mock_actor)
    mock_client.dataset = MagicMock(return_value=mock_dataset)

    with patch("scraper.APIFY_TOKEN", "test_token"), \
         patch("apify_client.ApifyClient", return_value=mock_client):
        result = scrape_city_category({
            "query": "cafe in Mumbai",
            "city": "Mumbai",
            "country": "india",
            "category": "cafe",
        }, max_results=3)

    assert len(result) == 3