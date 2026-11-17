"""Tests for the PDF endpoint using a per-request temp file (task 3, finding 4)."""
import os

from fastapi.testclient import TestClient

import app.api.analyze as analyze_mod
from app.main import app

client = TestClient(app)

_SAMPLE = {
    "url": "https://example.com",
    "score": 80,
    "summary": "Good.",
    "categories": [
        {"name": "Meta & Social", "score": 100, "checks": [
            {"name": "Title Tag", "status": "Passed", "message": "OK"},
        ]},
    ],
    "meta": {"checks_passed": 1, "checks_warned": 0, "checks_failed": 0,
             "response_time_ms": 5},
}


async def _fake_fetch(url: str) -> dict:
    return _SAMPLE


def test_download_pdf_uses_temp_file_not_fixed_name(tmp_path, monkeypatch):
    # run from an empty cwd and confirm no fixed file is created there
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(analyze_mod, "fetch_and_audit", _fake_fetch)
    r = client.get("/download-pdf?url=example.com")
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"
    assert not os.path.exists(tmp_path / "SEO_Detailed_Report.pdf")
