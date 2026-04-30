"""Tests for dashboard views in app/dashboard/views.py."""
import json
import io


def test_dashboard_index_authenticated(logged_in_client):
    """Authenticated user should access the dashboard index."""
    response = logged_in_client.get("/dashboard/")
    assert response.status_code == 200


def test_manage_quiz_returns_200(logged_in_client):
    """Manage quiz page should return 200 for authenticated user."""
    response = logged_in_client.get("/dashboard/manage-quiz")
    assert response.status_code == 200


def test_manage_quiz_admin_sees_all(admin_client):
    """Admin user should access manage-quiz page."""
    response = admin_client.get("/dashboard/manage-quiz")
    assert response.status_code == 200


def test_change_password_page_returns_200(logged_in_client):
    """Change password page should be accessible for logged-in users."""
    response = logged_in_client.get("/dashboard/change-password")
    assert response.status_code == 200


def test_profile_page_returns_200(logged_in_client):
    """Profile page should be accessible for logged-in users."""
    response = logged_in_client.get("/dashboard/profile")
    assert response.status_code == 200


def test_scores_page_returns_200(logged_in_client):
    """Scores page should return 200 for authenticated user."""
    response = logged_in_client.get("/dashboard/scores")
    assert response.status_code == 200


def test_users_scores_page_returns_200(logged_in_client):
    """Users-scores page should return 200 (duplicate route)."""
    response = logged_in_client.get("/dashboard/users-scores")
    assert response.status_code == 200


def test_upload_quiz_page_returns_200(logged_in_client):
    """Upload quiz page should return 200 for authenticated user."""
    response = logged_in_client.get("/dashboard/upload-quiz")
    assert response.status_code == 200


def test_add_quizes_page_returns_200(logged_in_client):
    """Add quizzes page should return 200 for authenticated user."""
    response = logged_in_client.get("/dashboard/add-quizes")
    assert response.status_code == 200


def test_logout_clears_session_and_redirects(logged_in_client):
    """Logging out should clear session and redirect to login."""
    response = logged_in_client.get("/dashboard/logout")
    assert response.status_code == 302
    assert "login" in response.location

    # After logout, dashboard should redirect again
    follow = logged_in_client.get("/dashboard/")
    assert follow.status_code == 302


def test_delete_quiz_redirects_to_manage(logged_in_client, sample_quiz):
    """Deleting a quiz should redirect to manage-quiz page."""
    response = logged_in_client.get(f"/dashboard/delete-quiz/{sample_quiz}")
    assert response.status_code == 302
    assert "manage-quiz" in response.location


def test_delete_quiz_nonexistent_code_redirects(logged_in_client):
    """Deleting a non-existent quiz should still redirect (no crash)."""
    response = logged_in_client.get("/dashboard/delete-quiz/doesnotexist")
    assert response.status_code == 302


def test_delete_quiz_owner_removes_document(app, logged_in_client, registered_user):
    """Owner delete should remove the quiz document (lines 113-115).

    Uses a unique code: ``app.db`` is module singleton; other tests may leave ``test01`` rows.
    """
    from app.db import quiz as quiz_col

    code = "del_owner_unique"
    with app.app_context():
        quiz_col.insert_one({
            "code": code,
            "author": registered_user["username"],
            "quiz_title": "Delete me",
            "data": [],
        })
        assert quiz_col.find_one({"code": code}) is not None

    response = logged_in_client.get(f"/dashboard/delete-quiz/{code}")
    assert response.status_code == 302

    with app.app_context():
        assert quiz_col.find_one({"code": code}) is None


def test_edit_quiz_owner_can_access(logged_in_client, sample_quiz):
    """Quiz owner should be able to access the edit page."""
    response = logged_in_client.get(f"/dashboard/edit-quiz/{sample_quiz}")
    assert response.status_code == 200


def test_edit_quiz_non_owner_forbidden(app, registered_user, sample_quiz):
    """A user who is not the quiz owner should get 403."""
    other_client = app.test_client()
    with other_client.session_transaction() as sess:
        sess["username"] = "otheruser"
        sess["name"] = "Other User"
        sess["type"] = 0
        sess["email"] = "other@example.com"

    response = other_client.get(f"/dashboard/edit-quiz/{sample_quiz}")
    assert response.status_code == 403


def test_edit_quiz_admin_can_access_any(admin_client, sample_quiz):
    """Admin should be able to access any quiz's edit page."""
    response = admin_client.get(f"/dashboard/edit-quiz/{sample_quiz}")
    assert response.status_code == 200


def test_manage_users_requires_admin(logged_in_client):
    """Manage users page should redirect non-admin users."""
    response = logged_in_client.get("/dashboard/manage-users")
    assert response.status_code == 302


def test_manage_users_accessible_by_admin(admin_client):
    """Admin should be able to access the manage users page."""
    response = admin_client.get("/dashboard/manage-users")
    assert response.status_code == 200


def test_download_quiz_returns_json_attachment(logged_in_client, sample_quiz):
    """download_quiz should return JSON with Content-Disposition (lines 29-49)."""
    response = logged_in_client.get(f"/dashboard/quiz/download/{sample_quiz}")
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    disp = response.headers.get("Content-Disposition", "")
    assert "attachment" in disp.lower()
    assert sample_quiz in disp


def test_export_quiz_existing_returns_response(logged_in_client, sample_quiz):
    """export_quiz with existing code returns 200 (lines 149-154)."""
    response = logged_in_client.get(f"/dashboard/export-quiz/{sample_quiz}")
    assert response.status_code == 200
    assert len(response.data) > 0


def test_export_quiz_missing_code_returns_no(client):
    """export_quiz with unknown code returns literal 'no' (line 155)."""
    response = client.get("/dashboard/export-quiz/doesnotexist999")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "no"
