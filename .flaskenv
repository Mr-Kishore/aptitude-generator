# Flask environment variables
FLASK_APP=wsgi.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database configuration
DATABASE_URL=sqlite:///${PWD}/instance/app.db

# Enable Flask's debug mode
DEBUG=True

# Enable development features
TEMPLATES_AUTO_RELOAD=True
EXPLAIN_TEMPLATE_LOADING=False
