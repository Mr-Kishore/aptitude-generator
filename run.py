#!/usr/bin/env python
"""
Run the Aptitude Generator application.

This script runs the Flask development server.
"""
import os
from app import create_app
from config import config

# Determine the environment to use (default to development)
env = os.environ.get('FLASK_ENV', 'development')

# Create the application
app = create_app(config[env])

if __name__ == '__main__':
    # Get the port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment variable or use False
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
    
    print(f"Starting {app.config['APP_NAME']} in {env} mode")
    print(f" * Debug mode: {'on' if debug else 'off'}")
    print(f" * Running on http://127.0.0.1:{port}/ (Press CTRL+C to quit)")
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=debug)
