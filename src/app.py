"""Main application entry point for running Flask API with Flet UI."""
import os
import threading
import logging

from flask import Flask, jsonify
from api.controllers.auth_controller import auth_bp
from api.controllers.tenant_controller import bp as tenant_bp
from api.controllers.conference_controller import bp as conference_bp
from api.controllers.track_controller import bp as track_bp
from api.controllers.email_template_controller import bp as email_template_bp
from api.controllers.paper_controller import bp as paper_bp
from api.controllers.pc_member_controller import bp as pc_member_bp
from api.controllers.decision_controller import bp as decision_bp
from api.middleware import middleware
from infrastructure.databases import init_db
from config import get_config
import flet as ft

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_name: Optional configuration name override
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(conference_bp)
    app.register_blueprint(track_bp)
    app.register_blueprint(email_template_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(pc_member_bp)
    app.register_blueprint(decision_bp)

    # Initialize database
    try:
        init_db(app)
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

    # Register middleware
    middleware(app)

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "service": "UTH-ConfMS API"})

    # API info endpoint
    @app.route("/", methods=["GET"])
    def api_info():
        return jsonify({
            "name": "UTH Conference Management System API",
            "version": "1.0.0",
            "description": "API for UTH Scientific Conference Paper Management System"
        })

    return app


def run_flask():
    """Run Flask API server"""
    app = create_app()
    app.run(host='0.0.0.0', port=9999, debug=False, use_reloader=False)


def run_flet_ui():
    """Run Flet UI application"""
    from submissions_ui import main
    ft.app(target=main)


# Run the application
if __name__ == '__main__':
    # Start Flask API in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask API running on http://localhost:9999")
    
    # Run Flet UI in main thread (required for GUI)
    logger.info("Starting Flet UI...")
    run_flet_ui()