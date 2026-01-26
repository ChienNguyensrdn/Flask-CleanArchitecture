from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from marshmallow import Schema, fields, validate


@dataclass
class ConferenceRequest:
    """Request DTO for creating/updating conference"""
    tenant_id: int
    name: str
    short_name: str
    description: Optional[str] = None
    website_url: Optional[str] = None
    venue: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    review_deadline: Optional[datetime] = None
    notification_date: Optional[datetime] = None
    camera_ready_deadline: Optional[datetime] = None
    conference_start_date: Optional[datetime] = None
    conference_end_date: Optional[datetime] = None
    cfp_content: Optional[str] = None
    cfp_is_public: bool = False
    review_mode: str = 'double_blind'
    min_reviews_per_paper: int = 3


@dataclass
class ConferenceResponse:
    """Response DTO for conference"""
    id: int
    tenant_id: int
    name: str
    short_name: str
    description: Optional[str]
    website_url: Optional[str]
    venue: Optional[str]
    submission_deadline: Optional[datetime]
    review_deadline: Optional[datetime]
    notification_date: Optional[datetime]
    camera_ready_deadline: Optional[datetime]
    conference_start_date: Optional[datetime]
    conference_end_date: Optional[datetime]
    cfp_content: Optional[str]
    cfp_is_public: bool
    review_mode: str
    min_reviews_per_paper: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


@dataclass
class CFPPublicResponse:
    """Response DTO for public CFP information"""
    id: int
    name: str
    short_name: str
    description: Optional[str]
    cfp_content: Optional[str]
    submission_deadline: Optional[datetime]
    venue: Optional[str]
    conference_start_date: Optional[datetime]
    conference_end_date: Optional[datetime]


class ConferenceRequestSchema(Schema):
    """Marshmallow schema for conference request validation"""
    tenant_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    short_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    website_url = fields.Url(allow_none=True)
    venue = fields.Str(allow_none=True)
    submission_deadline = fields.DateTime(allow_none=True)
    review_deadline = fields.DateTime(allow_none=True)
    notification_date = fields.DateTime(allow_none=True)
    camera_ready_deadline = fields.DateTime(allow_none=True)
    conference_start_date = fields.DateTime(allow_none=True)
    conference_end_date = fields.DateTime(allow_none=True)
    cfp_content = fields.Str(allow_none=True)
    cfp_is_public = fields.Bool(missing=False)
    review_mode = fields.Str(
        validate=validate.OneOf(['single_blind', 'double_blind', 'open']),
        missing='double_blind'
    )
    min_reviews_per_paper = fields.Int(missing=3)


class ConferenceResponseSchema(Schema):
    """Marshmallow schema for conference response"""
    id = fields.Int()
    tenant_id = fields.Int()
    name = fields.Str()
    short_name = fields.Str()
    description = fields.Str(allow_none=True)
    website_url = fields.Url(allow_none=True)
    venue = fields.Str(allow_none=True)
    submission_deadline = fields.DateTime(allow_none=True)
    review_deadline = fields.DateTime(allow_none=True)
    notification_date = fields.DateTime(allow_none=True)
    camera_ready_deadline = fields.DateTime(allow_none=True)
    conference_start_date = fields.DateTime(allow_none=True)
    conference_end_date = fields.DateTime(allow_none=True)
    cfp_content = fields.Str(allow_none=True)
    cfp_is_public = fields.Bool()
    review_mode = fields.Str()
    min_reviews_per_paper = fields.Int()
    status = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime(allow_none=True)
