from src.api.controllers.todo_controller import bp as todo_bp
from src.api.controllers.tenant_controller import bp as tenant_bp

def register_routes(app):
    app.register_blueprint(todo_bp)
    app.register_blueprint(tenant_bp) 