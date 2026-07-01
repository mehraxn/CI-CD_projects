"""Tests for input validation (FastAPI/Pydantic should return 422)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_reject_empty_title(client: TestClient) -> None:
    resp = client.post("/notes", json={"title": "", "content": "x"})
    assert resp.status_code == 422


def test_reject_whitespace_title(client: TestClient) -> None:
    resp = client.post("/notes", json={"title": "   ", "content": "x"})
    assert resp.status_code == 422


def test_reject_missing_title(client: TestClient) -> None:
    resp = client.post("/notes", json={"content": "x"})
    assert resp.status_code == 422


def test_reject_too_long_title(client: TestClient) -> None:
    resp = client.post("/notes", json={"title": "a" * 101})
    assert resp.status_code == 422


def test_reject_too_long_content(client: TestClient) -> None:
    resp = client.post("/notes", json={"title": "ok", "content": "a" * 1001})
    assert resp.status_code == 422


def test_accept_boundary_lengths(client: TestClient) -> None:
    resp = client.post(
        "/notes",
        json={"title": "a" * 100, "content": "b" * 1000},
    )
    assert resp.status_code == 201
