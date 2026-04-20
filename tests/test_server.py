"""Tests for server.py (seed_data, CSRF handler) — raises Sonar coverage on new code."""
import sys
from unittest.mock import MagicMock, patch

import pytest
from flask_wtf.csrf import CSRFError


@pytest.fixture
def users_snapshot(app):
    """Backup users collection, restore after test (mongomock singleton)."""
    from app.db import db

    backup = list(db.users.find({}))
    yield db
    db.users.delete_many({})
    if backup:
        db.users.insert_many(backup)


def test_01_server_seeds_admin_when_db_empty(users_snapshot):
    """Empty users → seed_data inserts default admin (incl. timezone-aware joined_at)."""
    db = users_snapshot
    db.users.delete_many({})

    sys.modules.pop("server", None)
    import server  # noqa: F401 — executes module-level seed_data

    admin = db.users.find_one({"username": "admin"})
    assert admin is not None
    assert admin["full_name"] == "Admin Web"
    assert admin["type"] == 1
    assert admin["email"] == "yourmail@gmail.com"
    assert admin.get("joined_at") is not None


def test_02_server_skips_seed_when_users_exist(users_snapshot):
    """Any existing user → seed_data does not add admin."""
    db = users_snapshot
    db.users.delete_many({})
    db.users.insert_one({
        "full_name": "Existing",
        "username": "existing_only",
        "password": "hashed",
        "email": "e@example.com",
        "type": 0,
    })

    sys.modules.pop("server", None)
    import server  # noqa: F401

    assert db.users.count_documents({}) == 1
    assert db.users.find_one({"username": "admin"}) is None


def test_03_server_seed_skips_logger_when_insert_has_no_inserted_id(users_snapshot):
    """Branch where insert_one returns no inserted_id (lines 29-30)."""
    db = users_snapshot
    db.users.delete_many({})
    with patch.object(db.users, "insert_one", return_value=MagicMock(inserted_id=None)):
        sys.modules.pop("server", None)
        import server  # noqa: F401
    assert db.users.find_one({"username": "admin"}) is None


def test_04_server_csrf_error_handler_returns_fail_json(app):
    """CSRF error handler returns JSON failure payload."""
    sys.modules.pop("server", None)
    import server

    with server.app.app_context():
        with server.app.test_request_context():
            resp = server.error_csrf(CSRFError())

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "fail"
    assert "CSRF" in body["errors"]
