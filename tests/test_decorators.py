"""Tests for authentication decorators in app/modules/decorators.py."""
from flask import session


def test_login_required_redirects_unauthenticated(client):
    """Unauthenticated user should be redirected to login."""
    response = client.get("/dashboard/")
    assert response.status_code == 302
    assert "login" in response.location


def test_login_required_allows_authenticated(app, client):
    """Authenticated user should access protected routes."""
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
        sess["name"] = "Test User"
        sess["type"] = 0

    response = client.get("/dashboard/")
    assert response.status_code == 200


def test_admin_required_redirects_non_admin(client):
    """Non-admin user should be redirected from admin routes."""
    with client.session_transaction() as sess:
        sess["username"] = "regularuser"
        sess["name"] = "Regular User"
        sess["type"] = 0

    response = client.get("/dashboard/manage-users")
    assert response.status_code == 302


def test_admin_required_redirects_unauthenticated(client):
    """Unauthenticated user should be redirected from admin routes."""
    response = client.get("/dashboard/manage-users")
    assert response.status_code == 302
