"""Tests for the SSRF URL guard (task 3, finding 1)."""
import asyncio

import httpx
import pytest

from app.core.url_guard import UnsafeURLError, validate_public_url, safe_get


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def test_blocks_loopback_ip():
    with pytest.raises(UnsafeURLError):
        run(validate_public_url("http://127.0.0.1/admin"))


def test_blocks_localhost_name():
    with pytest.raises(UnsafeURLError):
        run(validate_public_url("http://localhost:8000/docs"))


def test_blocks_cloud_metadata():
    with pytest.raises(UnsafeURLError):
        run(validate_public_url("http://169.254.169.254/latest/meta-data/"))


def test_blocks_private_ranges():
    for u in ("http://10.0.0.5/", "http://192.168.1.1/", "http://172.16.0.1/"):
        with pytest.raises(UnsafeURLError):
            run(validate_public_url(u))


def test_blocks_non_http_scheme():
    with pytest.raises(UnsafeURLError):
        run(validate_public_url("file:///etc/passwd"))


def test_allows_public_ip_literal():
    run(validate_public_url("https://8.8.8.8/"))  # should not raise


def test_safe_get_blocks_redirect_to_internal():
    # A public URL that redirects to an internal address must be rejected.
    def handler(request):
        if request.url.host == "8.8.8.8":
            return httpx.Response(302, headers={"location": "http://169.254.169.254/"})
        return httpx.Response(200, text="should not reach here")

    async def go():
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            with pytest.raises(UnsafeURLError):
                await safe_get(client, "https://8.8.8.8/")
    run(go())
