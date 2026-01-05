from marshmallow import Schema, fields

class RigisterUserRequestSchema(Schema):
    user_name = fields.Str(required=True)
    password = fields.Str(required=True)
    password_confirm = fields.Str(required=True)
    # email = fields.Email(required=True)
class RigisterUserResponseSchema(Schema):
    user_name = fields.Str(required=True)
    password = fields.Str(required=True)
    
    
class LoginUserRequestSchema(Schema):
    user_name = fields.Str(required=True)
    password = fields.Str(required=True)
    
class LoginUserResponseSchema(Schema):
    user_name = fields.Str(required=True)
    token = fields.Str(required=True)