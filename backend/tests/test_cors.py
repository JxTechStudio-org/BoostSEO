"""Tests for CORS configuration (task 3, finding 6)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_foreign_origin_is_not_allowed():
    r = client.get("/comments", headers={"Origin": "https://evil.com"})
    assert r.headers.get("access-control-allow-origin") != "https://evil.com"
    assert r.headers.get("access-control-allow-origin") != "*"


def test_known_origin_is_allowed():
    origin = "http://localhost:3012"
    r = client.get("/comments", headers={"Origin": origin})
    assert r.headers.get("access-control-allow-origin") == origin
