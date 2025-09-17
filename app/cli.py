"""
Command Line Interface (CLI) commands for the application.

This module contains CLI commands for database management and other utilities.
"""
import click
import unittest
import sys
from flask import current_app
from flask.cli import with_appcontext
from app.models.user import User, UserStore, ExcelUserStore


def init_app(app):
    """Register CLI commands with the application."""
    # Database-related commands removed
    app.cli.add_command(create_admin_command)
    app.cli.add_command(run_tests_command)


@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user.
    
    Args:
        username: Username for the admin
        email: Email for the admin
        password: Password for the admin
    """
    # Check if user already exists (in-memory)
    if ExcelUserStore.exists_username(username) or UserStore.exists_username(username):
        click.echo(f'User {username} already exists.')
        return
    
    # Create admin user
    admin = User(username=username, email=email, password=password, is_admin=True)
    try:
        ExcelUserStore.add(admin)
    except Exception:
        UserStore.add(admin)
    
    click.echo(f'Created admin user: {username}')


@click.command('run-tests')
@with_appcontext
def run_tests_command():
    """Run the test suite."""
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    
    if result.failures or result.errors:
        sys.exit(1)
