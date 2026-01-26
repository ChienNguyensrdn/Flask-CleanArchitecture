from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from marshmallow import Schema, fields, validate


@dataclass
class EmailTemplateRequest:
    """Request DTO for creating/updating email template"""
    conference_id: Optional[int]
    template_type: str
    name: str
    description: Optional[str] = None
    subject: str = ""
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    language: str = 'en'
    is_active: bool = True
    is_default: bool = False


@dataclass
class EmailTemplateResponse:
    """Response DTO for email template"""
    id: int
    conference_id: Optional[int]
    template_type: str
    name: str
    description: Optional[str]
    subject: str
    body_html: Optional[str]
    body_text: Optional[str]
    language: str
    is_active: bool
    is_default: bool
    ai_generated: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime


@dataclass
class EmailLogRequest:
    """Request DTO for sending email"""
    conference_id: Optional[int]
    template_id: Optional[int]
    recipient_email: str
    recipient_name: Optional[str] = None
    recipient_user_id: Optional[int] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    paper_id: Optional[int] = None


@dataclass
class EmailLogResponse:
    """Response DTO for email log"""
    id: int
    conference_id: Optional[int]
    template_id: Optional[int]
    recipient_email: str
    recipient_name: Optional[str]
    recipient_user_id: Optional[int]
    subject: str
    body: Optional[str]
    paper_id: Optional[int]
    status: str
    sent_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime


class EmailTemplateRequestSchema(Schema):
    """Marshmallow schema for email template request"""
    conference_id = fields.Int(allow_none=True)
    template_type = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    subject = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    body_html = fields.Str(allow_none=True)
    body_text = fields.Str(allow_none=True)
    language = fields.Str(missing='en', validate=validate.OneOf(['en', 'vi', 'es', 'fr']))
    is_active = fields.Bool(missing=True)
    is_default = fields.Bool(missing=False)


class EmailTemplateResponseSchema(Schema):
    """Marshmallow schema for email template response"""
    id = fields.Int()
    conference_id = fields.Int(allow_none=True)
    template_type = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    subject = fields.Str()
    body_html = fields.Str(allow_none=True)
    body_text = fields.Str(allow_none=True)
    language = fields.Str()
    is_active = fields.Bool()
    is_default = fields.Bool()
    ai_generated = fields.Bool()
    created_by = fields.Int(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class EmailLogRequestSchema(Schema):
    """Marshmallow schema for email log request"""
    conference_id = fields.Int(allow_none=True)
    template_id = fields.Int(allow_none=True)
    recipient_email = fields.Email(required=True)
    recipient_name = fields.Str(allow_none=True)
    recipient_user_id = fields.Int(allow_none=True)
    subject = fields.Str(allow_none=True)
    body = fields.Str(allow_none=True)
    paper_id = fields.Int(allow_none=True)


class EmailLogResponseSchema(Schema):
    """Marshmallow schema for email log response"""
    id = fields.Int()
    conference_id = fields.Int(allow_none=True)
    template_id = fields.Int(allow_none=True)
    recipient_email = fields.Email()
    recipient_name = fields.Str(allow_none=True)
    recipient_user_id = fields.Int(allow_none=True)
    subject = fields.Str()
    body = fields.Str(allow_none=True)
    paper_id = fields.Int(allow_none=True)
    status = fields.Str()
    sent_at = fields.DateTime(allow_none=True)
    error_message = fields.Str(allow_none=True)
    created_at = fields.DateTime()
