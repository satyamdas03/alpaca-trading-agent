"""
Scraper — Discovery Layer

Uses Apify's Google Maps Scraper actor to find businesses across
11 cities x 8 categories (88 queries), then filters to find SMEs
without real websites (hot leads).
"""

import json
import logging
from pathlib import Path

from config import (
    CITIES, CATEGORIES, SEARCH_TEMPLATES, MAX_RESULTS_PER_QUERY,
    RAW_DIR, APIFY_TOKEN, APIFY_ACTOR_ID, COUNTRY_CODES,
)

logger = logging.getLogger(__name__)

# Domains that indicate social/directory listings, not real business websites
SOCIAL_DOMAINS = {
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "yelp.com", "justdial.com", "zomato.com",
    "swiggy.com", "uber.com", "google.com", "maps.google.com",
    "tripadvisor.com", "foursquare.com", "bookmyshow.com",
    "indiamart.com", "sulekha.com", "gumtree.com",
    "truelocal.com.au", "yellowpages.com.au",
}


def build_queries():
    """Generate search queries for all city-category combinations.

    Returns:
        list[dict]: Each dict has keys: query, city, category, country.
        Total: 6 Indian cities + 5 Australian cities = 11, x 8 categories = 88.
    """
    queries = []
    for country, city_list in CITIES.items():
        for city in city_list:
            for category in CATEGORIES:
                template = SEARCH_TEMPLATES[category]
                query_text = template.format(category=category, city=city)
                queries.append({
                    "query": query_text,
                    "city": city,
                    "category": category,
                    "country": country,
                })
    return queries


def is_social_website(url):
    """Check if URL is a social/directory listing (not a real business website).

    Args:
        url: URL string to check (can be None).

    Returns:
        bool: True if the URL points to a known social/directory domain.
    """
    if not url:
        return False

    url = url.strip().lower()

    # Normalize: strip scheme and www
    for prefix in ("https://", "http://", "www."):
        if url.startswith(prefix):
            url = url[len(prefix):]

    # Extract the domain (everything before the first /)
    domain = url.split("/")[0]

    # Check exact match and subdomain match (e.g. m.facebook.com)
    for social_domain in SOCIAL_DOMAINS:
        if domain == social_domain or domain.endswith("." + social_domain):
            return True

    return False


def filter_no_website(leads):
    """Filter leads where website is None/empty OR only social/directory listings.

    These are our hot leads — businesses without a real website.

    Args:
        leads: list of lead dicts, each with at least 'name' and 'website' keys.

    Returns:
        list: Leads that have no real website.
    """
    result = []
    for lead in leads:
        website = lead.get("website")
        if not website or not website.strip():
            result.append(lead)
        elif is_social_website(website):
            result.append(lead)
    return result


def deduplicate_leads(leads):
    """Remove duplicates based on place_id (fallback to name+address).

    Args:
        leads: list of lead dicts with 'place_id', 'name', and 'address' keys.

    Returns:
        list: Deduplicated leads, preserving first occurrence order.
    """
    seen = set()
    result = []
    for lead in leads:
        # Primary key: place_id
        place_id = lead.get("place_id")
        if place_id:
            key = ("place_id", place_id)
        else:
            # Fallback: name + address
            name = lead.get("name", "").strip().lower()
            address = lead.get("address", "").strip().lower()
            key = ("name_addr", f"{name}|{address}")

        if key not in seen:
            seen.add(key)
            result.append(lead)

    return result


def _build_location_string(city, country):
    """Build a location string for Apify's locationQuery parameter.

    Args:
        city: City name (e.g. "Mumbai").
        country: Country key from config (e.g. "india").

    Returns:
        str: Location string like "Mumbai, India".
    """
    country_name = {
        "india": "India",
        "australia": "Australia",
    }.get(country, country.capitalize())
    return f"{city}, {country_name}"


def _map_apify_item_to_lead(item, city, category, country):
    """Map an Apify Google Maps Scraper result item to our lead schema.

    Args:
        item: Dict from Apify dataset (one place result).
        city: City name.
        category: Business category.
        country: Country key.

    Returns:
        dict: Lead with our schema fields.
    """
    location = item.get("location", {}) or {}
    return {
        "business_name": item.get("title", ""),
        "phone": item.get("phone", ""),
        "website": item.get("website", "") or None,
        "address": item.get("address", ""),
        "category": category,
        "city": city,
        "country": country,
        "maps_url": item.get("url", ""),
        "place_id": item.get("placeId", ""),
        "rating": item.get("totalScore"),
        "review_count": item.get("reviewsCount"),
        "latitude": location.get("lat"),
        "longitude": location.get("lng"),
    }


def scrape_city_category(query_info, max_results=None):
    """Scrape Google Maps for a city-category combination using Apify.

    Calls the Apify Google Maps Scraper actor, retrieves results from
    the dataset, and maps them to our lead schema.

    Args:
        query_info: dict with keys 'query', 'city', 'category', 'country'.
        max_results: Maximum results to return (default from config).

    Returns:
        list[dict]: List of lead dicts matching our schema.
                  Returns empty list if APIFY_TOKEN is not set.
    """
    if max_results is None:
        max_results = MAX_RESULTS_PER_QUERY

    if not APIFY_TOKEN:
        logger.warning(
            "APIFY_TOKEN not set — skipping scrape for '%s'. "
            "Set the APIFY_TOKEN environment variable to enable scraping.",
            query_info["query"],
        )
        return []

    from apify_client import ApifyClient

    query_text = query_info["query"]
    city = query_info["city"]
    category = query_info["category"]
    country = query_info["country"]

    location = _build_location_string(city, country)
    country_code = COUNTRY_CODES.get(country, "")

    logger.info("Scraping via Apify: %s", query_text)

    run_input = {
        "searchStringsArray": [query_text],
        "locationQuery": location,
        "maxCrawledPlacesPerSearch": max_results,
        "language": "en",
    }
    if country_code:
        run_input["countryCode"] = country_code

    try:
        client = ApifyClient(APIFY_TOKEN)
        run = client.actor(APIFY_ACTOR_ID).call(run_input=run_input)

        dataset_id = run["defaultDatasetId"]
        items = list(client.dataset(dataset_id).iterate_items())

        leads = []
        for item in items:
            lead = _map_apify_item_to_lead(item, city, category, country)
            leads.append(lead)

        logger.info("  Found %d results for '%s'", len(leads), query_text)
        return leads[:max_results]

    except Exception as e:
        logger.error("  Apify error for '%s': %s", query_text, e)
        return []


def run_all_scrapes(delay_seconds=3):
    """Run scraper for all 88 queries via Apify.

    Saves per-query JSON files and a combined all_leads_raw.json.

    Args:
        delay_seconds: Seconds to wait between queries (default 3).

    Returns:
        list[dict]: All leads collected across all queries.
    """
    import time

    queries = build_queries()
    all_leads = []

    # Ensure output directory exists
    raw_dir = Path(RAW_DIR)
    raw_dir.mkdir(parents=True, exist_ok=True)

    total = len(queries)
    logger.info("Starting scrape of %d queries via Apify...", total)

    for i, query_info in enumerate(queries):
        logger.info("[%d/%d] %s — %s in %s",
                    i + 1, total, query_info["category"],
                    query_info["query"], query_info["city"])

        leads = scrape_city_category(query_info)
        all_leads.extend(leads)

        # Save per-query JSON
        safe_name = f"{query_info['country']}_{query_info['city']}_{query_info['category']}".replace(" ", "_")
        query_file = raw_dir / f"{safe_name}.json"
        with open(query_file, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)

        # Delay between queries to respect rate limits
        if i < total - 1:
            time.sleep(delay_seconds)

    # Save combined results
    combined_file = raw_dir / "all_leads_raw.json"
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(all_leads, f, indent=2, ensure_ascii=False)

    logger.info("Scrape complete. %d leads saved to %s", len(all_leads), combined_file)
    return all_leads


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_all_scrapes()