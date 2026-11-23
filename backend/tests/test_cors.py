"""Tests for CORS configuration (task 3, finding 6 + review follow-up).

The app is served same-origin, so CORS is not needed in production. Origins are
now driven solely by CORS_ALLOWED_ORIGINS with an empty default: nothing is
allowed cross-origin unless it is explicitly configured, so no default (such as
localhost) ships to production.
"""
from fastapi.testclient import TestClient

from app.core.constants import parse_origins
from app.main import app

client = TestClient(app)


def test_foreign_origin_is_not_allowed():
    r = client.get("/comments", headers={"Origin": "https://evil.com"})
    assert r.headers.get("access-control-allow-origin") != "https://evil.com"
    assert r.headers.get("access-control-allow-origin") != "*"


def test_no_cross_origin_allowed_by_default():
    # With CORS_ALLOWED_ORIGINS unset, even localhost is not echoed back.
    r = client.get("/comments", headers={"Origin": "http://localhost:3012"})
    assert r.headers.get("access-control-allow-origin") is None


def test_parse_origins_empty_by_default():
    assert parse_origins("") == []


def test_parse_origins_splits_and_strips():
    assert parse_origins("https://a.com, http://b.com ") == [
        "https://a.com",
        "http://b.com",
    ]
