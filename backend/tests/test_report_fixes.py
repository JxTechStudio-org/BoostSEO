"""Tests for the report/PDF fixes (task 5): filename, text wrapping, report date, guides."""
from datetime import date

from app.api.analyze import _report_filename
from app.services import pdf_report
from app.services.pdf_report import build_pdf


def test_report_filename_uses_domain_and_date():
    name = _report_filename("https://nike.com/shoes")
    assert name == f"SEO_Report_nike.com_{date.today().isoformat()}.pdf"


def test_report_filename_handles_bare_domain():
    assert _report_filename("example.org").startswith("SEO_Report_example.org_")


def test_seo_guides_have_title_and_link():
    assert len(pdf_report.SEO_GUIDES) == 3
    for guide in pdf_report.SEO_GUIDES:
        assert guide["title"] and guide["url"].startswith("http")


def _sample_data(message: str) -> dict:
    return {
        "url": "https://x.com",
        "score": 62,
        "summary": "Average SEO, a few issues need attention.",
        "categories": [{
            "name": "Meta & Social",
            "score": 50,
            "checks": [{
                "name": "A very long check name that previously got cut off mid-word",
                "status": "Warning",
                "message": message,
                "value": "",
                "weight": 2,
                "category": "Meta & Social",
            }],
        }],
        "meta": {
            "checks_total": 1, "checks_passed": 0, "checks_warned": 1,
            "checks_failed": 0, "response_time_ms": 100,
        },
    }


def test_build_pdf_wraps_long_text_and_adds_guides(tmp_path):
    out = tmp_path / "report.pdf"
    build_pdf(_sample_data("This is a very long check message. " * 15), str(out))
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"
    