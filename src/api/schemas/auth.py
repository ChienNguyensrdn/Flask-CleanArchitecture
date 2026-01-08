from marshmallow import Schema, fields

class RigisterUserRequestSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    passwordconfirm = fields.Str(required=True)
    email = fields.Email(required=True)
class RigisterUserResponseSchema(Schema):
    username = fields.Str(required=True)
    # password = fields.Str(required=True)
    email = fields.Email(required=True)
    
    
class LoginUserRequestSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    
class LoginUserResponseSchema(Schema):
    username = fields.Str(required=True)
    token = fields.Str(required=True)