"""Contact Enrichment Layer for SME Lead Gen Pipeline.

Provides email guessing, MX verification, domain extraction,
and Apollo API enrichment for scraped business leads.
"""

import json
import logging
import os
from urllib.parse import urlparse

import dns.resolver
import requests

from config import ENRICHED_DIR, APOLLO_API_KEY

logger = logging.getLogger(__name__)

# Common SME contact email prefixes
EMAIL_PREFIXES = [
    "info",
    "contact",
    "hello",
    "bookings",
    "admin",
    "support",
    "enquiry",
]

APOLLO_MATCH_URL = "https://api.apollo.io/v1/people/match"
APOLLO_FREE_TIER_LIMIT = 100


def guess_email(business_name: str, domain: str) -> list[str]:
    """Generate common email patterns for a business domain.

    Args:
        business_name: Name of the business (reserved for future use
            with name-based patterns).
        domain: The business domain (e.g. "blueskycafe.com").

    Returns:
        List of common email addresses for the domain.
        Returns empty list if domain is falsy.
    """
    if not domain:
        return []

    return [f"{prefix}@{domain}" for prefix in EMAIL_PREFIXES]


def verify_email_mx(domain: str) -> bool:
    """Check if a domain has valid MX records.

    Args:
        domain: The domain to check (e.g. "gmail.com").

    Returns:
        True if MX records exist, False otherwise.
        Returns False for empty/None input or any DNS error.
    """
    if not domain:
        return False

    try:
        dns.resolver.resolve(domain, "MX")
        return True
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoNameservers,
        dns.resolver.Timeout,
        dns.exception.DNSException,
        Exception,
    ):
        return False


def extract_domain_from_website(url: str) -> str | None:
    """Extract the registrable domain from a URL.

    Strips protocol, www. prefix, and path components.

    Args:
        url: A website URL (e.g. "https://www.example.com/page").

    Returns:
        The bare domain (e.g. "example.com"), or None if the
        input is empty or contains no dot.
    """
    if not url:
        return None

    # Add a scheme so urlparse can parse bare domains correctly
    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    # Strip www. prefix
    if hostname.startswith("www."):
        hostname = hostname[4:]

    # Must contain a dot to be a valid registrable domain
    if "." not in hostname:
        return None

    return hostname if hostname else None


def enrich_with_apollo(leads: list[dict], api_key: str | None = None) -> list[dict]:
    """Enrich leads using the Apollo People Match API.

    Only enriches leads that lack an email field. Sorts by rating
    descending and respects the free-tier limit of 100 credits.

    Args:
        leads: List of lead dicts, each with at least business_name.
        api_key: Apollo API key. Falls back to config.APOLLO_API_KEY.
            If no key is available, returns leads unchanged.

    Returns:
        The leads list with enriched data where available.
    """
    key = api_key or APOLLO_API_KEY
    if not key:
        logger.warning("No Apollo API key provided; skipping enrichment.")
        return leads

    # Identify leads lacking an email, sorted by rating descending
    leads_needing_email = [
        lead for lead in leads if not lead.get("email")
    ]
    leads_needing_email.sort(key=lambda l: l.get("rating", 0) or 0, reverse=True)

    # Respect free-tier credit limit
    to_enrich = leads_needing_email[:APOLLO_FREE_TIER_LIMIT]

    for lead in to_enrich:
        name = lead.get("business_name", "")
        parts = name.split() if name else []
        first_name = parts[0] if parts else ""
        last_name = parts[-1] if len(parts) > 1 else ""

        domain = lead.get("domain") or extract_domain_from_website(
            lead.get("website", "")
        )

        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "organization_name": name,
        }
        if domain:
            payload["domain"] = domain

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

        try:
            resp = requests.post(
                APOLLO_MATCH_URL,
                headers=headers,
                json=payload,
                params={"api_key": key},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            person = data.get("person")
            if person and person.get("email"):
                lead["email"] = person["email"]
                lead["email_source"] = "apollo"
        except requests.RequestException as exc:
            logger.warning("Apollo match failed for %s: %s", name, exc)

    return leads


def enrich_leads(leads: list[dict]) -> list[dict]:
    """Full enrichment pipeline for a list of leads.

    For each lead:
      1. Extract domain from website URL
      2. Verify MX records for the domain
      3. Guess common email patterns
      4. Run Apollo enrichment on top leads lacking email

    Saves enriched data to ENRICHED_DIR/all_leads_enriched.json.

    Args:
        leads: List of lead dicts from the scraper.

    Returns:
        The enriched leads list with added fields:
        domain, mx_valid, guessed_emails.
    """
    for lead in leads:
        # Step 1: Extract domain
        domain = extract_domain_from_website(lead.get("website", ""))
        lead["domain"] = domain

        # Step 2: Verify MX
        if domain:
            lead["mx_valid"] = verify_email_mx(domain)
        else:
            lead["mx_valid"] = False

        # Step 3: Guess emails
        if domain and lead.get("mx_valid"):
            lead["guessed_emails"] = guess_email(
                lead.get("business_name", ""), domain
            )
        else:
            lead["guessed_emails"] = []

    # Step 4: Apollo enrichment for leads without email
    leads = enrich_with_apollo(leads)

    # Save to disk
    os.makedirs(ENRICHED_DIR, exist_ok=True)
    output_path = os.path.join(ENRICHED_DIR, "all_leads_enriched.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, default=str)

    logger.info("Enriched %d leads -> %s", len(leads), output_path)
    return leads