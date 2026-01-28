from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from marshmallow import Schema, fields, validate, validates, ValidationError


@dataclass
class PCMemberRequest:
    """Request DTO for PC member"""
    conference_id: int
    user_id: int
    track_id: Optional[int] = None
    role: str = 'reviewer'
    expertise_keywords: Optional[str] = None
    max_papers: int = 10
    can_access_author_info: bool = False


@dataclass
class PCMemberResponse:
    """Response DTO for PC member"""
    id: int
    conference_id: int
    user_id: int
    track_id: Optional[int]
    role: str
    invitation_status: str
    invitation_sent_at: Optional[datetime]
    invitation_responded_at: Optional[datetime]
    expertise_keywords: Optional[str]
    max_papers: int
    assigned_count: int
    is_active: bool
    can_access_author_info: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class PCInvitationRequest:
    """Request DTO for PC invitation"""
    conference_id: int
    user_id: int
    role: str = 'reviewer'
    track_id: Optional[int] = None


@dataclass
class COIRequest:
    """Request DTO for conflict of interest"""
    pc_member_id: int
    paper_id: Optional[int] = None
    author_user_id: Optional[int] = None
    conflict_type: str = ''
    institution: Optional[str] = None
    description: Optional[str] = None
    conflict_start_date: Optional[datetime] = None
    conflict_end_date: Optional[datetime] = None


@dataclass
class COIResponse:
    """Response DTO for COI"""
    id: int
    pc_member_id: int
    paper_id: Optional[int]
    author_user_id: Optional[int]
    conflict_type: str
    institution: Optional[str]
    description: Optional[str]
    declared_by: str
    is_active: bool
    verified_at: Optional[datetime]
    created_at: datetime


@dataclass
class BidRequest:
    """Request DTO for bidding"""
    paper_id: int
    pc_member_id: int
    bid_value: int  # -2: conflict, -1: no, 0: maybe, 1: yes, 2: strong yes


@dataclass
class BidResponse:
    """Response DTO for bid"""
    id: int
    paper_id: int
    pc_member_id: int
    bid_value: int
    bid_timestamp: datetime
    status: str


class PCMemberRequestSchema(Schema):
    """Marshmallow schema for PC member request"""
    conference_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    track_id = fields.Int(allow_none=True)
    role = fields.Str(
        validate=validate.OneOf(['reviewer', 'senior_pc', 'track_chair', 'program_chair', 'general_chair']),
        missing='reviewer'
    )
    expertise_keywords = fields.Str(allow_none=True)
    max_papers = fields.Int(missing=10, validate=validate.Range(min=1, max=100))
    can_access_author_info = fields.Bool(missing=False)


class PCMemberResponseSchema(Schema):
    """Marshmallow schema for PC member response"""
    id = fields.Int()
    conference_id = fields.Int()
    user_id = fields.Int()
    track_id = fields.Int(allow_none=True)
    role = fields.Str()
    invitation_status = fields.Str()
    invitation_sent_at = fields.DateTime(allow_none=True)
    invitation_responded_at = fields.DateTime(allow_none=True)
    expertise_keywords = fields.Str(allow_none=True)
    max_papers = fields.Int()
    assigned_count = fields.Int()
    is_active = fields.Bool()
    can_access_author_info = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class PCInvitationRequestSchema(Schema):
    """Marshmallow schema for PC invitation"""
    conference_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    role = fields.Str(
        validate=validate.OneOf(['reviewer', 'senior_pc', 'track_chair']),
        missing='reviewer'
    )
    track_id = fields.Int(allow_none=True)


class COIRequestSchema(Schema):
    """Marshmallow schema for COI"""
    pc_member_id = fields.Int(required=True)
    paper_id = fields.Int(allow_none=True)
    author_user_id = fields.Int(allow_none=True)
    conflict_type = fields.Str(
        required=True,
        validate=validate.OneOf([
            'co_author', 'same_institution', 'advisor_advisee', 
            'collaborator', 'personal', 'financial', 'other'
        ])
    )
    institution = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    conflict_start_date = fields.DateTime(allow_none=True)
    conflict_end_date = fields.DateTime(allow_none=True)
    
    @validates('paper_id')
    def validate_paper_or_author(self, value):
        # At least one of paper_id or author_user_id must be provided
        pass


class COIResponseSchema(Schema):
    """Marshmallow schema for COI response"""
    id = fields.Int()
    pc_member_id = fields.Int()
    paper_id = fields.Int(allow_none=True)
    author_user_id = fields.Int(allow_none=True)
    conflict_type = fields.Str()
    institution = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    declared_by = fields.Str()
    is_active = fields.Bool()
    verified_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()


class BidRequestSchema(Schema):
    """Marshmallow schema for bid request"""
    paper_id = fields.Int(required=True)
    pc_member_id = fields.Int(required=True)
    bid_value = fields.Int(
        required=True,
        validate=validate.OneOf([-2, -1, 0, 1, 2])
    )


class BidResponseSchema(Schema):
    """Marshmallow schema for bid response"""
    id = fields.Int()
    paper_id = fields.Int()
    pc_member_id = fields.Int()
    bid_value = fields.Int()
    bid_timestamp = fields.DateTime()
    status = fields.Str()
