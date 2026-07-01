"""Tests for the notes CRUD endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_empty_initially(client: TestClient) -> None:
    resp = client.get("/notes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_note(client: TestClient) -> None:
    resp = client.post("/notes", json={"title": "First", "content": "hello"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["title"] == "First"
    assert body["content"] == "hello"

    # It now shows up in the list.
    listing = client.get("/notes").json()
    assert len(listing) == 1


def test_create_note_defaults_empty_content(client: TestClient) -> None:
    resp = client.post("/notes", json={"title": "No content"})
    assert resp.status_code == 201
    assert resp.json()["content"] == ""


def test_get_existing_note(client: TestClient) -> None:
    created = client.post("/notes", json={"title": "Look me up"}).json()
    resp = client.get(f"/notes/{created['id']}")
    assert resp.status_code == 200
    assert resp.json() == created


def test_get_missing_note_returns_404(client: TestClient) -> None:
    resp = client.get("/notes/999")
    assert resp.status_code == 404


def test_update_existing_note(client: TestClient) -> None:
    created = client.post("/notes", json={"title": "Old", "content": "old"}).json()
    resp = client.put(
        f"/notes/{created['id']}",
        json={"title": "New", "content": "new"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == created["id"]
    assert body["title"] == "New"
    assert body["content"] == "new"


def test_update_missing_note_returns_404(client: TestClient) -> None:
    resp = client.put("/notes/999", json={"title": "Nope"})
    assert resp.status_code == 404


def test_delete_existing_note(client: TestClient) -> None:
    created = client.post("/notes", json={"title": "Delete me"}).json()
    resp = client.delete(f"/notes/{created['id']}")
    assert resp.status_code == 204

    # It is gone afterwards.
    assert client.get(f"/notes/{created['id']}").status_code == 404


def test_delete_missing_note_returns_404(client: TestClient) -> None:
    resp = client.delete("/notes/999")
    assert resp.status_code == 404
