import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import comments as comments_api
from app.services.comments_store import CommentsStore


@pytest.fixture
def client(tmp_path):
    test_store = CommentsStore(tmp_path / "test_comments.db")
    app.dependency_overrides[comments_api.get_store] = lambda: test_store
    comments_api._last_submission.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_valid_submission_returns_201_without_email(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "Great tool!"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane"
    assert data["body"] == "Great tool!"
    assert "email" not in data
    assert "id" in data
    assert "created_at" in data


def test_missing_field_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com"},
    )

    assert response.status_code == 422


def test_blank_field_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "   ", "email": "jane@example.com", "body": "Great tool!"},
    )

    assert response.status_code == 422


def test_malformed_email_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "not-an-email", "body": "Great tool!"},
    )

    assert response.status_code == 422


def test_body_too_long_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "x" * 2001},
    )

    assert response.status_code == 422


def test_rapid_repeat_submission_returns_429(client):
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    first = client.post("/comments", json=payload)
    second = client.post("/comments", json=payload)

    assert first.status_code == 201
    assert second.status_code == 429


def test_different_forwarded_ips_are_not_rate_limited_against_each_other(client):
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    first = client.post("/comments", json=payload, headers={"X-Forwarded-For": "1.2.3.4"})
    second = client.post("/comments", json=payload, headers={"X-Forwarded-For": "5.6.7.8"})

    assert first.status_code == 201
    assert second.status_code == 201


def test_same_forwarded_ip_rapid_repeat_returns_429(client):
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    first = client.post("/comments", json=payload, headers={"X-Forwarded-For": "9.9.9.9"})
    second = client.post("/comments", json=payload, headers={"X-Forwarded-For": "9.9.9.9"})

    assert first.status_code == 201
    assert second.status_code == 429


def test_spoofed_forwarded_for_cannot_bypass_rate_limit_when_real_ip_matches(client):
    # Simulates real nginx behavior: X-Real-IP is always the true socket
    # peer (nginx overwrites it, so it can't be spoofed), while
    # X-Forwarded-For can be freely set/prepended by the client. A previous
    # version of the rate limiter trusted the first X-Forwarded-For hop,
    # letting an attacker bypass the limit by varying that header on every
    # request. With the same real IP but different (attacker-controlled)
    # X-Forwarded-For values, the second request must still be rate limited.
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    first = client.post(
        "/comments",
        json=payload,
        headers={"X-Real-IP": "9.9.9.9", "X-Forwarded-For": "spoofed-1"},
    )
    second = client.post(
        "/comments",
        json=payload,
        headers={"X-Real-IP": "9.9.9.9", "X-Forwarded-For": "spoofed-2"},
    )

    assert first.status_code == 201
    assert second.status_code == 429


def test_last_submission_entries_are_pruned_after_expiry(client):
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    response = client.post(
        "/comments", json=payload, headers={"X-Real-IP": "42.42.42.42"}
    )
    assert response.status_code == 201
    assert "42.42.42.42" in comments_api._last_submission

    # Backdate the recorded submission time so it looks like it happened
    # longer ago than the rate-limit window, without a real sleep.
    comments_api._last_submission["42.42.42.42"] = (
        time.time() - comments_api.RATE_LIMIT_SECONDS - 1
    )

    # A submission from a *different* IP triggers the pruning sweep inside
    # create_comment, which should evict the now-expired entry above.
    other_response = client.post(
        "/comments", json=payload, headers={"X-Real-IP": "1.1.1.1"}
    )
    assert other_response.status_code == 201
    assert "42.42.42.42" not in comments_api._last_submission


def test_honeypot_field_returns_fake_success_without_persisting(client):
    response = client.post(
        "/comments",
        json={
            "name": "Bot",
            "email": "bot@example.com",
            "body": "Buy cheap stuff now!",
            "website": "http://spam.example.com",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bot"
    assert data["body"] == "Buy cheap stuff now!"
    assert "id" in data
    assert "created_at" in data

    listed = client.get("/comments")
    assert listed.status_code == 200
    assert listed.json() == []


def test_honeypot_field_does_not_trigger_rate_limit(client):
    payload = {
        "name": "Bot",
        "email": "bot@example.com",
        "body": "Spam!",
        "website": "http://spam.example.com",
    }

    first = client.post("/comments", json=payload, headers={"X-Real-IP": "7.7.7.7"})
    assert first.status_code == 201

    # A real submission from the same IP right after should still succeed,
    # proving the honeypot POST never touched the rate limiter for this IP.
    real = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "Great tool!"},
        headers={"X-Real-IP": "7.7.7.7"},
    )
    assert real.status_code == 201


def test_absent_website_field_still_works_as_before(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "Great tool!"},
    )

    assert response.status_code == 201
    listed = client.get("/comments")
    assert len(listed.json()) == 1


def test_get_comments_never_includes_email(client):
    client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "Nice!"},
    )

    response = client.get("/comments")

    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 1
    assert "email" not in comments[0]
    assert comments[0]["name"] == "Jane"
