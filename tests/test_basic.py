"""
Basic tests for the Aptitude Generator application.
"""
import os
import pytest
from app import create_app
from app.models.user import ExcelUserStore


def test_config():
    """Test that the test config works correctly."""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    """Test the hello route."""
    response = client.get('/hello')
    assert response.data == b'Hello, World!'


def test_index(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Aptitude Generator' in response.data


def test_register(client, app):
    """Test user registration."""
    assert client.get('/auth/register').status_code == 200
    
    response = client.post(
        '/auth/register',
        data={
            'username': 'test',
            'email': 'test@example.com',
            'password': 'test',
            'confirm_password': 'test'
        }
    )
    
    assert response.status_code in (200, 302)
    with app.app_context():
        assert ExcelUserStore.get_by_username('test') is not None


def test_login(client, test_user):
    """Test user login."""
    assert client.get('/auth/login').status_code == 200
    
    response = client.post(
        '/auth/login',
        data={'username': 'test', 'password': 'test'}
    )
    
    assert response.status_code == 302  # Redirect after successful login


def test_logout(client, auth):
    """Test user logout."""
    auth.login()
    
    with client:
        auth.logout()
        response = client.get('/')
        assert b'Login' in response.data  # Login button should be visible


def test_about(client):
    """Test the about page."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About' in response.data
