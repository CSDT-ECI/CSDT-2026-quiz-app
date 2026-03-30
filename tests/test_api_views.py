"""Tests for API views in app/api/views.py."""
import json

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
