from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from marshmallow import Schema, fields, validate


@dataclass
class TrackRequest:
    """Request DTO for creating/updating track"""
    conference_id: int
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    review_deadline: Optional[datetime] = None
    track_chair_id: Optional[int] = None
    is_active: bool = True
    display_order: int = 0


@dataclass
class TrackResponse:
    """Response DTO for track"""
    id: int
    conference_id: int
    name: str
    short_name: Optional[str]
    description: Optional[str]
    keywords: Optional[str]
    submission_deadline: Optional[datetime]
    review_deadline: Optional[datetime]
    track_chair_id: Optional[int]
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime


class TrackRequestSchema(Schema):
    """Marshmallow schema for track request validation"""
    conference_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    short_name = fields.Str(allow_none=True, validate=validate.Length(max=50))
    description = fields.Str(allow_none=True)
    keywords = fields.Str(allow_none=True)
    submission_deadline = fields.DateTime(allow_none=True)
    review_deadline = fields.DateTime(allow_none=True)
    track_chair_id = fields.Int(allow_none=True)
    is_active = fields.Bool(missing=True)
    display_order = fields.Int(missing=0)


class TrackResponseSchema(Schema):
    """Marshmallow schema for track response"""
    id = fields.Int()
    conference_id = fields.Int()
    name = fields.Str()
    short_name = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    keywords = fields.Str(allow_none=True)
    submission_deadline = fields.DateTime(allow_none=True)
    review_deadline = fields.DateTime(allow_none=True)
    track_chair_id = fields.Int(allow_none=True)
    is_active = fields.Bool()
    display_order = fields.Int()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
