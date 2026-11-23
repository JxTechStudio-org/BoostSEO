"""DNS rebinding tests (task 3, finding 1 review follow-up).

Validating a hostname and then letting the HTTP client resolve it a second time
is a TOCTOU gap: the name can return a public IP during the check and an
internal one when the client connects (DNS rebinding). The guard now resolves
once and pins the request to the validated IP, keeping the hostname only in the
Host header and the TLS SNI. These tests prove the request is pinned.
"""
import asyncio

import httpx
import pytest

from app.core.url_guard import UnsafeURLError, safe_get


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


class _RecordingClient:
    """Stands in for an httpx client and records the request it is handed."""

    def __init__(self):
        self.calls = []

    async def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": str(url), **kwargs})
        return httpx.Response(200, text="ok")


def test_request_is_pinned_to_validated_ip(monkeypatch):
    # The hostname resolves to a public IP at validation time.
    async def fake_resolve(host):
        return {"8.8.8.8"}

    monkeypatch.setattr("app.core.url_guard._resolve", fake_resolve)

    client = _RecordingClient()
    resp = run(safe_get(client, "https://rebind.example.com/path?q=1"))
    assert resp.status_code == 200

    call = client.calls[0]
    # The connection goes to the validated IP, not the hostname (so the client
    # cannot re-resolve the name to an internal address).
    assert "8.8.8.8" in call["url"]
    assert "rebind.example.com" not in call["url"]
    assert "q=1" in call["url"]  # path and query are preserved
    # The hostname is preserved for routing and TLS certificate verification.
    assert call["headers"]["Host"] == "rebind.example.com"
    assert call["extensions"] == {"sni_hostname": "rebind.example.com"}


def test_pinned_request_still_blocks_internal_resolution(monkeypatch):
    # A name that resolves to an internal address is rejected before any
    # request is made (pinning never reaches a blocked IP).
    async def fake_resolve(host):
        return {"169.254.169.254"}

    monkeypatch.setattr("app.core.url_guard._resolve", fake_resolve)

    client = _RecordingClient()
    with pytest.raises(UnsafeURLError):
        run(safe_get(client, "https://rebind.example.com/"))
    assert client.calls == []  # no request was ever sent
