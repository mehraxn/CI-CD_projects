"""Tests for the /health probe endpoint."""

from __future__ import annotations


def test_health_returns_ok_json(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
    assert resp.content_type == "application/json"
