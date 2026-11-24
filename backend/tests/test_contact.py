"""Tests for the contact form endpoint (task 6)."""
from fastapi.testclient import TestClient

import app.api.contact as contact_mod
from app.main import app

client = TestClient(app)


def test_valid_contact_sends_and_returns_sent(monkeypatch):
    sent = {}

    def fake_send(email, message):
        sent["email"] = email
        sent["message"] = message

    monkeypatch.setattr(contact_mod, "send_contact_email", fake_send)
    r = client.post("/contact", json={"email": "a@b.com", "message": "Hello there"})
    assert r.status_code == 200
    assert r.json() == {"status": "sent"}
    assert sent == {"email": "a@b.com", "message": "Hello there"}


def test_invalid_email_is_rejected():
    r = client.post("/contact", json={"email": "not-an-email", "message": "hi"})
    assert r.status_code == 422


def test_empty_message_is_rejected():
    r = client.post("/contact", json={"email": "a@b.com", "message": "   "})
    assert r.status_code == 422


def test_honeypot_is_accepted_without_sending(monkeypatch):
    calls = {"n": 0}

    def fake_send(email, message):
        calls["n"] += 1

    monkeypatch.setattr(contact_mod, "send_contact_email", fake_send)
    r = client.post(
        "/contact",
        json={"email": "a@b.com", "message": "hi", "website": "spam"},
    )
    assert r.status_code == 200
    assert calls["n"] == 0  # nothing was sent


def test_unconfigured_email_returns_503(monkeypatch):
    def fake_send(email, message):
        raise contact_mod.EmailNotConfigured("no smtp")

    monkeypatch.setattr(contact_mod, "send_contact_email", fake_send)
    r = client.post("/contact", json={"email": "a@b.com", "message": "hi"})
    assert r.status_code == 503
