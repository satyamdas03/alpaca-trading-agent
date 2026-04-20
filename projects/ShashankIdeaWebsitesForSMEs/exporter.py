"""Export leads to CSV and generate outreach-ready outputs."""

import csv
import json
import os
from collections import defaultdict

from config import EXPORT_DIR

CSV_COLUMNS = [
    "business_name",
    "phone",
    "email",
    "guessed_emails",
    "city",
    "category",
    "address",
    "maps_url",
    "has_website",
    "rating",
    "review_count",
    "domain_has_mx",
    "email_source",
    "phone_source",
]


def _has_phone(lead: dict) -> bool:
    return bool(lead.get("phone"))


def _has_email(lead: dict) -> bool:
    return bool(lead.get("email"))


def sort_leads_for_outreach(leads: list[dict]) -> list[dict]:
    """Sort leads by outreach priority.

    Priority groups (highest first):
      1. Has both phone AND email
      2. Has phone only
      3. Has email only
      4. Has neither

    Within each group, sort by rating (desc) then review_count (desc).
    """
    if not leads:
        return []

    def _priority(lead: dict) -> int:
        phone = _has_phone(lead)
        email = _has_email(lead)
        if phone and email:
            return 0
        if phone:
            return 1
        if email:
            return 2
        return 3

    def _sort_key(lead: dict):
        return (
            _priority(lead),
            -(lead.get("rating") or 0),
            -(lead.get("review_count") or 0),
        )

    return sorted(leads, key=_sort_key)


def export_csv(leads: list[dict], city: str, output_dir: str | None = None) -> str:
    """Export leads for a city to CSV.

    Returns the path of the written file.
    """
    if output_dir is None:
        output_dir = EXPORT_DIR

    os.makedirs(output_dir, exist_ok=True)

    filename = f"leads_{city}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()

        for lead in leads:
            row = {}
            for col in CSV_COLUMNS:
                value = lead.get(col, "")

                # Flatten guessed_emails list to semicolon-separated string
                if col == "guessed_emails" and isinstance(value, list):
                    value = ";".join(str(v) for v in value)

                row[col] = value

            writer.writerow(row)

    return filepath


def generate_city_summary(leads: list[dict], city: str) -> dict:
    """Return a summary dict for a city's leads."""
    by_category: dict[str, int] = defaultdict(int)
    with_phone = 0
    with_email = 0

    for lead in leads:
        if _has_phone(lead):
            with_phone += 1
        if _has_email(lead):
            with_email += 1
        cat = lead.get("category", "unknown")
        by_category[cat] += 1

    return {
        "city": city,
        "total_leads": len(leads),
        "with_phone": with_phone,
        "with_email": with_email,
        "by_category": dict(by_category),
    }


def export_all_cities(leads: list[dict], output_dir: str | None = None) -> dict:
    """Export CSV per city and save pipeline_summary.json.

    Returns the pipeline summary dict.
    """
    if output_dir is None:
        output_dir = EXPORT_DIR

    os.makedirs(output_dir, exist_ok=True)

    # Group leads by city
    city_leads: dict[str, list[dict]] = defaultdict(list)
    for lead in leads:
        city = lead.get("city", "unknown")
        city_leads[city].append(lead)

    # Export CSV per city
    summaries = {}
    for city, city_lead_list in city_leads.items():
        sorted_leads = sort_leads_for_outreach(city_lead_list)
        export_csv(sorted_leads, city, output_dir)
        summaries[city] = generate_city_summary(city_lead_list, city)

    # Save pipeline summary
    summary_path = os.path.join(output_dir, "pipeline_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    return summaries