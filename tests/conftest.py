"""
Test configuration and fixtures.

This file contains pytest fixtures and configuration for the test suite.
"""
import os
import tempfile
import pytest
from app import create_app, db
from app.models.user import User


@pytest.fixture
def app():
    """Create and configure a new app instance for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    # Create the app with test configuration
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        db.session.add(user)
        db.session.commit()

    yield app

    # Clean up the database after the test
    os.close(db_fd)
    os.unlink(db_path)


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
