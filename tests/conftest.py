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
