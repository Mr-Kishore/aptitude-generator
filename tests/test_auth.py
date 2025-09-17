"""
Tests for authentication routes.

This module contains tests for user authentication functionality.
"""
import pytest
from app.models.user import User, ExcelUserStore


def test_register(client, app):
    ""Test that a user can register."""
    # Test GET request to register page
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create an Account' in response.data

    # Test successful registration
    response = client.post(
        '/auth/register',
        data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Registration successful' in response.data

    # Verify user was added to the Excel store
    with app.app_context():
        user = ExcelUserStore.get_by_username('newuser')
        assert user is not None
        assert user.email == 'newuser@example.com'


def test_register_existing_username(client):
    ""Test that a username must be unique."""
    # First registration (should succeed)
    client.post(
        '/auth/register',
        data={
            'username': 'existinguser',
            'email': 'user1@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
    )
    
    # Second registration with same username (should fail)
    response = client.post(
        '/auth/register',
        data={
            'username': 'existinguser',
            'email': 'user2@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
    )
    assert b'Username is already taken' in response.data


def test_login(client, auth):
    ""Test that a user can log in."""
    # Test GET request to login page
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

    # Test successful login
    response = auth.login()
    assert response.status_code == 200
    assert b'You have been logged in' in response.data

    # Test login with invalid credentials
    response = auth.login('nonexistent', 'wrongpassword')
    assert b'Invalid username or password' in response.data


def test_logout(client, auth):
    ""Test that a user can log out."""
    # Log in first
    auth.login()
    
    # Test logout
    response = auth.logout()
    assert b'You have been logged out' in response.data
    
    # Verify user is redirected to login page
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in to access this page' in response.data
