"""Reliability tests: bad input, slow sites and oversized pages (task 4)."""
import asyncio

import httpx
import pytest
from fastapi import HTTPException

import app.services.fetcher as fetcher


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


class _FakeResp:
    def __init__(self, headers, content):
        self.headers = headers
        self.content = content


def test_too_large_detects_declared_size():
    assert fetcher._too_large(_FakeResp({"content-length": "10000000"}, b"x")) is True


def test_too_large_detects_actual_size():
    big = b"a" * (fetcher.MAX_PAGE_BYTES + 1)
    assert fetcher._too_large(_FakeResp({}, big)) is True


def test_not_too_large_for_small_page():
    assert fetcher._too_large(_FakeResp({}, b"<html></html>")) is False


def test_slow_site_returns_504(monkeypatch):
    async def slow(client, url):
        raise httpx.ReadTimeout("too slow")

    monkeypatch.setattr(fetcher, "safe_get", slow)
    with pytest.raises(HTTPException) as exc:
        run(fetcher.fetch_and_audit("example.com"))
    assert exc.value.status_code == 504


def test_connection_error_returns_502(monkeypatch):
    async def broken(client, url):
        raise httpx.ConnectError("no route")

    monkeypatch.setattr(fetcher, "safe_get", broken)
    with pytest.raises(HTTPException) as exc:
        run(fetcher.fetch_and_audit("example.com"))
    assert exc.value.status_code == 502


def test_oversized_page_returns_413(monkeypatch):
    big = b"a" * (fetcher.MAX_PAGE_BYTES + 1)

    async def huge(client, url):
        return httpx.Response(200, content=big, request=httpx.Request("GET", url))

    monkeypatch.setattr(fetcher, "safe_get", huge)
    with pytest.raises(HTTPException) as exc:
        run(fetcher.fetch_and_audit("https://example.com"))
    assert exc.value.status_code == 413


def test_normal_page_is_audited(monkeypatch):
    async def ok(client, url):
        return httpx.Response(200, text="<html></html>", request=httpx.Request("GET", url))

    async def fake_audit(html, final_url, ms):
        return {"ok": True}

    monkeypatch.setattr(fetcher, "safe_get", ok)
    monkeypatch.setattr(fetcher, "run_audit", fake_audit)
    assert run(fetcher.fetch_and_audit("https://example.com")) == {"ok": True}
