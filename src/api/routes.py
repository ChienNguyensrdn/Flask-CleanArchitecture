from src.api.controllers.todo_controller import bp as todo_bp
from src.api.controllers.tenant_controller import bp as tenant_bp
from src.api.controllers.conference_controller import bp as conference_bp
from src.api.controllers.track_controller import bp as track_bp
from src.api.controllers.email_template_controller import bp as email_template_bp
from src.api.controllers.paper_controller import bp as paper_bp
from src.api.controllers.pc_member_controller import bp as pc_member_bp
from src.api.controllers.decision_controller import bp as decision_bp

def register_routes(app):
    app.register_blueprint(todo_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(conference_bp)
    app.register_blueprint(track_bp)
    app.register_blueprint(email_template_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(pc_member_bp)
    app.register_blueprint(decision_bp) 