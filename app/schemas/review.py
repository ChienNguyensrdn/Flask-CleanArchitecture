"""Review schemas for API requests/responses."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.review import ReviewRecommendation
from app.models.decision import DecisionType


class ReviewBase(BaseModel):
    """Base review schema."""
    overall_score: Optional[int] = Field(None, ge=1, le=10)
    originality_score: Optional[int] = Field(None, ge=1, le=10)
    significance_score: Optional[int] = Field(None, ge=1, le=10)
    clarity_score: Optional[int] = Field(None, ge=1, le=10)
    technical_quality_score: Optional[int] = Field(None, ge=1, le=10)
    confidence: Optional[int] = Field(None, ge=1, le=5)
    recommendation: Optional[ReviewRecommendation] = None


class ReviewCreate(ReviewBase):
    """Schema for creating/updating a review."""
    summary: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    comments_to_authors: Optional[str] = None
    confidential_comments: Optional[str] = None


class ReviewSubmit(ReviewCreate):
    """Schema for submitting a review (marks as final)."""
    is_final: bool = True


class ReviewResponse(ReviewBase):
    """Schema for review response."""
    id: int
    assignment_id: int
    paper_id: int
    reviewer_id: int
    
    summary: Optional[str]
    strengths: Optional[str]
    weaknesses: Optional[str]
    comments_to_authors: Optional[str]
    confidential_comments: Optional[str]  # Only for chairs
    
    is_submitted: bool
    is_final: bool
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewForAuthor(BaseModel):
    """Review information visible to authors (anonymized)."""
    overall_score: Optional[int]
    recommendation: Optional[ReviewRecommendation]
    strengths: Optional[str]
    weaknesses: Optional[str]
    comments_to_authors: Optional[str]


class DiscussionMessage(BaseModel):
    """Schema for review discussion message."""
    message: str = Field(..., min_length=1)


class DiscussionResponse(BaseModel):
    """Schema for discussion message response."""
    id: int
    review_id: int
    author_id: int
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DecisionCreate(BaseModel):
    """Schema for making a decision on a paper."""
    decision: DecisionType
    meta_review: Optional[str] = None
    feedback_to_authors: Optional[str] = None
    conditions: Optional[str] = None  # For conditional acceptance


class DecisionResponse(BaseModel):
    """Schema for decision response."""
    id: int
    paper_id: int
    decided_by_id: int
    decision: DecisionType
    meta_review: Optional[str]
    feedback_to_authors: Optional[str]
    conditions: Optional[str]
    notification_sent: bool
    decided_at: datetime
    
    class Config:
        from_attributes = True
