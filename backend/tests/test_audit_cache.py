"""Tests for the audit cache and PDF/screen consistency (task 5, finding: mismatch)."""
from fastapi.testclient import TestClient

from app.core import audit_cache
from app.main import app
from app.api import analyze


def test_cache_set_and_get():
    audit_cache._store.clear()
    audit_cache.set_result("http://x", {"score": 1})
    assert audit_cache.get_result("http://x") == {"score": 1}


def test_cache_expires():
    audit_cache._store.clear()
    audit_cache.set_result("http://x", {"score": 1})
    saved_at, result = audit_cache._store["http://x"]
    audit_cache._store["http://x"] = (saved_at - audit_cache.TTL_SECONDS - 1, result)
    assert audit_cache.get_result("http://x") is None


def test_pdf_reuses_screen_result(monkeypatch):
    """The PDF must use the exact result /analyze produced, not a second audit."""
    audit_cache._store.clear()
    runs = {"n": 0}

    async def fake_audit(url):
        runs["n"] += 1
        return {"run": runs["n"]}

    captured = {}

    def fake_build_pdf(data, path):
        captured["data"] = data
        open(path, "wb").close()

    monkeypatch.setattr(analyze, "fetch_and_audit", fake_audit)
    monkeypatch.setattr(analyze, "build_pdf", fake_build_pdf)

    client = TestClient(app)
    screen = client.get("/analyze", params={"url": "http://x"}).json()
    client.get("/download-pdf", params={"url": "http://x"})

    assert screen == {"run": 1}
    assert captured["data"] == {"run": 1}
    assert runs["n"] == 1