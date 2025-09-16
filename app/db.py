"""
Database configuration and utilities.

This module configures SQLAlchemy and provides database-related utilities.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create SQLAlchemy instance
db = SQLAlchemy()

# Create a custom base model with common functionality
class BaseModel(db.Model):
    """Base model with common functionality."""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def save(self):
        """Save the current instance to the database."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the current instance from the database."""
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        """Update the current instance with the provided attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

# Set up SQLAlchemy event listeners for connection pooling
@event.listens_for(db.engine, 'engine_connect')
def receive_engine_connect(dbapi_connection, connection_record):
    """Handle database connection events."""
    # Enable SQLite foreign key support
    if db.engine.name == 'sqlite':
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

def init_app(app):
    """Initialize the database with the Flask application."""
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Register teardown function to close database connections
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove database sessions at the end of the request or app context."""
        db.session.remove()
