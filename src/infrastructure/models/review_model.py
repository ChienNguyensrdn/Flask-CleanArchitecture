from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class ReviewModel(Base):
    """
    Review model for storing paper reviews.
    Includes scores, comments, and confidential notes.
    """
    __tablename__ = 'reviews'
    __table_args__ = (
        Index('idx_review_paper', 'paper_id'),
        Index('idx_review_reviewer', 'reviewer_pc_id'),
        Index('idx_review_status', 'status'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    reviewer_pc_id = Column(Integer, ForeignKey('pc_members.id'), nullable=False)
    assignment_id = Column(Integer, ForeignKey('paper_assignments.id'), nullable=True)
    
    # Overall evaluation
    overall_score = Column(Integer, nullable=True)  # e.g., 1-10 or -3 to +3
    confidence_score = Column(Integer, nullable=True)  # Reviewer confidence 1-5
    recommendation = Column(String(50), nullable=True)  
    # strong_accept, accept, weak_accept, borderline, weak_reject, reject, strong_reject
    
    # Detailed scores (customizable per conference)
    originality_score = Column(Integer, nullable=True)
    significance_score = Column(Integer, nullable=True)
    technical_quality_score = Column(Integer, nullable=True)
    clarity_score = Column(Integer, nullable=True)
    relevance_score = Column(Integer, nullable=True)
    
    # Review text
    summary = Column(Text, nullable=True)  # Brief summary of the paper
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    detailed_comments = Column(Text, nullable=True)  # Visible to authors
    confidential_comments = Column(Text, nullable=True)  # Only for PC/chairs
    
    # Questions for authors (for rebuttal)
    questions_for_authors = Column(Text, nullable=True)
    
    # AI-assisted features (optional)
    ai_key_points = Column(Text, nullable=True)  # AI-extracted key points
    
    # Review status
    status = Column(String(50), default='draft')  # draft, submitted, revised
    submitted_at = Column(DateTime, nullable=True)
    
    # Post-rebuttal update
    post_rebuttal_comments = Column(Text, nullable=True)
    post_rebuttal_score = Column(Integer, nullable=True)
    post_rebuttal_updated_at = Column(DateTime, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paper = relationship("PaperModel", back_populates="reviews")
    reviewer_pc = relationship("PCMemberModel", back_populates="reviews")


class ReviewDiscussionModel(Base):
    """
    Internal PC discussion model for papers.
    Allows PC members to discuss papers privately.
    """
    __tablename__ = 'review_discussions'
    __table_args__ = (
        Index('idx_discussion_paper', 'paper_id'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    pc_member_id = Column(Integer, ForeignKey('pc_members.id'), nullable=False)
    
    # Discussion content
    message = Column(Text, nullable=False)
    
    # Reply to another discussion
    parent_id = Column(Integer, ForeignKey('review_discussions.id'), nullable=True)
    
    # Visibility
    is_visible_to_authors = Column(Boolean, default=False)  # For shepherding discussions
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
