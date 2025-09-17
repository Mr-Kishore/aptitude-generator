"""
Test package for the Aptitude Generator application.

This package contains all the test modules for the application.
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
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()

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
    
    def login(self, username='test', password='test'):
        """Log in as a test user."""
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):
        """Log out the current user."""
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """Authentication test helper."""
    return AuthActions(client)


@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(username='test', email='test@example.com', password='test')
    db.session.add(user)
    db.session.commit()
    return user
