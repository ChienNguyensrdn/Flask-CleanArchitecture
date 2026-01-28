"""Error handling logic for the Flask application."""
from flask import jsonify, current_app
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for application errors."""
    status_code = 500
    error_code = 'INTERNAL_ERROR'

    def __init__(self, message, status_code=None, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.details = details

    def to_dict(self):
        rv = {
            'error': self.error_code,
            'message': self.message
        }
        if self.details:
            rv['details'] = self.details
        return rv


class BadRequestError(AppError):
    """400 Bad Request"""
    status_code = 400
    error_code = 'BAD_REQUEST'


class UnauthorizedError(AppError):
    """401 Unauthorized"""
    status_code = 401
    error_code = 'UNAUTHORIZED'


class ForbiddenError(AppError):
    """403 Forbidden"""
    status_code = 403
    error_code = 'FORBIDDEN'


class NotFoundError(AppError):
    """404 Not Found"""
    status_code = 404
    error_code = 'NOT_FOUND'


class ConflictError(AppError):
    """409 Conflict"""
    status_code = 409
    error_code = 'CONFLICT'


class ValidationError(AppError):
    """422 Validation Error"""
    status_code = 422
    error_code = 'VALIDATION_ERROR'


def handle_app_error(error):
    """Handle application-specific errors."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logger.warning(f"AppError: {error.error_code} - {error.message}")
    return response


def handle_generic_error(error):
    """Handle unexpected errors."""
    logger.error(f"Unhandled exception: {type(error).__name__}: {str(error)}", exc_info=True)
    
    # Don't expose internal error details in production
    if current_app.debug:
        message = str(error)
    else:
        message = 'An unexpected error occurred'
    
    response = jsonify({
        'error': 'INTERNAL_ERROR',
        'message': message
    })
    response.status_code = 500
    return response


def register_error_handlers(app):
    """Register error handlers with the Flask application."""
    
    @app.errorhandler(AppError)
    def handle_app_exception(error):
        return handle_app_error(error)
    
    @app.errorhandler(BadRequestError)
    def handle_bad_request(error):
        return handle_app_error(error)
    
    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(error):
        return handle_app_error(error)
    
    @app.errorhandler(ForbiddenError)
    def handle_forbidden(error):
        return handle_app_error(error)
    
    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        return handle_app_error(error)
    
    @app.errorhandler(ConflictError)
    def handle_conflict(error):
        return handle_app_error(error)
    
    @app.errorhandler(ValidationError)
    def handle_validation(error):
        return handle_app_error(error)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        return handle_generic_error(error)


# Backward compatibility alias
CustomError = AppError
handle_error = handle_generic_error