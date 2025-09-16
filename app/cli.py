"""
Command Line Interface (CLI) commands for the application.

This module contains CLI commands for database management and other utilities.
"""
import click
import unittest
import sys
from flask import current_app
from flask.cli import with_appcontext
from app import db


def init_app(app):
    """Register CLI commands with the application."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(run_tests_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()
    click.echo('Initialized the database.')


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
    from app.models.user import User
    
    # Check if user already exists
    if User.query.filter_by(username=username).first() is not None:
        click.echo(f'User {username} already exists.')
        return
    
    # Create admin user
    admin = User(
        username=username,
        email=email,
        password=password,
        is_admin=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f'Created admin user: {username}')


@click.command('run-tests')
@with_appcontext
def run_tests_command():
    """Run the test suite."""
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    
    if result.failures or result.errors:
        sys.exit(1)
