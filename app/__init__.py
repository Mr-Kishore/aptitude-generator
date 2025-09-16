"""
Application Factory

This module initializes the Flask application and its extensions.
"""
import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

# Import models to ensure they are registered with SQLAlchemy
# This import must come after db initialization to avoid circular imports
from app.models.user import User  # noqa

# Import blueprints to register routes
from . import auth, main  # noqa

def create_app(config=None):
    """Create and configure the Flask application.
    
    Args:
        config: Configuration object or dictionary to use
    """
    # Create the Flask application
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    load_dotenv()  # Load environment variables from .env file
    
    # Default configuration
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URL',
            f"sqlite:///{os.path.join(app.instance_path, 'app.db')}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True,
    )
    
    # Override with passed config if provided
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Import and register blueprints
    from . import auth, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    
    # Initialize error handlers
    from .utils import errors
    errors.init_error_handlers(app)
    
    # Initialize template filters
    from .utils import filters
    filters.init_filters(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Import and register CLI commands
    from . import cli
    cli.init_app(app)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    return app
