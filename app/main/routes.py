"""
Main application routes.

This module contains the main application routes for the Aptitude Generator.
"""
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from . import bp


@bp.route('/')
def index():
    """Render the home page or redirect to dashboard if logged in."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Render the user dashboard."""
    return render_template('dashboard.html', user=current_user)
