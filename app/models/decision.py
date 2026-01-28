"""Decision model for paper acceptance decisions."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class DecisionType(str, enum.Enum):
    """Paper decision types."""
    ACCEPTED = "accepted"
    CONDITIONALLY_ACCEPTED = "conditionally_accepted"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"


class Decision(Base):
    """
    Decision model for final paper decisions.
    Records accept/reject decisions made by chairs.
    """
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, unique=True)
    decided_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Decision
    decision = Column(SQLEnum(DecisionType), nullable=False)
    
    # Feedback
    meta_review = Column(Text, nullable=True)  # Chair's summary
    feedback_to_authors = Column(Text, nullable=True)  # Anonymized feedback
    
    # For conditional acceptance
    conditions = Column(Text, nullable=True)
    
    # Notification
    notification_sent = Column(Integer, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    
    # Timestamps
    decided_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paper = relationship("Paper", back_populates="decision")
