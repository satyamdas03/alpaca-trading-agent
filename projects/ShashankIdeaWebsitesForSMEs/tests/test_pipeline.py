import json
import os
from unittest.mock import patch, MagicMock

import pytest

from pipeline import Pipeline


# Helper to monkeypatch config dirs in both config and pipeline modules
def patch_config_dirs(monkeypatch, tmp_path):
    """Patch all config directory paths to use tmp_path."""
    output_dir = str(tmp_path / "output")
    raw_dir = str(tmp_path / "output" / "raw")
    enriched_dir = str(tmp_path / "output" / "enriched")
    export_dir = str(tmp_path / "output" / "exports")

    # Patch in both modules since pipeline imports these at module level
    for module_name in ["config", "pipeline"]:
        monkeypatch.setattr(f"{module_name}.OUTPUT_DIR", output_dir)
        monkeypatch.setattr(f"{module_name}.RAW_DIR", raw_dir)
        monkeypatch.setattr(f"{module_name}.ENRICHED_DIR", enriched_dir)
        monkeypatch.setattr(f"{module_name}.EXPORT_DIR", export_dir)

    return output_dir, raw_dir, enriched_dir, export_dir


# ── Pipeline.__init__ ──────────────────────────────────────────────────

class TestPipelineInit:
    def test_creates_output_directories(self, tmp_path, monkeypatch):
        output_dir, raw_dir, enriched_dir, export_dir = patch_config_dirs(monkeypatch, tmp_path)

        Pipeline()

        assert os.path.isdir(output_dir)
        assert os.path.isdir(raw_dir)
        assert os.path.isdir(enriched_dir)
        assert os.path.isdir(export_dir)

    def test_idempotent_creation(self, tmp_path, monkeypatch):
        patch_config_dirs(monkeypatch, tmp_path)

        Pipeline()  # first call creates dirs
        Pipeline()  # second call should not error

        assert os.path.isdir(str(tmp_path / "output"))


# ── Pipeline.load_raw ──────────────────────────────────────────────────

class TestLoadRaw:
    def test_loads_raw_leads_from_disk(self, tmp_path, monkeypatch):
        _, raw_dir, _, _ = patch_config_dirs(monkeypatch, tmp_path)
        os.makedirs(raw_dir, exist_ok=True)

        leads = [
            {"business_name": "Test Cafe", "phone": "123-456-7890"},
            {"business_name": "Test Salon", "phone": "987-654-3210"},
        ]
        with open(os.path.join(raw_dir, "all_leads_raw.json"), "w") as f:
            json.dump(leads, f)

        p = Pipeline()
        loaded = p.load_raw()
        assert len(loaded) == 2
        assert loaded[0]["business_name"] == "Test Cafe"

    def test_load_raw_file_not_found(self, tmp_path, monkeypatch):
        patch_config_dirs(monkeypatch, tmp_path)

        p = Pipeline()
        with pytest.raises(FileNotFoundError):
            p.load_raw()


# ── Pipeline.load_enriched ─────────────────────────────────────────────

class TestLoadEnriched:
    def test_loads_enriched_leads_from_disk(self, tmp_path, monkeypatch):
        _, _, enriched_dir, _ = patch_config_dirs(monkeypatch, tmp_path)
        os.makedirs(enriched_dir, exist_ok=True)

        leads = [
            {"business_name": "Test Cafe", "email": "info@testcafe.com", "mx_valid": True},
        ]
        with open(os.path.join(enriched_dir, "all_leads_enriched.json"), "w") as f:
            json.dump(leads, f)

        p = Pipeline()
        loaded = p.load_enriched()
        assert len(loaded) == 1
        assert loaded[0]["email"] == "info@testcafe.com"

    def test_load_enriched_file_not_found(self, tmp_path, monkeypatch):
        patch_config_dirs(monkeypatch, tmp_path)

        p = Pipeline()
        with pytest.raises(FileNotFoundError):
            p.load_enriched()


# ── Pipeline.run_discovery ─────────────────────────────────────────────

class TestRunDiscovery:
    def test_calls_run_all_scrapes(self, tmp_path, monkeypatch):
        patch_config_dirs(monkeypatch, tmp_path)

        fake_leads = [{"business_name": "Cafe A", "city": "Mumbai"}]

        with patch("pipeline.run_all_scrapes", return_value=fake_leads):
            p = Pipeline()
            result = p.run_discovery()
            assert result == fake_leads

    def test_returns_empty_on_no_results(self, tmp_path, monkeypatch):
        patch_config_dirs(monkeypatch, tmp_path)

        with patch("pipeline.run_all_scrapes", return_value=[]):
            p = Pipeline()
            result = p.run_discovery()
            assert result == []


# ── Pipeline.run_enrichment ────────────────────────────────────────────

class TestRunEnrichment:
    def test_enriches_provided_leads(self, tmp_path, monkeypatch):
        patch_config_dirs(monkeypatch, tmp_path)

        input_leads = [{"business_name": "Cafe A", "website": "http://cafe.com"}]
        enriched_leads = [
            {"business_name": "Cafe A", "website": "http://cafe.com",
             "domain": "cafe.com", "mx_valid": True, "guessed_emails": ["info@cafe.com"]},
        ]

        with patch("pipeline.enrich_leads", return_value=enriched_leads) as mock_enrich:
            p = Pipeline()
            result = p.run_enrichment(input_leads)
            mock_enrich.assert_called_once_with(input_leads)
            assert result == enriched_leads

    def test_loads_raw_when_no_leads_provided(self, tmp_path, monkeypatch):
        _, raw_dir, _, _ = patch_config_dirs(monkeypatch, tmp_path)
        os.makedirs(raw_dir, exist_ok=True)

        leads = [{"business_name": "Cafe A"}]
        with open(os.path.join(raw_dir, "all_leads_raw.json"), "w") as f:
            json.dump(leads, f)

        enriched_leads = [{"business_name": "Cafe A", "email": "info@cafe.com"}]

        with patch("pipeline.enrich_leads", return_value=enriched_leads) as mock_enrich:
            p = Pipeline()
            result = p.run_enrichment()  # No leads passed — should load from disk
            mock_enrich.assert_called_once_with(leads)
            assert result == enriched_leads


# ── Pipeline.run_export ────────────────────────────────────────────────

class TestRunExport:
    def test_exports_provided_leads(self, tmp_path, monkeypatch):
        patch_config_dirs(monkeypatch, tmp_path)

        leads = [
            {"business_name": "Cafe A", "city": "Mumbai", "phone": "123", "email": "a@b.com"},
        ]
        fake_summary = {
            "Mumbai": {"city": "Mumbai", "total_leads": 1, "with_phone": 1, "with_email": 1, "by_category": {}},
        }

        with patch("pipeline.export_all_cities", return_value=fake_summary) as mock_export:
            p = Pipeline()
            result = p.run_export(leads)
            mock_export.assert_called_once_with(leads)
            assert result == fake_summary

    def test_loads_enriched_when_no_leads_provided(self, tmp_path, monkeypatch):
        _, _, enriched_dir, _ = patch_config_dirs(monkeypatch, tmp_path)
        os.makedirs(enriched_dir, exist_ok=True)

        leads = [{"business_name": "Cafe A", "city": "Mumbai", "email": "a@b.com"}]
        with open(os.path.join(enriched_dir, "all_leads_enriched.json"), "w") as f:
            json.dump(leads, f)

        fake_summary = {
            "Mumbai": {"city": "Mumbai", "total_leads": 1, "with_phone": 0, "with_email": 1, "by_category": {}},
        }

        with patch("pipeline.export_all_cities", return_value=fake_summary) as mock_export:
            p = Pipeline()
            result = p.run_export()  # No leads passed — should load from disk
            mock_export.assert_called_once_with(leads)
            assert result == fake_summary


# ── Pipeline.run_full ──────────────────────────────────────────────────

class TestRunFull:
    def test_runs_all_three_steps_sequentially(self, tmp_path, monkeypatch):
        patch_config_dirs(monkeypatch, tmp_path)

        raw_leads = [{"business_name": "Cafe A"}]
        enriched_leads = [{"business_name": "Cafe A", "email": "a@b.com"}]
        summary = {"Mumbai": {"city": "Mumbai", "total_leads": 1, "with_phone": 1, "with_email": 1, "by_category": {}}}

        with patch("pipeline.run_all_scrapes", return_value=raw_leads), \
             patch("pipeline.enrich_leads", return_value=enriched_leads), \
             patch("pipeline.export_all_cities", return_value=summary):
            p = Pipeline()
            result = p.run_full()
            assert result == summary


# ── Pipeline.run_from_raw ──────────────────────────────────────────────

class TestRunFromRaw:
    def test_loads_raw_then_enriches_and_exports(self, tmp_path, monkeypatch):
        _, raw_dir, _, _ = patch_config_dirs(monkeypatch, tmp_path)
        os.makedirs(raw_dir, exist_ok=True)

        raw_leads = [{"business_name": "Cafe A"}]
        with open(os.path.join(raw_dir, "all_leads_raw.json"), "w") as f:
            json.dump(raw_leads, f)

        enriched_leads = [{"business_name": "Cafe A", "email": "a@b.com"}]
        summary = {"Mumbai": {"city": "Mumbai", "total_leads": 1, "with_phone": 1, "with_email": 1, "by_category": {}}}

        with patch("pipeline.enrich_leads", return_value=enriched_leads), \
             patch("pipeline.export_all_cities", return_value=summary):
            p = Pipeline()
            result = p.run_from_raw()
            assert result == summary


# ── Pipeline.run_from_enriched ─────────────────────────────────────────

class TestRunFromEnriched:
    def test_loads_enriched_then_exports(self, tmp_path, monkeypatch):
        _, _, enriched_dir, _ = patch_config_dirs(monkeypatch, tmp_path)
        os.makedirs(enriched_dir, exist_ok=True)

        enriched_leads = [{"business_name": "Cafe A", "email": "a@b.com"}]
        with open(os.path.join(enriched_dir, "all_leads_enriched.json"), "w") as f:
            json.dump(enriched_leads, f)

        summary = {"Mumbai": {"city": "Mumbai", "total_leads": 1, "with_phone": 0, "with_email": 1, "by_category": {}}}

        with patch("pipeline.export_all_cities", return_value=summary):
            p = Pipeline()
            result = p.run_from_enriched()
            assert result == summary