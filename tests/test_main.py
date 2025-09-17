"""
Tests for main application routes.

This module contains tests for the main application routes.
"""
import pytest


def test_index(client):
    """Test that the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Aptitude Generator' in response.data


def test_about(client):
    """Test that the about page loads successfully."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About' in response.data


def test_dashboard_requires_login(client):
    """Test that the dashboard requires login."""
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in to access this page' in response.data


def test_dashboard_after_login(client, auth):
    """Test that the dashboard is accessible after login."""
    auth.login()
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Welcome' in response.data
    assert b'testuser' in response.data


def test_404_error(client):
    """Test that a 404 error is handled correctly."""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data
