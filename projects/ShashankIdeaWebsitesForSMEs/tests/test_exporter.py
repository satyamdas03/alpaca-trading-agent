import os
import json
import pytest
import pandas as pd

from exporter import (
    sort_leads_for_outreach,
    export_csv,
    generate_city_summary,
    export_all_cities,
)


# ── sort_leads_for_outreach ──────────────────────────────────────────

class TestSortLeadsForOutreach:
    def test_phone_and_email_first(self):
        leads = [
            {"business_name": "A", "phone": "123", "email": "a@b.com", "rating": 4.0, "review_count": 10},
            {"business_name": "B", "phone": "456", "email": "", "rating": 4.5, "review_count": 50},
            {"business_name": "C", "phone": "", "email": "c@b.com", "rating": 4.0, "review_count": 10},
            {"business_name": "D", "phone": "", "email": "", "rating": 4.0, "review_count": 10},
        ]
        result = sort_leads_for_outreach(leads)
        names = [l["business_name"] for l in result]
        assert names.index("A") < names.index("B")
        assert names.index("A") < names.index("C")
        assert names.index("B") < names.index("C")
        assert names.index("C") < names.index("D")

    def test_within_group_sort_by_rating_desc(self):
        leads = [
            {"business_name": "Low", "phone": "123", "email": "a@b.com", "rating": 3.0, "review_count": 10},
            {"business_name": "High", "phone": "456", "email": "b@b.com", "rating": 4.8, "review_count": 10},
        ]
        result = sort_leads_for_outreach(leads)
        assert result[0]["business_name"] == "High"

    def test_within_group_sort_by_review_count_desc_when_rating_equal(self):
        leads = [
            {"business_name": "Few", "phone": "123", "email": "a@b.com", "rating": 4.0, "review_count": 5},
            {"business_name": "Many", "phone": "456", "email": "b@b.com", "rating": 4.0, "review_count": 200},
        ]
        result = sort_leads_for_outreach(leads)
        assert result[0]["business_name"] == "Many"

    def test_empty_list(self):
        assert sort_leads_for_outreach([]) == []

    def test_missing_phone_email_treated_as_empty(self):
        leads = [
            {"business_name": "NoFields", "rating": 4.0, "review_count": 10},
            {"business_name": "WithBoth", "phone": "123", "email": "a@b.com", "rating": 4.0, "review_count": 10},
        ]
        result = sort_leads_for_outreach(leads)
        assert result[0]["business_name"] == "WithBoth"


# ── export_csv ────────────────────────────────────────────────────────

class TestExportCsv:
    def test_export_csv_creates_file(self, tmp_path):
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
        assert df.iloc[0]["business_name"] == "Cafe A"

    def test_export_csv_has_required_columns(self, tmp_path):
        leads = [
            {"business_name": "Test", "phone": "123", "email": "a@b.com",
             "city": "Delhi", "category": "cafe", "address": "Addr",
             "maps_url": "http://maps", "has_website": True, "rating": 4.0,
             "review_count": 50, "guessed_emails": ["x@y.com", "z@y.com"],
             "domain_has_mx": True, "email_source": "google", "phone_source": "maps"},
        ]
        filepath = export_csv(leads, "Delhi", str(tmp_path))
        df = pd.read_csv(filepath)
        expected_cols = [
            "business_name", "phone", "email", "guessed_emails", "city",
            "category", "address", "maps_url", "has_website", "rating",
            "review_count", "domain_has_mx", "email_source", "phone_source",
        ]
        for col in expected_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_guessed_emails_flattened_with_semicolons(self, tmp_path):
        leads = [
            {"business_name": "Test", "phone": "", "email": "",
             "guessed_emails": ["a@b.com", "c@b.com"],
             "city": "Pune", "category": "cafe", "address": "",
             "maps_url": "", "has_website": False, "rating": None, "review_count": 0},
        ]
        filepath = export_csv(leads, "Pune", str(tmp_path))
        df = pd.read_csv(filepath)
        assert df.iloc[0]["guessed_emails"] == "a@b.com;c@b.com"

    def test_utf8_sig_encoding(self, tmp_path):
        leads = [
            {"business_name": "Test", "phone": "", "email": "",
             "city": "Mumbai", "category": "cafe", "address": "",
             "maps_url": "", "has_website": False, "rating": None, "review_count": 0},
        ]
        filepath = export_csv(leads, "Mumbai", str(tmp_path))
        with open(filepath, "rb") as f:
            raw = f.read(3)
        assert raw == b"\xef\xbb\xbf"  # UTF-8 BOM

    def test_filename_format(self, tmp_path):
        leads = [{"business_name": "X", "phone": "", "email": "",
                  "city": "Bangalore", "category": "cafe", "address": "",
                  "maps_url": "", "has_website": False, "rating": None, "review_count": 0}]
        filepath = export_csv(leads, "Bangalore", str(tmp_path))
        assert filepath.endswith("leads_Bangalore.csv")

    def test_missing_optional_fields_default_empty(self, tmp_path):
        leads = [
            {"business_name": "Minimal", "phone": "", "email": "",
             "city": "Chennai", "category": "cafe"},
        ]
        filepath = export_csv(leads, "Chennai", str(tmp_path))
        df = pd.read_csv(filepath)
        assert len(df) == 1
        assert df.iloc[0]["business_name"] == "Minimal"

    def test_uses_config_export_dir_when_no_output_dir(self):
        leads = [
            {"business_name": "DefaultDir", "phone": "", "email": "",
             "city": "Hyderabad", "category": "cafe"},
        ]
        filepath = export_csv(leads, "Hyderabad")
        assert "exports" in filepath or "output" in filepath
        # cleanup
        if os.path.exists(filepath):
            os.remove(filepath)


# ── generate_city_summary ────────────────────────────────────────────

class TestGenerateCitySummary:
    def test_generate_city_summary_returns_dict(self):
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
        assert "bakery" in summary["by_category"]

    def test_empty_leads(self):
        summary = generate_city_summary([], "Nowhere")
        assert summary["total_leads"] == 0
        assert summary["with_phone"] == 0
        assert summary["with_email"] == 0

    def test_category_counts(self):
        leads = [
            {"business_name": "A", "phone": "1", "email": "", "city": "X", "category": "cafe"},
            {"business_name": "B", "phone": "", "email": "b@b.com", "city": "X", "category": "cafe"},
            {"business_name": "C", "phone": "3", "email": "c@c.com", "city": "X", "category": "gym"},
        ]
        summary = generate_city_summary(leads, "X")
        assert summary["by_category"]["cafe"] == 2
        assert summary["by_category"]["gym"] == 1


# ── export_all_cities ────────────────────────────────────────────────

class TestExportAllCities:
    def test_export_all_cities_creates_csv_per_city(self, tmp_path):
        leads = [
            {"business_name": "A", "phone": "1", "email": "a@a.com",
             "city": "Mumbai", "category": "cafe", "address": "",
             "maps_url": "", "has_website": False, "rating": 4.0, "review_count": 10},
            {"business_name": "B", "phone": "2", "email": "",
             "city": "Delhi", "category": "gym", "address": "",
             "maps_url": "", "has_website": False, "rating": 3.5, "review_count": 5},
        ]
        export_all_cities(leads, str(tmp_path))
        assert os.path.exists(os.path.join(str(tmp_path), "leads_Mumbai.csv"))
        assert os.path.exists(os.path.join(str(tmp_path), "leads_Delhi.csv"))

    def test_export_all_cities_creates_pipeline_summary(self, tmp_path):
        leads = [
            {"business_name": "A", "phone": "1", "email": "a@a.com",
             "city": "Mumbai", "category": "cafe", "address": "",
             "maps_url": "", "has_website": False, "rating": 4.0, "review_count": 10},
        ]
        export_all_cities(leads, str(tmp_path))
        summary_path = os.path.join(str(tmp_path), "pipeline_summary.json")
        assert os.path.exists(summary_path)
        with open(summary_path) as f:
            data = json.load(f)
        assert "Mumbai" in data or "cities" in data