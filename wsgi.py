"""
WSGI config for Aptitude Generator.

This module contains the WSGI application used by the production server.
"""
import os
from app import create_app
from config import config

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
load_dotenv()

# Create the Flask application
app = create_app(config[os.getenv('FLASK_ENV', 'development')])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() in ['true', '1', 't']
    
    print(f"Starting server in {os.getenv('FLASK_ENV', 'development')} mode")
    print(f" * Debug mode: {'on' if debug else 'off'}")
    print(f" * Running on http://127.0.0.1:{port}/ (Press CTRL+C to quit)")
    
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
