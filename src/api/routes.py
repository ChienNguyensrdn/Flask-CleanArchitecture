from src.api.controllers.todo_controller import bp as todo_bp
from src.api.controllers.tenant_controller import bp as tenant_bp
from src.api.controllers.conference_controller import bp as conference_bp
from src.api.controllers.track_controller import bp as track_bp
from src.api.controllers.email_template_controller import bp as email_template_bp
from src.api.controllers.paper_controller import bp as paper_bp

def register_routes(app):
    app.register_blueprint(todo_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(conference_bp)
    app.register_blueprint(track_bp)
    app.register_blueprint(email_template_bp)
    app.register_blueprint(paper_bp) 