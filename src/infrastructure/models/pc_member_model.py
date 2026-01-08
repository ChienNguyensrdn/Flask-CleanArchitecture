from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class PCMemberModel(Base):
    """
    Program Committee Member model.
    Manages PC members for conferences, including track assignments and roles.
    """
    __tablename__ = 'pc_members'
    __table_args__ = (
        Index('idx_pc_member_conference', 'conference_id'),
        Index('idx_pc_member_user', 'user_id'),
        Index('idx_pc_member_track', 'track_id'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    conference_id = Column(Integer, ForeignKey('conferences.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('flask_user.id'), nullable=False)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=True)  # Null = all tracks
    
    # Role in the conference
    role = Column(String(50), default='reviewer')  
    # reviewer, senior_pc, track_chair, program_chair, general_chair
    
    # Invitation status
    invitation_status = Column(String(50), default='pending')  # pending, accepted, declined
    invitation_sent_at = Column(DateTime, nullable=True)
    invitation_responded_at = Column(DateTime, nullable=True)
    
    # Expertise areas (for assignment matching)
    expertise_keywords = Column(Text, nullable=True)  # Comma-separated keywords
    
    # Review quota
    max_papers = Column(Integer, default=10)  # Maximum papers to review
    assigned_count = Column(Integer, default=0)  # Currently assigned papers
    
    # Flags
    is_active = Column(Boolean, default=True)
    can_access_author_info = Column(Boolean, default=False)  # For single-blind mode
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship("ConferenceModel", back_populates="pc_members")
    assignments = relationship("PaperAssignmentModel", back_populates="reviewer")
    reviews = relationship("ReviewModel", back_populates="reviewer_pc")
    conflicts = relationship("COIModel", back_populates="pc_member")
