"""
Main Blueprint

This module contains the main application routes.
"""
from flask import Blueprint

# Create the blueprint
bp = Blueprint('main', __name__)

# Import the routes module to register the routes with the blueprint
from . import routes  # noqa
