"""Email template model for notification templates."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class EmailTemplateType(str, enum.Enum):
    """Types of email templates."""
    PC_INVITATION = "pc_invitation"
    SUBMISSION_CONFIRMATION = "submission_confirmation"
    REVIEW_ASSIGNMENT = "review_assignment"
    REVIEW_REMINDER = "review_reminder"
    DECISION_ACCEPT = "decision_accept"
    DECISION_REJECT = "decision_reject"
    DECISION_REVISION = "decision_revision"
    CAMERA_READY_OPEN = "camera_ready_open"
    CAMERA_READY_REMINDER = "camera_ready_reminder"
    CUSTOM = "custom"


class EmailTemplate(Base):
    """
    Email template model for customizable notifications.
    Supports placeholders for dynamic content.
    """
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"), nullable=False)
    
    # Template info
    name = Column(String(255), nullable=False)
    template_type = Column(SQLEnum(EmailTemplateType), nullable=False)
    
    # Content
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)  # Plain text version
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    conference = relationship("Conference", back_populates="email_templates")
