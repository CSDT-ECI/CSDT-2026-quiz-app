"""Pytest configuration and fixtures."""
import os
from unittest.mock import patch, MagicMock

import pytest
import mongomock


@pytest.fixture(autouse=True)
def mock_mongodb():
    """Patch MongoDB to use mongomock for all tests."""
    with patch.dict(os.environ, {"MONGODB_URI": "mongodb://localhost"}):
        with patch("app.modules.mongo.MongoClient", mongomock.MongoClient):
            with patch("config.GeneralConfig.MONGODB_URI", "mongodb://localhost"):
                yield


@pytest.fixture
def app(mock_mongodb):
    """Create and return the Flask application."""
    from app import create_app, csrf_protect

    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    csrf_protect.protect = MagicMock()
    return app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def sample_user_data():
    """Return valid user registration data."""
    return {
        "full_name": "Test User",
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123",
        "password_confirmation": "secret123",
    }


@pytest.fixture
def registered_user(app, sample_user_data):
    """Insert a user directly into the mock DB and return their data."""
    from app.db import db
    from app.modules.utils import generate_password

    user = dict(sample_user_data)
    user["password"] = generate_password(sample_user_data["password"])
    user["type"] = 0
    with app.app_context():
        db.users.insert_one(user)
    return sample_user_data  # return plain-text password version


@pytest.fixture
def admin_user(app):
    """Insert an admin user into the mock DB."""
    from app.db import db
    from app.modules.utils import generate_password

    data = {
        "full_name": "Admin User",
        "username": "adminuser",
        "email": "admin@example.com",
        "password": generate_password("admin123"),
        "type": 1,
    }
    with app.app_context():
        db.users.insert_one(data)
    return {"username": "adminuser", "password": "admin123", "type": 1}


@pytest.fixture
def logged_in_client(app, registered_user):
    """Return a test client with an active session for a regular user."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["username"] = registered_user["username"]
        sess["name"] = registered_user["full_name"]
        sess["type"] = 0
        sess["email"] = registered_user["email"]
    return client


@pytest.fixture
def admin_client(app, admin_user):
    """Return a test client with an active session for an admin user."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["username"] = admin_user["username"]
        sess["name"] = "Admin User"
        sess["type"] = 1
        sess["email"] = "admin@example.com"
    return client


@pytest.fixture
def sample_quiz(app, logged_in_client):
    """Insert a quiz into the mock DB and return its code."""
    from app.db import quiz as quiz_col

    quiz_data = {
        "code": "test01",
        "author": "testuser",
        "quiz_title": "Sample Quiz",
        "data": [
            {
                "question": "What is 2+2?",
                "a_option": "3",
                "b_option": "4",
                "c_option": "5",
                "d_option": "6",
                "answer": "b",
            },
            {
                "question": "What color is the sky?",
                "a_option": "red",
                "b_option": "green",
                "c_option": "blue",
                "d_option": "yellow",
                "answer": "c",
            },
        ],
    }
    with app.app_context():
        quiz_col.insert_one(quiz_data)
    return "test01"
