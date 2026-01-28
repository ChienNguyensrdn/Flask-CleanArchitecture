"""Paper assignment model for reviewer-paper assignments."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class AssignmentStatus(str, enum.Enum):
    """Assignment status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"


class PaperAssignment(Base):
    """
    Paper assignment model for reviewer-paper assignments.
    Tracks assignment status and review progress.
    """
    __tablename__ = "paper_assignments"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("pc_members.id"), nullable=False)
    
    # Status
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.PENDING)
    
    # Assignment type
    is_primary = Column(Integer, default=False)  # Primary vs secondary reviewer
    
    # Timestamps
    assigned_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Notes (for chairs)
    notes = Column(String(500), nullable=True)
    
    # Relationships
    paper = relationship("Paper", back_populates="assignments")
    reviewer = relationship("PCMember", back_populates="assignments")
    review = relationship("Review", back_populates="assignment", uselist=False)
