"""
Tests for database models.

This module contains tests for the User model and other database models.
"""
import pytest
from app.models.user import User, ExcelUserStore
from werkzeug.security import check_password_hash


def test_user_model(app):
    ""Test the User model."""
    with app.app_context():
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        ExcelUserStore.add(user)

        # Test user attributes
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.is_authenticated is True
        assert user.is_anonymous is False
        
        # Test password hashing
        assert user.password_hash is not None
        assert user.password_hash != 'testpass123'
        assert user.check_password('testpass123') is True
        assert user.check_password('wrongpassword') is False
        
        # Test get_id method
        assert user.get_id() == user.username


def test_user_repr(app):
    ""Test the __repr__ method of the User model."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        assert repr(user) == f"<User testuser>"


def test_set_password(app):
    ""Test the set_password method."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('newpassword')
        
        assert user.password_hash is not None
        assert user.check_password('newpassword') is True
        assert user.check_password('wrongpassword') is False


def test_user_authentication(app, client):
    ""Test user authentication flow."""
    with app.app_context():
        # Create a test user
        user = User(
            username='authuser',
            email='auth@example.com',
            password='authpass123'
        )
        ExcelUserStore.add(user)
        
        # Test login with correct credentials
        response = client.post(
            '/auth/login',
            data={
                'username': 'authuser',
                'password': 'authpass123'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'You have been logged in' in response.data
        
        # Test accessing protected route
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'Welcome' in response.data
        assert b'authuser' in response.data
        
        # Test logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert b'You have been logged out' in response.data
        
        # Test accessing protected route after logout
        response = client.get('/dashboard', follow_redirects=True)
        assert b'Please log in to access this page' in response.data
