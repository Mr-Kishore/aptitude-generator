"""
Authentication Blueprint

This module contains the authentication routes and functionality.
"""
from flask import Blueprint

# Create the blueprint
bp = Blueprint('auth', __name__)

# Import the routes module to register the routes with the blueprint
from . import routes  # noqa
