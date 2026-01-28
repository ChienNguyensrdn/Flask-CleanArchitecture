# Configuration settings for the Flask application

import os
from datetime import timedelta


class Config:
    """Base configuration."""
    # SECURITY WARNING: Set these via environment variables in production!
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        import warnings
        warnings.warn(
            "SECRET_KEY not set! Using insecure default. "
            "Set SECRET_KEY environment variable in production.",
            RuntimeWarning
        )
        SECRET_KEY = 'dev-only-insecure-key-change-in-production'
    
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    TESTING = os.environ.get('TESTING', 'False').lower() in ['true', '1']
    
    # Database configuration - MUST be set via environment variable
    DATABASE_URI = os.environ.get('DATABASE_URI')
    if not DATABASE_URI:
        raise ValueError(
            "DATABASE_URI environment variable is required. "
            "Example: mssql+pymssql://user:password@host:port/database"
        )
    
    CORS_HEADERS = 'Content-Type'
    
    # JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_ALGORITHM = 'HS256'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
    # Allow default DATABASE_URI for development only
    DATABASE_URI = os.environ.get('DATABASE_URI') or os.environ.get('DEV_DATABASE_URI')
    if not DATABASE_URI:
        raise ValueError(
            "DATABASE_URI or DEV_DATABASE_URI environment variable is required. "
            "Example: mssql+pymssql://user:password@host:port/database"
        )


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    
    DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or os.environ.get('DATABASE_URI')
    if not DATABASE_URI:
        raise ValueError("TEST_DATABASE_URI or DATABASE_URI environment variable is required.")


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Strict validation for production
    @classmethod
    def init_app(cls, app):
        # Ensure SECRET_KEY is properly set
        if app.config['SECRET_KEY'] == 'dev-only-insecure-key-change-in-production':
            raise ValueError("SECRET_KEY must be set in production!")
        
        # Ensure DATABASE_URI is set
        if not app.config.get('DATABASE_URI'):
            raise ValueError("DATABASE_URI must be set in production!")


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])