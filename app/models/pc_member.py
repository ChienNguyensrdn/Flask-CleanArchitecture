"""PC Member model for program committee management."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class PCRole(str, enum.Enum):
    """PC member roles."""
    REVIEWER = "reviewer"
    SENIOR_PC = "senior_pc"
    TRACK_CHAIR = "track_chair"
    PROGRAM_CHAIR = "program_chair"
    GENERAL_CHAIR = "general_chair"


class InvitationStatus(str, enum.Enum):
    """Invitation status for PC members."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class PCMember(Base):
    """
    Program Committee member model.
    Manages reviewers and their assignments for conferences.
    """
    __tablename__ = "pc_members"

    id = Column(Integer, primary_key=True, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=True)  # Null = all tracks
    
    # Role
    role = Column(SQLEnum(PCRole), default=PCRole.REVIEWER)
    
    # Invitation
    invitation_status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.PENDING)
    invitation_sent_at = Column(DateTime, nullable=True)
    invitation_responded_at = Column(DateTime, nullable=True)
    
    # Expertise
    expertise_keywords = Column(Text, nullable=True)  # Comma-separated
    
    # Quota
    max_papers = Column(Integer, default=10)
    assigned_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    can_access_author_info = Column(Boolean, default=False)  # For single-blind
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship("Conference", back_populates="pc_members")
    user = relationship("User", back_populates="pc_memberships")
    track = relationship("Track", back_populates="pc_members")
    assignments = relationship("PaperAssignment", back_populates="reviewer")
    bids = relationship("Bid", back_populates="pc_member")
    coi_declarations = relationship("COI", back_populates="pc_member")
