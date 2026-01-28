"""Paper schemas for API requests/responses."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.paper import PaperStatus


class AuthorInfo(BaseModel):
    """Author information for a paper."""
    user_id: Optional[int] = None  # Null for external authors
    email: str
    first_name: str
    last_name: str
    affiliation: Optional[str] = None
    country: Optional[str] = None
    order: int = 1
    is_corresponding: bool = False


class PaperBase(BaseModel):
    """Base paper schema."""
    title: str = Field(..., min_length=1, max_length=1000)
    abstract: str = Field(..., min_length=50)
    keywords: Optional[str] = None


class PaperCreate(PaperBase):
    """Schema for creating a paper submission."""
    conference_id: int
    track_id: Optional[int] = None
    authors: List[AuthorInfo]


class PaperUpdate(BaseModel):
    """Schema for updating a paper."""
    title: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    track_id: Optional[int] = None
    authors: Optional[List[AuthorInfo]] = None


class AuthorResponse(BaseModel):
    """Author response in paper."""
    id: int
    order: int
    is_corresponding: bool
    first_name: str
    last_name: str
    affiliation: Optional[str]
    country: Optional[str]
    email: Optional[str]  # Hidden in double-blind
    
    class Config:
        from_attributes = True


class PaperResponse(PaperBase):
    """Schema for paper response."""
    id: int
    conference_id: int
    track_id: Optional[int]
    submitter_id: int
    paper_number: Optional[str]
    status: PaperStatus
    
    # Files
    pdf_path: Optional[str]
    supplementary_path: Optional[str]
    
    # Metadata
    page_count: Optional[int]
    
    # Timestamps
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # AI features
    ai_summary: Optional[str]
    
    class Config:
        from_attributes = True


class PaperWithAuthors(PaperResponse):
    """Paper response with authors."""
    authors: List[AuthorResponse] = []


class PaperSubmit(BaseModel):
    """Schema for submitting a paper (changing status to submitted)."""
    confirm: bool = True


class PaperWithdraw(BaseModel):
    """Schema for withdrawing a paper."""
    reason: Optional[str] = None
