"""Tests for the Flask application."""


def test_main_index_returns_200(client):
    """Main index page should return 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_auth_index_returns_200(client):
    """Auth index page should return 200."""
    response = client.get("/auth/")
    assert response.status_code == 200


def test_auth_login_returns_200(client):
    """Login page should return 200."""
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_auth_register_returns_200(client):
    """Register page should return 200."""
    response = client.get("/auth/register")
    assert response.status_code == 200


def test_quiz_landing_returns_200(client):
    """Quiz landing page should return 200."""
    response = client.get("/quiz/")
    assert response.status_code == 200


def test_quiz_homepage_returns_200(client):
    """Quiz start page with code should return 200."""
    response = client.get("/quiz/start/abc123")
    assert response.status_code == 200


def test_dashboard_redirects_without_login(client):
    """Dashboard should redirect to login when not authenticated."""
    response = client.get("/dashboard/")
    assert response.status_code == 302
    assert "/auth/login" in response.location or "login" in response.location


def test_app_creation(app):
    """App should be created successfully with testing config."""
    assert app is not None
    assert app.config["TESTING"] is True
