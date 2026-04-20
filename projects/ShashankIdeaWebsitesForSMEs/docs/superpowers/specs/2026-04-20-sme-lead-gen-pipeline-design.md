# SME Lead Generation Pipeline — Design Spec

**Date:** 2026-04-20
**Author:** Claude + Satyam Das
**Status:** Approved

## Problem

SMEs in India and Australia lack websites. We sell basic static websites ($200-500 / Rs.5,000-20,000). Need to discover businesses without websites, get their contact details, and reach out via email + cold call. Budget: $0.

## Market Opportunity

- **India**: 63.4M MSMEs, ~1% have websites, 70% of cafes/salons/retail lack sites. Pricing: Rs.5,000-20,000 per basic site.
- **Australia**: 2.4M+ SMEs, 59% have no website. Pricing: $1,500-$6,000 AUD per basic site.
- **TAM**: ~62.8M Indian + ~1.4M Australian SMEs without websites.

## Architecture — 3-Layer FREE Pipeline

### Layer 1: Discovery (Python Maps Scraper — FREE)

Use open-source `noworneverev/google-maps-scraper`:
- pip installable, async, 20+ fields (name, phone, website, address, category, rating, hours, coordinates)
- Playwright/Firefox engine with stealth mode
- Crash recovery with auto-save
- Filter: `website == null or empty` = hot lead

Scale alternative: `ssecgroup/google-maps-scraper-pro` for 100K+ results at constant 50MB RAM.

**Search Strategy:**
- 11 target cities: Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Pune, Sydney, Melbourne, Brisbane, Perth, Adelaide
- 8 business categories per city: cafe, bakery, salon, gym, retail shop, plumber, electrician, restaurant
- ~88 search queries total
- Target: 200-500 leads per city (2,200-5,500 total)

### Layer 2: Contact Enrichment (FREE)

1. **Phone numbers**: Already extracted by Maps scraper
2. **Email extraction**:
   - Scrape business Instagram/Facebook pages for contact emails
   - Apollo.io free tier: 100 lead credits + 160 phone credits for top-priority leads
   - Pattern-based email guessing (firstname@businessname.com) with verification
3. **Website verification**: Cross-check that business truly lacks a website

### Layer 3: Outreach (FREE)

1. **CSV Export** with columns: business_name, phone, email, city, category, address, maps_url, has_website, rating, review_count
2. **Cold call script template** per category
3. **Email template** with portfolio link
4. **Prioritization**: Leads with phone numbers first (higher conversion for cold call)

## Data Flow

```
Python Maps Scraper (free, local)
  → Search queries per city per category
  → Filter website == null/empty
  → Output: name, phone, address, category, Maps URL, rating

Email Finder (free scraping + Apollo 100 credits)
  → Scrape social profiles for emails
  → Apollo enrichment for top leads

CSV Export
  → Sorted by: has_phone DESC, has_email DESC, rating DESC
  → Ready for cold call + email outreach
```

## Implementation Components

1. **`scraper.py`** — Main pipeline orchestrator
   - Runs Maps scraper per city/category
   - Filters no-website businesses
   - Deduplicates by place_id

2. **`enricher.py`** — Contact enrichment
   - Instagram/FB email scraping
   - Apollo API enrichment (100 credits)
   - Email pattern guessing + MX verification

3. **`exporter.py`** — CSV export + outreach templates
   - Generates CSV per city
   - Generates cold call script per category
   - Generates email template

4. **`config.py`** — Cities, categories, search queries

## Target Cities

**India (Tier 1):** Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Pune
**Australia (Major):** Sydney, Melbourne, Brisbane, Perth, Adelaide

## Business Categories

cafe, bakery, salon, gym, retail shop, plumber, electrician, restaurant

## Cost

**Total: $0**

- Maps scraper: open-source Python (free)
- Enrichment: Apollo free tier (100 credits), social scraping (free)
- Export: CSV (free)

## Constraints

- Google Maps may rate-limit aggressive scraping — use stealth mode, delays
- Apollo free tier limited to 100 lead credits — reserve for highest-value leads
- Email accuracy from social scraping ~60-70% — verify before outreach
- Phone numbers from Maps ~80-90% accurate

## Success Criteria

- 200-500 verified no-website businesses per city
- Phone number for >70% of leads
- Email for >40% of leads
- CSV export ready for immediate outreach