from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class TrackModel(Base):
    """
    Track/Topic model for organizing conference submissions by subject area.
    Each conference can have multiple tracks (e.g., AI, Security, Networks).
    """
    __tablename__ = 'tracks'
    __table_args__ = (
        Index('idx_track_conference', 'conference_id'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    conference_id = Column(Integer, ForeignKey('conferences.id'), nullable=False)
    
    # Track info
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # Comma-separated keywords
    
    # Track-specific deadlines (override conference defaults)
    submission_deadline = Column(DateTime, nullable=True)
    review_deadline = Column(DateTime, nullable=True)
    
    # Track chair
    track_chair_id = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship("ConferenceModel", back_populates="tracks")
    papers = relationship("PaperModel", back_populates="track")
