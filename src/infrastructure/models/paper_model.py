from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class PaperModel(Base):
    """
    Paper/Submission model for managing research paper submissions.
    Tracks the full lifecycle: submission -> review -> decision -> camera-ready.
    """
    __tablename__ = 'papers'
    __table_args__ = (
        Index('idx_paper_conference', 'conference_id'),
        Index('idx_paper_track', 'track_id'),
        Index('idx_paper_status', 'status'),
        Index('idx_paper_submitter', 'submitter_id'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    conference_id = Column(Integer, ForeignKey('conferences.id'), nullable=False)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=True)
    submitter_id = Column(Integer, ForeignKey('flask_user.id'), nullable=False)
    
    # Paper identification
    paper_number = Column(String(50), nullable=True)  # e.g., "CONF-2026-001"
    
    # Paper content
    title = Column(String(1000), nullable=False)
    abstract = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # Comma-separated keywords
    
    # File paths
    pdf_path = Column(String(500), nullable=True)  # Main submission PDF
    supplementary_path = Column(String(500), nullable=True)  # Additional materials
    
    # Submission metadata
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Status tracking
    status = Column(String(50), default='draft')  
    # draft, submitted, under_review, revision_requested, accepted, rejected, withdrawn, camera_ready
    
    # Timestamps
    submitted_at = Column(DateTime, nullable=True)
    withdrawn_at = Column(DateTime, nullable=True)
    
    # Flags
    is_withdrawn = Column(Boolean, default=False)
    requires_revision = Column(Boolean, default=False)
    
    # AI-assisted features (optional)
    ai_grammar_checked = Column(Boolean, default=False)
    ai_summary = Column(Text, nullable=True)  # AI-generated summary for bidding
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship("ConferenceModel", back_populates="papers")
    track = relationship("TrackModel", back_populates="papers")
    authors = relationship("PaperAuthorModel", back_populates="paper", order_by="PaperAuthorModel.author_order")
    assignments = relationship("PaperAssignmentModel", back_populates="paper")
    reviews = relationship("ReviewModel", back_populates="paper")
    decision = relationship("DecisionModel", back_populates="paper", uselist=False)
    camera_ready = relationship("CameraReadyModel", back_populates="paper", uselist=False)
