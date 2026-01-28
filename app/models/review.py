"""Review model for paper reviews."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class ReviewRecommendation(str, enum.Enum):
    """Review recommendation."""
    STRONG_ACCEPT = "strong_accept"
    ACCEPT = "accept"
    WEAK_ACCEPT = "weak_accept"
    BORDERLINE = "borderline"
    WEAK_REJECT = "weak_reject"
    REJECT = "reject"
    STRONG_REJECT = "strong_reject"


class Review(Base):
    """
    Review model for paper evaluations.
    Contains scores, comments, and recommendations.
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("paper_assignments.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Scores (typically 1-10)
    overall_score = Column(Integer, nullable=True)
    originality_score = Column(Integer, nullable=True)
    significance_score = Column(Integer, nullable=True)
    clarity_score = Column(Integer, nullable=True)
    technical_quality_score = Column(Integer, nullable=True)
    
    # Recommendation
    recommendation = Column(SQLEnum(ReviewRecommendation), nullable=True)
    
    # Confidence (1-5)
    confidence = Column(Integer, nullable=True)
    
    # Comments
    summary = Column(Text, nullable=True)  # Summary of the paper
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    comments_to_authors = Column(Text, nullable=True)  # Visible to authors
    confidential_comments = Column(Text, nullable=True)  # Only for chairs
    
    # Rebuttal response
    rebuttal_response = Column(Text, nullable=True)
    post_rebuttal_score = Column(Integer, nullable=True)
    post_rebuttal_recommendation = Column(SQLEnum(ReviewRecommendation), nullable=True)
    
    # Status
    is_submitted = Column(Boolean, default=False)
    is_final = Column(Boolean, default=False)
    
    # Timestamps
    submitted_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assignment = relationship("PaperAssignment", back_populates="review")
    paper = relationship("Paper", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
    discussions = relationship("ReviewDiscussion", back_populates="review")
