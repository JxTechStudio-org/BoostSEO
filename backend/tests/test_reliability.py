"""Reliability tests: bad input, slow sites and oversized pages (task 4)."""
import asyncio

import httpx
import pytest
from fastapi import HTTPException

import app.services.fetcher as fetcher


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def _client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.fixture(autouse=True)
def _skip_ssrf(monkeypatch):
    # SSRF validation does real DNS; bypass it so these tests stay offline.
    async def _ok(url):
        return None

    monkeypatch.setattr(fetcher, "validate_public_url", _ok)


# ── _fetch_html: streaming + size cap ──────────────────────────────────────
def test_fetch_html_returns_text_for_normal_page():
    def handler(request):
        return httpx.Response(200, text="<html>ok</html>")

    async def go():
        async with _client(handler) as c:
            final_url, html = await fetcher._fetch_html(c, "https://e.com", fetcher.MAX_PAGE_BYTES)
            assert "<html>ok</html>" in html

    run(go())


def test_fetch_html_follows_redirects():
    def handler(request):
        if request.url.path == "/final":
            return httpx.Response(200, text="final page")
        return httpx.Response(302, headers={"location": "https://e.com/final"})

    async def go():
        async with _client(handler) as c:
            final_url, html = await fetcher._fetch_html(c, "https://e.com", fetcher.MAX_PAGE_BYTES)
            assert "final page" in html
            assert final_url.endswith("/final")

    run(go())


def test_fetch_html_aborts_on_oversized_body():
    big = b"a" * (fetcher.MAX_PAGE_BYTES + 100)

    def handler(request):
        return httpx.Response(200, content=big)

    async def go():
        async with _client(handler) as c:
            with pytest.raises(fetcher.PageTooLargeError):
                await fetcher._fetch_html(c, "https://e.com", fetcher.MAX_PAGE_BYTES)

    run(go())


def test_fetch_html_rejects_large_declared_content_length():
    def handler(request):
        return httpx.Response(
            200, headers={"content-length": str(fetcher.MAX_PAGE_BYTES + 1)}, content=b"x"
        )

    async def go():
        async with _client(handler) as c:
            with pytest.raises(fetcher.PageTooLargeError):
                await fetcher._fetch_html(c, "https://e.com", 10)  # tiny cap

    run(go())


# ── fetch_and_audit: failures map to clear status codes ────────────────────
def test_slow_site_returns_504(monkeypatch):
    async def slow(client, url, max_bytes):
        raise httpx.ReadTimeout("too slow")

    monkeypatch.setattr(fetcher, "_fetch_html", slow)
    with pytest.raises(HTTPException) as exc:
        run(fetcher.fetch_and_audit("example.com"))
    assert exc.value.status_code == 504


def test_connection_error_returns_502(monkeypatch):
    async def broken(client, url, max_bytes):
        raise httpx.ConnectError("no route")

    monkeypatch.setattr(fetcher, "_fetch_html", broken)
    with pytest.raises(HTTPException) as exc:
        run(fetcher.fetch_and_audit("example.com"))
    assert exc.value.status_code == 502


def test_oversized_page_returns_413(monkeypatch):
    async def huge(client, url, max_bytes):
        raise fetcher.PageTooLargeError

    monkeypatch.setattr(fetcher, "_fetch_html", huge)
    with pytest.raises(HTTPException) as exc:
        run(fetcher.fetch_and_audit("example.com"))
    assert exc.value.status_code == 413


def test_normal_page_is_audited(monkeypatch):
    async def ok(client, url, max_bytes):
        return "https://example.com", "<html></html>"

    async def fake_audit(html, final_url, ms):
        return {"ok": True}

    monkeypatch.setattr(fetcher, "_fetch_html", ok)
    monkeypatch.setattr(fetcher, "run_audit", fake_audit)
    assert run(fetcher.fetch_and_audit("https://example.com")) == {"ok": True}
