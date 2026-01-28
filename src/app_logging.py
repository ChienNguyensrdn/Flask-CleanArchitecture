"""Logging configuration for the Flask application."""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(app=None):
    """
    Configure application logging with proper formatting and handlers.
    
    Args:
        app: Optional Flask application instance for app-specific configuration
    """
    # Determine log level from environment or use INFO as default
    log_level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = os.environ.get('LOG_DIR', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)
    
    # Error file handler - separate file for errors only
    error_log_file = os.path.join(log_dir, 'error.log')
    error_file_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(error_file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Configure Flask app logger if provided
    if app:
        app.logger.setLevel(log_level)
        app.logger.info(f"Logging configured at {log_level_name} level")
    
    logging.info(f"Logging initialized - Level: {log_level_name}, Log directory: {log_dir}")


class RequestLogger:
    """Utility class for logging request/response information."""
    
    @staticmethod
    def log_request(request, logger=None):
        """Log incoming request details (excluding sensitive data)."""
        if logger is None:
            logger = logging.getLogger(__name__)
        
        # Build safe headers (exclude Authorization details)
        safe_headers = {
            k: v for k, v in request.headers
            if k.lower() not in ['authorization', 'cookie']
        }
        
        logger.info(f"Request: {request.method} {request.path}")
        logger.debug(f"Headers: {safe_headers}")
        logger.debug(f"Query params: {dict(request.args)}")
    
    @staticmethod
    def log_response(response, duration_ms, logger=None):
        """Log response details."""
        if logger is None:
            logger = logging.getLogger(__name__)
        
        logger.info(f"Response: {response.status_code} ({duration_ms:.2f}ms)") 