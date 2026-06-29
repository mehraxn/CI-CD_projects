"""Tests for the HTTP route handlers."""

from __future__ import annotations


def test_homepage_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_task_list_loads(client):
    resp = client.get("/tasks")
    assert resp.status_code == 200


def test_create_page_loads(client):
    resp = client.get("/tasks/new")
    assert resp.status_code == 200


def test_create_valid_task(client):
    resp = client.post(
        "/tasks/new",
        data={"title": "Ship pipeline", "description": "wire up CI"},
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_created_task_appears_in_list(client):
    client.post("/tasks/new", data={"title": "Visible task"})
    resp = client.get("/tasks")
    assert b"Visible task" in resp.data


def test_empty_title_rejected(client):
    resp = client.post("/tasks/new", data={"title": "", "description": "x"})
    assert resp.status_code == 400
    assert b"Title is required" in resp.data


def test_whitespace_title_rejected(client):
    resp = client.post("/tasks/new", data={"title": "    "})
    assert resp.status_code == 400
    assert b"Title is required" in resp.data


def test_over_max_length_title_rejected(client):
    resp = client.post("/tasks/new", data={"title": "a" * 121})
    assert resp.status_code == 400
    assert b"characters or fewer" in resp.data


def test_complete_task(client):
    client.post("/tasks/new", data={"title": "finish me"})
    resp = client.post("/tasks/1/complete", follow_redirects=True)
    assert resp.status_code == 200
    assert b"completed" in resp.data


def test_delete_task(client):
    client.post("/tasks/new", data={"title": "remove me"})
    resp = client.post("/tasks/1/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert b"remove me" not in resp.data


def test_complete_missing_task_does_not_error(client):
    resp = client.post("/tasks/999/complete", follow_redirects=True)
    assert resp.status_code == 200


def test_delete_missing_task_does_not_error(client):
    resp = client.post("/tasks/999/delete", follow_redirects=True)
    assert resp.status_code == 200
