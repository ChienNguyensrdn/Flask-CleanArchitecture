"""Track model for conference tracks/topics."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Track(Base):
    """
    Track model for organizing papers by topic/area.
    Each conference can have multiple tracks.
    """
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"), nullable=False)
    
    # Track info
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    submission_limit = Column(Integer, nullable=True)  # Max papers in track
    
    # Deadlines (override conference defaults if set)
    submission_deadline = Column(DateTime, nullable=True)
    review_deadline = Column(DateTime, nullable=True)
    
    # Chair for this track
    track_chair_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Order for display
    display_order = Column(Integer, default=0)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship("Conference", back_populates="tracks")
    papers = relationship("Paper", back_populates="track")
    pc_members = relationship("PCMember", back_populates="track")
