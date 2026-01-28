"""Conference schemas for API requests/responses."""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.models.conference import ConferenceStatus, ReviewMode


class TrackBase(BaseModel):
    """Base track schema."""
    name: str = Field(..., min_length=1, max_length=255)
    short_name: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0


class TrackCreate(TrackBase):
    """Schema for creating a track."""
    submission_deadline: Optional[datetime] = None
    review_deadline: Optional[datetime] = None


class TrackResponse(TrackBase):
    """Schema for track response."""
    id: int
    conference_id: int
    is_active: bool
    track_chair_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConferenceBase(BaseModel):
    """Base conference schema."""
    name: str = Field(..., min_length=1, max_length=500)
    short_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    website_url: Optional[str] = None
    venue: Optional[str] = None


class ConferenceCreate(ConferenceBase):
    """Schema for creating a conference."""
    tenant_id: int
    review_mode: ReviewMode = ReviewMode.DOUBLE_BLIND
    
    # Deadlines
    submission_deadline: Optional[datetime] = None
    abstract_deadline: Optional[datetime] = None
    review_deadline: Optional[datetime] = None
    notification_date: Optional[datetime] = None
    camera_ready_deadline: Optional[datetime] = None
    conference_start_date: Optional[datetime] = None
    conference_end_date: Optional[datetime] = None
    
    # Settings
    min_reviews_per_paper: int = 3
    max_papers_per_reviewer: int = 10
    allow_rebuttal: bool = False


class ConferenceUpdate(BaseModel):
    """Schema for updating a conference."""
    name: Optional[str] = None
    short_name: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    venue: Optional[str] = None
    status: Optional[ConferenceStatus] = None
    review_mode: Optional[ReviewMode] = None
    
    # Deadlines
    submission_deadline: Optional[datetime] = None
    abstract_deadline: Optional[datetime] = None
    review_deadline: Optional[datetime] = None
    notification_date: Optional[datetime] = None
    camera_ready_deadline: Optional[datetime] = None
    
    # CFP
    cfp_content: Optional[str] = None
    cfp_is_public: Optional[bool] = None
    
    # Settings
    min_reviews_per_paper: Optional[int] = None
    max_papers_per_reviewer: Optional[int] = None


class ConferenceResponse(ConferenceBase):
    """Schema for conference response."""
    id: int
    tenant_id: int
    status: ConferenceStatus
    review_mode: ReviewMode
    
    # Deadlines
    submission_deadline: Optional[datetime]
    abstract_deadline: Optional[datetime]
    review_deadline: Optional[datetime]
    notification_date: Optional[datetime]
    camera_ready_deadline: Optional[datetime]
    conference_start_date: Optional[datetime]
    conference_end_date: Optional[datetime]
    
    # CFP
    cfp_content: Optional[str]
    cfp_is_public: bool
    
    # Settings
    min_reviews_per_paper: int
    max_papers_per_reviewer: int
    allow_rebuttal: bool
    
    # AI settings
    ai_grammar_check_enabled: bool
    ai_summary_enabled: bool
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConferenceWithTracks(ConferenceResponse):
    """Conference response with tracks."""
    tracks: List[TrackResponse] = []


class CFPPublic(BaseModel):
    """Public CFP information."""
    id: int
    name: str
    short_name: str
    description: Optional[str]
    venue: Optional[str]
    cfp_content: Optional[str]
    submission_deadline: Optional[datetime]
    conference_start_date: Optional[datetime]
    conference_end_date: Optional[datetime]
    tracks: List[TrackResponse] = []
    
    class Config:
        from_attributes = True
