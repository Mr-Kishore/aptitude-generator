"""
Error handlers for the application.

This module contains error handlers for common HTTP errors.
"""
from flask import render_template, request, jsonify
from werkzeug.http import HTTP_STATUS_CODES


def wants_json_response():
    """Check if the client wants a JSON response."""
    return request.accept_mimetypes.best == 'application/json'


def error_response(status_code, message=None):
    """Create a JSON response for an error."""
    payload = {
        'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error'),
        'status': 'error',
        'code': status_code
    }
    if message:
        payload['message'] = message
    
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    """Create a 400 Bad Request response."""
    return error_response(400, message)


def unauthorized(message='Authentication required'):
    """Create a 401 Unauthorized response."""
    return error_response(401, message)


def forbidden(message='Insufficient permissions'):
    """Create a 403 Forbidden response."""
    return error_response(403, message)


def not_found(message='Resource not found'):
    """Create a 404 Not Found response."""
    return error_response(404, message)


def method_not_allowed(message='Method not allowed'):
    """Create a 405 Method Not Allowed response."""
    return error_response(405, message)


def internal_error(message='An unexpected error occurred'):
    """Create a 500 Internal Server Error response."""
    return error_response(500, message)


def page_not_found(e):
    """Handle 404 errors."""
    if wants_json_response():
        return not_found('The requested URL was not found on the server.')
    return render_template('errors/404.html'), 404


def forbidden_error(e):
    """Handle 403 errors."""
    if wants_json_response():
        return forbidden('You do not have permission to access this resource.')
    return render_template('errors/403.html'), 403


def internal_error_handler(e):
    """Handle 500 errors."""
    if wants_json_response():
        return internal_error('An internal server error occurred.')
    return render_template('errors/500.html'), 500


def init_error_handlers(app):
    """Register error handlers with the Flask application."""
    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden_error)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(500, internal_error_handler)
    
    # No database-specific error handlers required since the app does not use a DB backend
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        return internal_error('An unexpected error occurred.')
