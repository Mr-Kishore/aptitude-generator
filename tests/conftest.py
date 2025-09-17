"""
Test configuration and fixtures.

This file contains pytest fixtures and configuration for the test suite.
"""
import os
import tempfile
import pytest
from app import create_app
from app.models.user import User, ExcelUserStore


@pytest.fixture
def app(tmp_path):
    """Create and configure a new app instance for testing (Excel store)."""
    # Point ExcelUserStore to a temp file
    excel_path = tmp_path / 'users.xlsx'
    original_file = ExcelUserStore.FILE_NAME
    ExcelUserStore.FILE_NAME = str(excel_path)

    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })

    # Create a test user in the Excel store
    with app.app_context():
        user = User(username='testuser', email='test@example.com', password='testpass123')
        ExcelUserStore.add(user)

    yield app

    # Restore file name and cleanup
    ExcelUserStore.FILE_NAME = original_file
    try:
        if os.path.exists(str(excel_path)):
            os.remove(str(excel_path))
    except Exception:
        pass


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions:
    """Helper class for testing authentication."""
    def __init__(self, client):
        self._client = client

    def login(self, username='testuser', password='testpass123'):
        """Log in a test user."""
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        """Log out the current user."""
        return self._client.get('/auth/logout', follow_redirects=True)


@pytest.fixture
def auth(client):
    """Fixture for authentication test helpers."""
    return AuthActions(client)
