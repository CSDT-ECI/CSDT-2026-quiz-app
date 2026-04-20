"""Tests for API views in app/api/views.py."""
import json
from unittest.mock import MagicMock, patch

from app.modules.utils import generate_password


def test_add_account_success(client):
    """Registering a new user should return success."""
    response = client.post(
        "/api/add-account",
        data=json.dumps({
            "full_name": "New User",
            "username": "newuser",
            "password": "secret123",
            "password_confirmation": "secret123",
            "email": "newuser@example.com",
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"


def test_add_account_duplicate_username(client):
    """Registering with an existing username should fail."""
    user_data = {
        "full_name": "Test User",
        "username": "duplicateuser",
        "password": "secret123",
        "password_confirmation": "secret123",
        "email": "first@example.com",
    }
    client.post("/api/add-account", data=json.dumps(user_data), content_type="application/json")

    user_data["email"] = "second@example.com"
    response = client.post("/api/add-account", data=json.dumps(user_data), content_type="application/json")
    data = response.get_json()
    assert data["status"] == "fail"


def test_add_account_missing_fields(client):
    """Registering without required fields should fail."""
    response = client.post(
        "/api/add-account",
        data=json.dumps({"username": "x"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "fail"


def test_api_login_success(client):
    """Logging in with valid credentials should succeed."""
    # First register
    client.post(
        "/api/add-account",
        data=json.dumps({
            "full_name": "Login User",
            "username": "loginuser",
            "password": "secret123",
            "password_confirmation": "secret123",
            "email": "login@example.com",
        }),
        content_type="application/json",
    )

    # Then login
    response = client.post(
        "/api/login",
        data=json.dumps({"username": "loginuser", "password": "secret123"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"


def test_api_login_wrong_password(client):
    """Logging in with wrong password should fail."""
    client.post(
        "/api/add-account",
        data=json.dumps({
            "full_name": "Wrong Pw User",
            "username": "wrongpwuser",
            "password": "correct123",
            "password_confirmation": "correct123",
            "email": "wrongpw@example.com",
        }),
        content_type="application/json",
    )

    response = client.post(
        "/api/login",
        data=json.dumps({"username": "wrongpwuser", "password": "badpassword"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "fail"


def test_api_login_nonexistent_user(client):
    """Logging in with a user that doesn't exist should fail."""
    response = client.post(
        "/api/login",
        data=json.dumps({"username": "ghost", "password": "nope"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "fail"


def test_show_users_returns_json(client):
    """GET /api/users should return a JSON list."""
    response = client.get("/api/users")
    data = response.get_json()
    assert "data" in data


def test_change_password_not_logged_in(client):
    """Changing password without being logged in should fail."""
    response = client.post(
        "/api/change-password",
        data=json.dumps({"old_password": "x", "password": "new123", "password_confirmation": "new123"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "fail"


def test_edit_profile_requires_login(client):
    """Editing profile without login should redirect."""
    response = client.post(
        "/api/edit-profile",
        data=json.dumps({"username": "hacker", "email": "h@h.com"}),
        content_type="application/json",
    )
    assert response.status_code == 302


def test_add_account_insert_without_inserted_id(client):
    """If insert_one returns no inserted_id, add_account should fail (line 42)."""
    mock_result = MagicMock()
    mock_result.inserted_id = None
    payload = {
        "full_name": "No Id User",
        "username": "noiduser",
        "password": "secret123",
        "password_confirmation": "secret123",
        "email": "noid@example.com",
    }
    with patch("app.api.views.db.users.insert_one", return_value=mock_result):
        response = client.post(
            "/api/add-account",
            data=json.dumps(payload),
            content_type="application/json",
        )
    data = response.get_json()
    assert data["status"] == "fail"
    assert data.get("errors") == "unkown failure"


def test_add_account_insert_raises_exception(client):
    """DB exception during insert should be returned in errors (lines 43-44)."""
    payload = {
        "full_name": "Boom User",
        "username": "boomuser",
        "password": "secret123",
        "password_confirmation": "secret123",
        "email": "boom@example.com",
    }
    with patch(
        "app.api.views.db.users.insert_one",
        side_effect=RuntimeError("database unavailable"),
    ):
        response = client.post(
            "/api/add-account",
            data=json.dumps(payload),
            content_type="application/json",
        )
    data = response.get_json()
    assert data["status"] == "fail"
    assert "database unavailable" in data.get("errors", "")


def test_api_login_invalid_form_returns_fail(client):
    """When LoginForm.validate() is false, api_login should not check password (line 87)."""
    with patch("app.api.views.LoginForm") as mock_form_cls:
        instance = mock_form_cls.return_value
        instance.validate.return_value = False
        response = client.post(
            "/api/login",
            data=json.dumps({"username": "any", "password": "any"}),
            content_type="application/json",
        )
    data = response.get_json()
    assert data["status"] == "fail"
    assert "invalid username" in data.get("errors", "").lower()


def test_manage_users_unpromote(admin_client, registered_user):
    """Admin unpromote option updates user type to 0 (lines 60-62)."""
    with admin_client.application.app_context():
        from app.db import db

        db.users.update_one(
            {"username": registered_user["username"]},
            {"$set": {"type": 1}},
        )

    response = admin_client.post(
        "/api/manage-users",
        data=json.dumps({
            "option": "unpromote",
            "data": [registered_user["username"]],
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"

    with admin_client.application.app_context():
        from app.db import db

        doc = db.users.find_one({"username": registered_user["username"]})
    assert doc.get("type") == 0


def test_edit_profile_duplicate_username(app, logged_in_client, registered_user):
    """Changing username to one owned by another user should fail (lines 112-113)."""
    from app.db import db

    with app.app_context():
        db.users.insert_one({
            "full_name": "Taken User",
            "username": "takenname",
            "email": "takenname@example.com",
            "password": generate_password("pass123"),
            "type": 0,
        })

    response = logged_in_client.post(
        "/api/edit-profile",
        data=json.dumps({
            "username": "takenname",
            "email": registered_user["email"],
            "full_name": registered_user["full_name"],
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "failed"
    assert "username" in data.get("message", "").lower()
