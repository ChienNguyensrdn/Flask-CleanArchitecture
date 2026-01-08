from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class DecisionModel(Base):
    """
    Decision model for paper acceptance/rejection.
    Records the final decision made by chairs after review aggregation.
    """
    __tablename__ = 'decisions'
    __table_args__ = (
        Index('idx_decision_paper', 'paper_id'),
        Index('idx_decision_status', 'decision'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False, unique=True)
    
    # Decision details
    decision = Column(String(50), nullable=False)  
    # accept, conditional_accept, reject, desk_reject
    
    decision_type = Column(String(50), nullable=True)
    # full_paper, short_paper, poster, workshop
    
    # Decision maker
    decided_by = Column(Integer, ForeignKey('flask_user.id'), nullable=False)
    decided_at = Column(DateTime, default=datetime.utcnow)
    
    # Review statistics at decision time
    avg_score = Column(Integer, nullable=True)
    review_count = Column(Integer, nullable=True)
    
    # Internal notes (not shared with authors)
    internal_notes = Column(Text, nullable=True)
    
    # Feedback to authors
    meta_review = Column(Text, nullable=True)  # Summary of reviews for authors
    feedback_to_authors = Column(Text, nullable=True)  # Additional comments
    
    # Conditional accept requirements
    conditions = Column(Text, nullable=True)  # What needs to be addressed
    conditions_met = Column(Boolean, default=False)
    conditions_verified_by = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    conditions_verified_at = Column(DateTime, nullable=True)
    
    # Notification status
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    
    # AI-assisted (optional)
    ai_draft_feedback = Column(Text, nullable=True)  # AI-drafted feedback template
    ai_feedback_used = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paper = relationship("PaperModel", back_populates="decision")
