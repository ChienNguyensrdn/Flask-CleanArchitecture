"""Paper model for submissions."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class PaperStatus(str, enum.Enum):
    """Paper submission status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    REVISION_REQUESTED = "revision_requested"
    ACCEPTED = "accepted"
    CONDITIONALLY_ACCEPTED = "conditionally_accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    CAMERA_READY = "camera_ready"


class Paper(Base):
    """
    Paper model for manuscript submissions.
    Tracks the full lifecycle from submission to camera-ready.
    """
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=True)
    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Paper identification
    paper_number = Column(String(50), nullable=True)  # e.g., "CONF-2026-001"
    
    # Content
    title = Column(String(1000), nullable=False)
    abstract = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # Comma-separated
    
    # Files
    pdf_path = Column(String(500), nullable=True)
    supplementary_path = Column(String(500), nullable=True)
    camera_ready_path = Column(String(500), nullable=True)
    
    # Metadata
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Status
    status = Column(SQLEnum(PaperStatus), default=PaperStatus.DRAFT)
    
    # Timestamps
    submitted_at = Column(DateTime, nullable=True)
    withdrawn_at = Column(DateTime, nullable=True)
    decision_at = Column(DateTime, nullable=True)
    
    # Flags
    is_withdrawn = Column(Boolean, default=False)
    requires_revision = Column(Boolean, default=False)
    
    # AI features
    ai_grammar_checked = Column(Boolean, default=False)
    ai_summary = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship("Conference", back_populates="papers")
    track = relationship("Track", back_populates="papers")
    submitter = relationship("User", back_populates="submitted_papers", foreign_keys=[submitter_id])
    authors = relationship("PaperAuthor", back_populates="paper", order_by="PaperAuthor.order")
    assignments = relationship("PaperAssignment", back_populates="paper")
    reviews = relationship("Review", back_populates="paper")
    decision = relationship("Decision", back_populates="paper", uselist=False)
    camera_ready = relationship("CameraReady", back_populates="paper", uselist=False)
