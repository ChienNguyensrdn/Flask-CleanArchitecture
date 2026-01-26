from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from marshmallow import Schema, fields, validate, validates, ValidationError


@dataclass
class PaperAuthorRequest:
    """Request DTO for paper author"""
    user_id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    affiliation: Optional[str] = None
    country: Optional[str] = None
    orcid: Optional[str] = None
    author_order: int = 1
    is_corresponding: bool = False
    is_presenter: bool = False


@dataclass
class PaperAuthorResponse:
    """Response DTO for paper author"""
    id: int
    paper_id: int
    user_id: Optional[int]
    first_name: str
    last_name: str
    email: str
    affiliation: Optional[str]
    country: Optional[str]
    orcid: Optional[str]
    author_order: int
    is_corresponding: bool
    is_presenter: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class PaperSubmissionRequest:
    """Request DTO for paper submission"""
    conference_id: int
    track_id: Optional[int] = None
    title: str = ""
    abstract: str = ""
    keywords: Optional[str] = None
    authors: List[PaperAuthorRequest] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None


@dataclass
class PaperUpdateRequest:
    """Request DTO for paper update"""
    title: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    track_id: Optional[int] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None


@dataclass
class PaperResponse:
    """Response DTO for paper"""
    id: int
    conference_id: int
    track_id: Optional[int]
    submitter_id: int
    paper_number: Optional[str]
    title: str
    abstract: str
    keywords: Optional[str]
    pdf_path: Optional[str]
    supplementary_path: Optional[str]
    page_count: Optional[int]
    word_count: Optional[int]
    status: str
    is_withdrawn: bool
    requires_revision: bool
    submitted_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    authors: Optional[List[PaperAuthorResponse]] = None


class PaperAuthorRequestSchema(Schema):
    """Marshmallow schema for paper author request"""
    user_id = fields.Int(allow_none=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True)
    affiliation = fields.Str(allow_none=True, validate=validate.Length(max=500))
    country = fields.Str(allow_none=True, validate=validate.Length(max=100))
    orcid = fields.Str(allow_none=True, validate=validate.Length(max=50))
    author_order = fields.Int(missing=1)
    is_corresponding = fields.Bool(missing=False)
    is_presenter = fields.Bool(missing=False)


class PaperAuthorResponseSchema(Schema):
    """Marshmallow schema for paper author response"""
    id = fields.Int()
    paper_id = fields.Int()
    user_id = fields.Int(allow_none=True)
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    affiliation = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    orcid = fields.Str(allow_none=True)
    author_order = fields.Int()
    is_corresponding = fields.Bool()
    is_presenter = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class PaperSubmissionRequestSchema(Schema):
    """Marshmallow schema for paper submission"""
    conference_id = fields.Int(required=True)
    track_id = fields.Int(allow_none=True)
    title = fields.Str(required=True, validate=validate.Length(min=5, max=1000))
    abstract = fields.Str(required=True, validate=validate.Length(min=50, max=5000))
    keywords = fields.Str(allow_none=True)
    authors = fields.List(fields.Nested(PaperAuthorRequestSchema), required=True)
    page_count = fields.Int(allow_none=True)
    word_count = fields.Int(allow_none=True)
    
    @validates('authors')
    def validate_authors(self, value):
        if not value or len(value) == 0:
            raise ValidationError("At least one author is required")
        
        # Check for corresponding author
        has_corresponding = any(author.get('is_corresponding', False) for author in value)
        if not has_corresponding:
            raise ValidationError("At least one author must be marked as corresponding")


class PaperUpdateRequestSchema(Schema):
    """Marshmallow schema for paper update"""
    title = fields.Str(allow_none=True, validate=validate.Length(min=5, max=1000))
    abstract = fields.Str(allow_none=True, validate=validate.Length(min=50, max=5000))
    keywords = fields.Str(allow_none=True)
    track_id = fields.Int(allow_none=True)
    page_count = fields.Int(allow_none=True)
    word_count = fields.Int(allow_none=True)


class PaperResponseSchema(Schema):
    """Marshmallow schema for paper response"""
    id = fields.Int()
    conference_id = fields.Int()
    track_id = fields.Int(allow_none=True)
    submitter_id = fields.Int()
    paper_number = fields.Str(allow_none=True)
    title = fields.Str()
    abstract = fields.Str()
    keywords = fields.Str(allow_none=True)
    pdf_path = fields.Str(allow_none=True)
    supplementary_path = fields.Str(allow_none=True)
    page_count = fields.Int(allow_none=True)
    word_count = fields.Int(allow_none=True)
    status = fields.Str()
    is_withdrawn = fields.Bool()
    requires_revision = fields.Bool()
    submitted_at = fields.DateTime(allow_none=True)
    withdrawn_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    authors = fields.List(fields.Nested(PaperAuthorResponseSchema), allow_none=True)
