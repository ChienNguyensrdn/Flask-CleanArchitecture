from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

spec = APISpec(
    title="UTH Conference Management System API",
    version="1.0.0",
    openapi_version="3.0.2",
    info={
        "description": "API for UTH Scientific Conference Paper Management System (UTH-ConfMS). "
                       "Supports the full conference workflow: CFP -> Submission -> Review -> Decision -> Camera-ready.",
        "contact": {"email": "admin@uth.edu.vn"}
    },
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Schemas will be registered as controllers are added
# Example: spec.components.schema("ConferenceRequest", schema=ConferenceRequestSchema)