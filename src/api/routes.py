"""Route registration module - consolidates all blueprint registrations."""
from api.controllers.tenant_controller import bp as tenant_bp
from api.controllers.conference_controller import bp as conference_bp
from api.controllers.track_controller import bp as track_bp
from api.controllers.email_template_controller import bp as email_template_bp
from api.controllers.paper_controller import bp as paper_bp
from api.controllers.pc_member_controller import bp as pc_member_bp
from api.controllers.decision_controller import bp as decision_bp
from api.controllers.auth_controller import auth_bp


def register_routes(app):
    """Register all application blueprints with the Flask app."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(conference_bp)
    app.register_blueprint(track_bp)
    app.register_blueprint(email_template_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(pc_member_bp)
    app.register_blueprint(decision_bp) 