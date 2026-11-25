"""Rate limiting tests (task 4)."""
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import app.api.analyze as analyze_mod
from app.core.rate_limit import RateLimiter
from app.main import app

client = TestClient(app)


def test_rate_limiter_allows_then_blocks():
    rl = RateLimiter(max_calls=2, window_seconds=60)
    rl.check("ip1")
    rl.check("ip1")
    with pytest.raises(HTTPException) as exc:
        rl.check("ip1")
    assert exc.value.status_code == 429


def test_rate_limiter_keys_are_independent():
    rl = RateLimiter(max_calls=1, window_seconds=60)
    rl.check("a")
    rl.check("b")  # a different client is not affected
    with pytest.raises(HTTPException):
        rl.check("a")


def test_analyze_endpoint_is_rate_limited(monkeypatch):
    async def fake_fetch(url):
        return {"ok": True}

    monkeypatch.setattr(analyze_mod, "fetch_and_audit", fake_fetch)
    analyze_mod._analyze_limiter._hits.clear()

    for _ in range(10):  # the limit is 10/minute
        assert client.get("/analyze?url=https://example.com").status_code == 200
    # the 11th request from the same client is rejected
    assert client.get("/analyze?url=https://example.com").status_code == 429
