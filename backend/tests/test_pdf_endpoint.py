"""Tests for the PDF endpoint using a per-request temp file (task 3, finding 4)."""
import glob
import os
import tempfile

from fastapi.testclient import TestClient

import app.api.analyze as analyze_mod
from app.main import app

client = TestClient(app)
# A client that returns the 500 instead of re-raising, so we can assert on the
# response and then check that no temp file was left behind.
err_client = TestClient(app, raise_server_exceptions=False)

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


def test_download_pdf_removes_temp_file_when_build_fails(tmp_path, monkeypatch):
    # If building the PDF raises, the temp file must not be left on disk.
    monkeypatch.setattr(analyze_mod, "fetch_and_audit", _fake_fetch)

    def _boom(data, path):
        raise RuntimeError("render failed")

    monkeypatch.setattr(analyze_mod, "build_pdf", _boom)

    # Create the temp files inside tmp_path so we can assert the dir is clean.
    real_mkstemp = tempfile.mkstemp

    def _mkstemp(*args, **kwargs):
        kwargs["dir"] = str(tmp_path)
        return real_mkstemp(*args, **kwargs)

    monkeypatch.setattr(analyze_mod.tempfile, "mkstemp", _mkstemp)

    r = err_client.get("/download-pdf?url=example.com")
    assert r.status_code == 500
    assert glob.glob(str(tmp_path / "seo_report_*.pdf")) == []
