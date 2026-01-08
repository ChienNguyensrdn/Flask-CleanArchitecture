from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class PaperAssignmentModel(Base):
    """
    Paper Assignment model for assigning reviewers to papers.
    Tracks assignment method (manual/automatic) and reviewer response.
    """
    __tablename__ = 'paper_assignments'
    __table_args__ = (
        Index('idx_assignment_paper', 'paper_id'),
        Index('idx_assignment_reviewer', 'reviewer_id'),
        Index('idx_assignment_status', 'status'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('pc_members.id'), nullable=False)
    
    # Assignment info
    assignment_method = Column(String(50), default='manual')  # manual, automatic, bidding
    assigned_by = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # AI-assisted matching (optional)
    ai_similarity_score = Column(Integer, nullable=True)  # 0-100 score from keyword matching
    ai_match_reason = Column(Text, nullable=True)  # Explanation of why matched
    
    # Reviewer response
    status = Column(String(50), default='pending')  
    # pending, accepted, declined, completed
    
    declined_reason = Column(Text, nullable=True)
    response_at = Column(DateTime, nullable=True)
    
    # Review deadline for this assignment
    due_date = Column(DateTime, nullable=True)
    
    # Flags
    is_lead_reviewer = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paper = relationship("PaperModel", back_populates="assignments")
    reviewer = relationship("PCMemberModel", back_populates="assignments")
