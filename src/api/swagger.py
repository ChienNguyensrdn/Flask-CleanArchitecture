from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from api.schemas.auth import LoginUserRequestSchema, LoginUserResponseSchema, RigisterUserRequestSchema, RigisterUserResponseSchema
from api.schemas.todo import TodoRequestSchema, TodoResponseSchema

spec = APISpec(
    title="Todo API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Đăng ký schema để tự động sinh model
spec.components.schema("TodoRequest", schema=TodoRequestSchema)
spec.components.schema("TodoResponse", schema=TodoResponseSchema)
spec.components.schema("LoginUserRequest", schema= LoginUserRequestSchema)
spec.components.schema("LoginUserResponse", schema= LoginUserResponseSchema)
spec.components.schema("RigisterUserRequest", schema= RigisterUserRequestSchema)
spec.components.schema("RigisterUserResponse", schema= RigisterUserResponseSchema)