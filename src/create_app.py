"""
Application factory module.
This is the main create_app function that should be used to create the Flask application.
"""
from flask import Flask, jsonify
from .config import get_config, Config
from .api.middleware import middleware
from .infrastructure.databases import init_db
from .app_logging import setup_logging
import logging

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_name: Configuration name ('development', 'testing', 'production')
                    If None, uses FLASK_ENV environment variable.
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name:
        import os
        os.environ['FLASK_ENV'] = config_name
    
    config_class = get_config()
    app.config.from_object(config_class)

    # Setup logging
    setup_logging(app)
    
    # Initialize database
    try:
        init_db(app)
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    
    # Setup middleware
    middleware(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register health check and info endpoints
    _register_core_routes(app)
    
    logger.info("Application created successfully")
    return app


def _register_blueprints(app):
    """Register all application blueprints"""
    from .api.controllers.auth_controller import auth_bp
    from .api.controllers.tenant_controller import bp as tenant_bp
    from .api.controllers.conference_controller import bp as conference_bp
    from .api.controllers.track_controller import bp as track_bp
    from .api.controllers.email_template_controller import bp as email_template_bp
    from .api.controllers.paper_controller import bp as paper_bp
    from .api.controllers.pc_member_controller import bp as pc_member_bp
    from .api.controllers.decision_controller import bp as decision_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(conference_bp)
    app.register_blueprint(track_bp)
    app.register_blueprint(email_template_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(pc_member_bp)
    app.register_blueprint(decision_bp)


def _register_core_routes(app):
    """Register core application routes"""
    
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "service": "UTH-ConfMS API"})

    @app.route("/", methods=["GET"])
    def api_info():
        return jsonify({
            "name": "UTH Conference Management System API",
            "version": "1.0.0",
            "description": "API for UTH Scientific Conference Paper Management System"
        })