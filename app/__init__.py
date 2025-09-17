"""
Application Factory

This module initializes the Flask application and its extensions.
"""
import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Initialize extensions (no database)
login_manager = LoginManager()
csrf = CSRFProtect()

# Import models to ensure they are registered with SQLAlchemy
# This import must come after db initialization to avoid circular imports
from app.models.user import User, UserStore, ExcelUserStore  # noqa

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
    login_manager.init_app(app)
    csrf.init_app(app)
    
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
    
    # No database initialization required
    
    # Import and register CLI commands
    from . import cli
    cli.init_app(app)
    
    # User loader for Flask-Login (use in-memory store)
    @login_manager.user_loader
    def load_user(user_id):
        # Prefer Excel-backed store if available
        try:
            user = ExcelUserStore.get_by_username(user_id)
            if user:
                return user
        except Exception:
            pass
        return UserStore.get_by_username(user_id)
    
    return app
