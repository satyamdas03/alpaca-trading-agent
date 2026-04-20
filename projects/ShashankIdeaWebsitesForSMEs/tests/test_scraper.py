import pytest
from scraper import (
    build_queries, filter_no_website, deduplicate_leads,
    is_social_website, SOCIAL_DOMAINS,
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