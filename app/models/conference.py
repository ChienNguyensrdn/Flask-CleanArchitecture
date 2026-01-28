"""Conference model for managing scientific conferences."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class ConferenceStatus(str, enum.Enum):
    """Conference lifecycle status."""
    DRAFT = "draft"
    CFP_OPEN = "cfp_open"          # Call for papers open
    SUBMISSION_OPEN = "submission_open"
    SUBMISSION_CLOSED = "submission_closed"
    UNDER_REVIEW = "under_review"
    DECISION_PENDING = "decision_pending"
    DECISIONS_SENT = "decisions_sent"
    CAMERA_READY = "camera_ready"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ReviewMode(str, enum.Enum):
    """Review anonymity modes."""
    SINGLE_BLIND = "single_blind"   # Reviewers know authors
    DOUBLE_BLIND = "double_blind"   # Neither knows the other
    OPEN = "open"                   # No anonymity


class Conference(Base):
    """
    Conference model for scientific conferences.
    Contains all settings, deadlines, and CFP information.
    """
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Basic info
    name = Column(String(500), nullable=False)
    short_name = Column(String(100), nullable=False)  # e.g., "ICSE 2026"
    description = Column(Text, nullable=True)
    website_url = Column(String(500), nullable=True)
    venue = Column(String(500), nullable=True)
    
    # Status and mode
    status = Column(SQLEnum(ConferenceStatus), default=ConferenceStatus.DRAFT)
    review_mode = Column(SQLEnum(ReviewMode), default=ReviewMode.DOUBLE_BLIND)
    
    # Deadlines
    submission_deadline = Column(DateTime, nullable=True)
    abstract_deadline = Column(DateTime, nullable=True)
    review_deadline = Column(DateTime, nullable=True)
    rebuttal_start = Column(DateTime, nullable=True)
    rebuttal_end = Column(DateTime, nullable=True)
    notification_date = Column(DateTime, nullable=True)
    camera_ready_deadline = Column(DateTime, nullable=True)
    conference_start_date = Column(DateTime, nullable=True)
    conference_end_date = Column(DateTime, nullable=True)
    
    # CFP (Call for Papers)
    cfp_content = Column(Text, nullable=True)  # Markdown/HTML
    cfp_is_public = Column(Boolean, default=False)
    
    # Review settings
    min_reviews_per_paper = Column(Integer, default=3)
    max_papers_per_reviewer = Column(Integer, default=10)
    allow_rebuttal = Column(Boolean, default=False)
    
    # AI settings
    ai_grammar_check_enabled = Column(Boolean, default=False)
    ai_summary_enabled = Column(Boolean, default=False)
    ai_assignment_hints_enabled = Column(Boolean, default=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="conferences")
    tracks = relationship("Track", back_populates="conference", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="conference")
    pc_members = relationship("PCMember", back_populates="conference")
    email_templates = relationship("EmailTemplate", back_populates="conference")
