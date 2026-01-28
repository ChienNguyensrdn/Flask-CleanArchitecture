# Middleware functions for processing requests and responses

from flask import request, jsonify, g, current_app
from functools import wraps
import jwt
import logging

logger = logging.getLogger(__name__)


def log_request_info():
    """Log incoming request information"""
    logger.debug('Headers: %s', dict(request.headers))
    logger.debug('Method: %s, Path: %s', request.method, request.path)
    if request.is_json:
        # Don't log sensitive data like passwords
        data = request.get_json(silent=True) or {}
        safe_data = {k: v for k, v in data.items() if 'password' not in k.lower()}
        logger.debug('Body: %s', safe_data)


def handle_options_request():
    return jsonify({'message': 'CORS preflight response'}), 200


def error_handling_middleware(error):
    """Handle errors without exposing sensitive information"""
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    
    # Don't expose internal error details in production
    if current_app.debug:
        response = jsonify({'error': str(error), 'type': type(error).__name__})
    else:
        response = jsonify({'error': 'An internal error occurred'})
    
    response.status_code = getattr(error, 'status_code', 500)
    return response


def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response


def get_current_user_from_token():
    """Extract user information from JWT token if present"""
    g.current_user_id = None
    g.current_user_name = None
    
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            g.current_user_id = payload.get('user_id')
            g.current_user_name = payload.get('user_name')
        except jwt.ExpiredSignatureError:
            logger.debug("Token expired")
        except jwt.InvalidTokenError:
            logger.debug("Invalid token")


def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.get('current_user_id'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Decorator to require specific roles for a route"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not g.get('current_user_id'):
                return jsonify({'error': 'Authentication required'}), 401
            # TODO: Implement role checking from database
            # user_role = get_user_role(g.current_user_id)
            # if user_role not in roles:
            #     return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# Public routes that don't require authentication
PUBLIC_ROUTES = [
    '/health',
    '/',
    '/auth/login',
    '/auth/register',
    '/conferences/public-cfp',
]


def is_public_route(path):
    """Check if the route is public"""
    for route in PUBLIC_ROUTES:
        if path == route or path.startswith(route + '/'):
            return True
    return False


def middleware(app):
    """Register middleware with the Flask application"""
    
    @app.before_request
    def before_request():
        log_request_info()
        get_current_user_from_token()

    @app.after_request
    def after_request(response):
        return add_security_headers(response)

    @app.errorhandler(Exception)
    def handle_exception(error):
        return error_handling_middleware(error)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    @app.route('/options', methods=['OPTIONS'])
    def options_route():
        return handle_options_request()


def setup_middleware(app):
    """Alias for middleware function for compatibility"""
    middleware(app)