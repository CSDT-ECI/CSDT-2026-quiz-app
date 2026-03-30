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
