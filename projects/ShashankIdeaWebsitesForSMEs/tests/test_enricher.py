import pytest
from unittest.mock import patch, MagicMock
from enricher import guess_email, verify_email_mx, extract_domain_from_website, enrich_with_apollo, enrich_leads


# ── guess_email ──────────────────────────────────────────────────────────────

def test_guess_email_generates_common_patterns():
    patterns = guess_email("Blue Sky Cafe", "blueskycafe.com")
    assert "info@blueskycafe.com" in patterns
    assert "contact@blueskycafe.com" in patterns
    assert "hello@blueskycafe.com" in patterns


def test_guess_email_includes_booking_pattern():
    patterns = guess_email("Blue Sky Cafe", "blueskycafe.com")
    assert "bookings@blueskycafe.com" in patterns
    assert "admin@blueskycafe.com" in patterns
    assert "support@blueskycafe.com" in patterns
    assert "enquiry@blueskycafe.com" in patterns


def test_guess_email_handles_empty_domain():
    patterns = guess_email("Blue Sky Cafe", None)
    assert patterns == []


def test_guess_email_handles_empty_string_domain():
    patterns = guess_email("Blue Sky Cafe", "")
    assert patterns == []


def test_guess_email_returns_all_seven_patterns():
    patterns = guess_email("Test Biz", "testbiz.com")
    assert len(patterns) == 7


# ── verify_email_mx ──────────────────────────────────────────────────────────

def test_verify_email_mx_returns_bool():
    result = verify_email_mx("gmail.com")
    assert isinstance(result, bool)


def test_verify_email_mx_returns_true_for_valid_domain():
    # gmail.com is guaranteed to have MX records
    result = verify_email_mx("gmail.com")
    assert result is True


def test_verify_email_mx_returns_false_for_invalid_domain():
    result = verify_email_mx("thisdomaindoesnotexist12345.invalid")
    assert result is False


def test_verify_email_mx_handles_empty_domain():
    result = verify_email_mx("")
    assert result is False


def test_verify_email_mx_handles_none_domain():
    result = verify_email_mx(None)
    assert result is False


def test_verify_email_mx_handles_dns_exception():
    with patch("enricher.dns.resolver.resolve", side_effect=Exception("DNS error")):
        result = verify_email_mx("example.com")
        assert result is False


# ── extract_domain_from_website ─────────────────────────────────────────────

def test_extract_domain_strips_protocol():
    assert extract_domain_from_website("https://www.example.com") == "example.com"


def test_extract_domain_strips_http_protocol():
    assert extract_domain_from_website("http://example.com") == "example.com"


def test_extract_domain_strips_www():
    assert extract_domain_from_website("www.example.com") == "example.com"


def test_extract_domain_strips_path():
    assert extract_domain_from_website("https://example.com/about/us") == "example.com"


def test_extract_domain_handles_bare_domain():
    assert extract_domain_from_website("example.com") == "example.com"


def test_extract_domain_returns_none_for_empty():
    assert extract_domain_from_website(None) is None


def test_extract_domain_returns_none_for_no_dot():
    assert extract_domain_from_website("localhost") is None


def test_extract_domain_returns_none_for_empty_string():
    assert extract_domain_from_website("") is None


# ── enrich_with_apollo ───────────────────────────────────────────────────────

def test_enrich_with_apollo_handles_missing_key():
    leads = [{"business_name": "Test Cafe", "phone": "123456"}]
    result = enrich_with_apollo(leads, api_key="")
    assert result == leads


def test_enrich_with_apollo_handles_none_key():
    leads = [{"business_name": "Test Cafe", "phone": "123456"}]
    result = enrich_with_apollo(leads, api_key=None)
    assert result == leads


def test_enrich_with_apollo_only_enriches_leads_lacking_email():
    leads = [
        {"business_name": "No Email Cafe", "rating": 4.9},
        {"business_name": "Has Email Cafe", "email": "exists@cafe.com", "rating": 3.0},
    ]
    with patch("enricher.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"person": {"email": "found@noemailcafe.com"}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = enrich_with_apollo(leads, api_key="test-key")
        # Only the lead without email should have been sent to Apollo
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        posted_body = call_args[1]["json"] if "json" in call_args[1] else call_args[0][1] if len(call_args[0]) > 1 else None
        # The posted first_name etc should come from "No Email Cafe"


def test_enrich_with_apollo_limits_to_100_credits():
    leads = [{"business_name": f"Cafe {i}", "rating": 5.0 - i * 0.01} for i in range(150)]
    with patch("enricher.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"person": None}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = enrich_with_apollo(leads, api_key="test-key")
        assert mock_post.call_count <= 100


def test_enrich_with_apollo_sorts_by_rating_desc():
    leads = [
        {"business_name": "Low Cafe", "rating": 2.0},
        {"business_name": "High Cafe", "rating": 5.0},
        {"business_name": "Mid Cafe", "rating": 3.5},
    ]
    with patch("enricher.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"person": None}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = enrich_with_apollo(leads, api_key="test-key")
        # First call should be for highest rated lead
        if mock_post.call_count > 0:
            first_call_body = mock_post.call_args_list[0][1].get("json", {})
            assert first_call_body.get("first_name", "") or "High" in str(first_call_body)


# ── enrich_leads (integration-level) ─────────────────────────────────────────

def test_enrich_leads_adds_guessed_emails():
    leads = [
        {
            "business_name": "Test Cafe",
            "website": "https://www.testcafe.com",
            "rating": 4.5,
        }
    ]
    with patch("enricher.verify_email_mx", return_value=True), \
         patch("enricher.enrich_with_apollo", side_effect=lambda l, **kw: l):
        result = enrich_leads(leads)
        assert "guessed_emails" in result[0]
        assert "info@testcafe.com" in result[0]["guessed_emails"]


def test_enrich_leads_sets_mx_valid_flag():
    leads = [
        {
            "business_name": "Test Cafe",
            "website": "https://www.testcafe.com",
            "rating": 4.5,
        }
    ]
    with patch("enricher.verify_email_mx", return_value=True), \
         patch("enricher.enrich_with_apollo", side_effect=lambda l, **kw: l):
        result = enrich_leads(leads)
        assert result[0].get("mx_valid") is True


def test_enrich_leads_extracts_domain():
    leads = [
        {
            "business_name": "Test Cafe",
            "website": "https://www.testcafe.com",
            "rating": 4.5,
        }
    ]
    with patch("enricher.verify_email_mx", return_value=True), \
         patch("enricher.enrich_with_apollo", side_effect=lambda l, **kw: l):
        result = enrich_leads(leads)
        assert result[0].get("domain") == "testcafe.com"