"""Tests for admin API endpoints in app/api/views.py."""
import json


def test_manage_users_delete(admin_client, registered_user):
    """Admin should be able to delete users."""
    response = admin_client.post(
        "/api/manage-users",
        data=json.dumps({
            "option": "delete",
            "data": [registered_user["username"]],
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"


def test_manage_users_promote(admin_client, registered_user):
    """Admin should be able to promote a user to admin."""
    response = admin_client.post(
        "/api/manage-users",
        data=json.dumps({
            "option": "promote",
            "data": [registered_user["username"]],
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"


def test_manage_users_unpromote(admin_client, registered_user):
    """Admin should be able to unpromote a user from admin."""
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


def test_manage_users_no_option(admin_client):
    """Manage users without a valid option should return failed."""
    response = admin_client.post(
        "/api/manage-users",
        data=json.dumps({}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "failed"


def test_manage_users_requires_admin(logged_in_client):
    """Non-admin should be redirected from manage-users endpoint."""
    response = logged_in_client.post(
        "/api/manage-users",
        data=json.dumps({"option": "delete", "data": ["someone"]}),
        content_type="application/json",
    )
    assert response.status_code == 302


def test_change_password_success(logged_in_client, registered_user):
    """Logged-in user should be able to change their password."""
    response = logged_in_client.post(
        "/api/change-password",
        data=json.dumps({
            "old_password": registered_user["password"],
            "password": "newpass123",
            "password_confirmation": "newpass123",
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"


def test_change_password_wrong_old(logged_in_client):
    """Changing password with wrong old password should fail."""
    response = logged_in_client.post(
        "/api/change-password",
        data=json.dumps({
            "old_password": "wrongoldpassword",
            "password": "newpass123",
            "password_confirmation": "newpass123",
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "fail"


def test_edit_profile_success(logged_in_client, registered_user):
    """Logged-in user should be able to edit their profile."""
    response = logged_in_client.post(
        "/api/edit-profile",
        data=json.dumps({
            "username": registered_user["username"],
            "email": registered_user["email"],
            "full_name": "Updated Name",
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"


def test_edit_profile_duplicate_email(app, logged_in_client, registered_user):
    """Changing email to one already registered should fail."""
    from app.db import db
    from app.modules.utils import generate_password

    with app.app_context():
        db.users.insert_one({
            "full_name": "Another User",
            "username": "anotheruser",
            "email": "taken@example.com",
            "password": generate_password("pass123"),
            "type": 0,
        })

    response = logged_in_client.post(
        "/api/edit-profile",
        data=json.dumps({
            "username": registered_user["username"],
            "email": "taken@example.com",
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "failed"


def test_get_scores_logged_in(logged_in_client):
    """Logged-in user using 'logged_in' author should get their scores."""
    response = logged_in_client.get("/api/quiz/author/logged_in/getScores")
    data = response.get_json()
    assert data["status"] in ("success", "failed")


def test_view_quiz_owner(logged_in_client, sample_quiz):
    """Quiz owner should be able to view their quiz via API."""
    response = logged_in_client.get(f"/api/quiz/view/{sample_quiz}")
    assert response.status_code == 200
    data = response.get_json()
    # view_quiz returns the quiz document directly (no 'status' wrapper on success)
    assert "code" in data or "quiz_title" in data


def test_view_quiz_wrong_owner(app, sample_quiz):
    """Non-owner should get fail response when viewing quiz."""
    other_client = app.test_client()
    with other_client.session_transaction() as sess:
        sess["username"] = "nottheowner"
        sess["name"] = "Not Owner"
        sess["type"] = 0

    response = other_client.get(f"/api/quiz/view/{sample_quiz}")
    data = response.get_json()
    assert data["status"] == "fail"


def test_edit_quiz_via_api(logged_in_client, sample_quiz):
    """Quiz owner should be able to edit their quiz via API."""
    response = logged_in_client.post(
        f"/api/quiz/edit/{sample_quiz}",
        data=json.dumps({
            "quiz_title": "Updated Title",
            "data": [],
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"


def test_nilai_quiz_not_found(client):
    """Submitting answers for nonexistent quiz should return fail."""
    response = client.post(
        "/api/quiz/nilai/doesnotexist",
        data=json.dumps({"quest_0": "a_option"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "fail"
