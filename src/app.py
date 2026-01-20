from flask import Flask, jsonify
from api.controllers.auth_controller import auth_bp
from api.controllers.tenant_controller import bp as tenant_bp
from api.middleware import middleware
from api.responses import success_response
from infrastructure.databases import init_db
from config import Config
import threading
import flet as ft


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tenant_bp)

    # Initialize database
    try:
        init_db(app)
    except Exception as e:
        print(f"Error initializing database: {e}")
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
    print("Flask API running on http://localhost:9999")
    
    # Run Flet UI in main thread (required for GUI)
    print("Starting Flet UI...")
    run_flet_ui()