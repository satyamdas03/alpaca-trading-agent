"""
Scraper — Discovery Layer

Scrapes Google Maps for businesses across 11 cities x 8 categories (88 queries),
then filters to find SMEs without real websites (hot leads).
"""

import asyncio
import json
import logging
from pathlib import Path
from urllib.parse import quote_plus

from config import CITIES, CATEGORIES, SEARCH_TEMPLATES, MAX_RESULTS_PER_QUERY, RAW_DIR

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


def _build_maps_search_url(query_text):
    """Build a Google Maps search URL from a query string.

    Args:
        query_text: e.g. "cafe in Mumbai"

    Returns:
        str: Google Maps search URL.
    """
    encoded = quote_plus(query_text)
    return f"https://www.google.com/maps/search/?api=1&query={encoded}"


def _map_place_to_lead(place, city, category, country):
    """Map a gmaps_scraper PlaceDetails object to our lead schema.

    Args:
        place: PlaceDetails from gmaps_scraper.
        city: City name.
        category: Business category.
        country: Country name.

    Returns:
        dict: Lead with our schema fields.
    """
    return {
        "business_name": place.name,
        "phone": place.phone,
        "website": place.website,
        "address": place.address,
        "category": category,
        "city": city,
        "country": country,
        "maps_url": place.google_maps_url,
        "place_id": place.place_id,
        "rating": place.rating,
        "review_count": place.review_count,
        "latitude": place.latitude,
        "longitude": place.longitude,
    }


async def scrape_city_category(query_info, max_results=None):
    """Async function that scrapes Google Maps for a city-category combination.

    Uses gmaps_scraper library to navigate to a Google Maps search URL
    and extract place details from the top result.

    Args:
        query_info: dict with keys 'query', 'city', 'category', 'country'.
        max_results: Maximum results to return (default from config).

    Returns:
        list[dict]: List of lead dicts matching our schema.
    """
    from gmaps_scraper import GoogleMapsScraper, ScrapeConfig

    if max_results is None:
        max_results = MAX_RESULTS_PER_QUERY

    query_text = query_info["query"]
    city = query_info["city"]
    category = query_info["category"]
    country = query_info["country"]

    search_url = _build_maps_search_url(query_text)
    logger.info("Scraping: %s", query_text)

    config = ScrapeConfig(headless=True, max_retries=2)
    leads = []

    try:
        async with GoogleMapsScraper(config) as scraper:
            result = await scraper.scrape(search_url)

            if result.success and result.place and result.place.name:
                lead = _map_place_to_lead(result.place, city, category, country)
                leads.append(lead)
                logger.info("  Found: %s", result.place.name)
            else:
                error_msg = result.error or "No place found"
                logger.warning("  No result for '%s': %s", query_text, error_msg)

    except Exception as e:
        logger.error("  Scraper error for '%s': %s", query_text, e)

    return leads[:max_results]


async def run_all_scrapes(delay_seconds=3):
    """Run scraper for all 88 queries with delays between queries.

    Saves per-query JSON files and a combined all_leads_raw.json.

    Args:
        delay_seconds: Seconds to wait between queries (default 3).

    Returns:
        list[dict]: All leads collected across all queries.
    """
    queries = build_queries()
    all_leads = []

    # Ensure output directory exists
    raw_dir = Path(RAW_DIR)
    raw_dir.mkdir(parents=True, exist_ok=True)

    total = len(queries)
    logger.info("Starting scrape of %d queries...", total)

    for i, query_info in enumerate(queries):
        logger.info("[%d/%d] %s — %s in %s",
                    i + 1, total, query_info["category"], query_info["query"], query_info["city"])

        leads = await scrape_city_category(query_info)
        all_leads.extend(leads)

        # Save per-query JSON
        safe_name = f"{query_info['country']}_{query_info['city']}_{query_info['category']}".replace(" ", "_")
        query_file = raw_dir / f"{safe_name}.json"
        with open(query_file, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)

        # Delay between queries to avoid rate limiting
        if i < total - 1:
            await asyncio.sleep(delay_seconds)

    # Save combined results
    combined_file = raw_dir / "all_leads_raw.json"
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(all_leads, f, indent=2, ensure_ascii=False)

    logger.info("Scrape complete. %d leads saved to %s", len(all_leads), combined_file)
    return all_leads


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(run_all_scrapes())