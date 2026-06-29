"""Tests for the SQLite data access layer.

These exercise the database functions directly within an app context so the
request-scoped connection on ``g`` is available.
"""

from __future__ import annotations

from app import database


def test_init_creates_table(app):
    with app.app_context():
        database.init_db()
        db = database.get_db()
        row = db.execute(
            "SELECT name FROM sqlite_master " "WHERE type='table' AND name='tasks';"
        ).fetchone()
        assert row is not None
        assert row["name"] == "tasks"


def test_insert_and_retrieve(app):
    with app.app_context():
        task_id = database.create_task("write tests", "cover the db layer")
        task = database.get_task(task_id)
        assert task is not None
        assert task["title"] == "write tests"
        assert task["description"] == "cover the db layer"
        assert task["is_completed"] == 0


def test_get_all_returns_everything(app):
    with app.app_context():
        database.create_task("one")
        database.create_task("two")
        database.create_task("three")
        tasks = database.get_tasks()
        assert len(tasks) == 3
        titles = {t["title"] for t in tasks}
        assert titles == {"one", "two", "three"}


def test_update_marks_completed(app):
    with app.app_context():
        task_id = database.create_task("complete me")
        affected = database.complete_task(task_id)
        assert affected == 1
        assert database.get_task(task_id)["is_completed"] == 1


def test_delete_removes(app):
    with app.app_context():
        task_id = database.create_task("delete me")
        affected = database.delete_task(task_id)
        assert affected == 1
        assert database.get_task(task_id) is None


def test_get_missing_returns_none(app):
    with app.app_context():
        assert database.get_task(424242) is None
