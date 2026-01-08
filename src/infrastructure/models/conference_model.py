from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class ConferenceModel(Base):
    """
    Conference model for managing scientific conferences.
    Supports CFP (Call for Papers), deadlines, and conference settings.
    """
    __tablename__ = 'conferences'
    __table_args__ = (
        Index('idx_conference_short_name', 'short_name'),
        Index('idx_conference_status', 'status'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey('Tenant.Tenant_ID'), nullable=False)
    
    # Basic info
    name = Column(String(500), nullable=False)
    short_name = Column(String(100), nullable=False)  # e.g., "UTH-CONF-2026"
    description = Column(Text, nullable=True)
    website_url = Column(String(500), nullable=True)
    venue = Column(String(500), nullable=True)
    
    # Important dates
    submission_deadline = Column(DateTime, nullable=True)
    review_deadline = Column(DateTime, nullable=True)
    notification_date = Column(DateTime, nullable=True)
    camera_ready_deadline = Column(DateTime, nullable=True)
    conference_start_date = Column(DateTime, nullable=True)
    conference_end_date = Column(DateTime, nullable=True)
    
    # CFP settings
    cfp_content = Column(Text, nullable=True)  # Call for Papers content
    cfp_is_public = Column(Boolean, default=False)
    
    # Review settings
    review_mode = Column(String(50), default='double_blind')  # single_blind, double_blind, open
    min_reviews_per_paper = Column(Integer, default=3)
    allow_rebuttal = Column(Boolean, default=False)
    rebuttal_deadline = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), default='draft')  # draft, open, reviewing, decided, published
    
    # Audit fields
    created_by = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tracks = relationship("TrackModel", back_populates="conference")
    papers = relationship("PaperModel", back_populates="conference")
    pc_members = relationship("PCMemberModel", back_populates="conference")
