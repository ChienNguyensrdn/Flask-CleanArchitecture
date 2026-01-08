from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from infrastructure.databases.base import Base
from datetime import datetime


class EmailTemplateModel(Base):
    """
    Email Template model for conference communications.
    Stores customizable email templates for notifications.
    """
    __tablename__ = 'email_templates'
    __table_args__ = (
        Index('idx_email_template_conference', 'conference_id'),
        Index('idx_email_template_type', 'template_type'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    conference_id = Column(Integer, ForeignKey('conferences.id'), nullable=True)  # Null = system default
    
    # Template identification
    template_type = Column(String(100), nullable=False)
    # Types: 'submission_confirmation', 'pc_invitation', 'review_assigned', 
    #        'review_reminder', 'decision_accept', 'decision_reject', 
    #        'camera_ready_reminder', 'rebuttal_open', etc.
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template content
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    
    # Available placeholders
    # {{author_name}}, {{paper_title}}, {{conference_name}}, {{deadline}}, etc.
    
    # Language support
    language = Column(String(10), default='en')  # en, vi, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # System default template
    
    # AI-assisted (optional)
    ai_generated = Column(Boolean, default=False)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailLogModel(Base):
    """
    Email Log model for tracking sent emails.
    Provides audit trail for all conference communications.
    """
    __tablename__ = 'email_logs'
    __table_args__ = (
        Index('idx_email_log_conference', 'conference_id'),
        Index('idx_email_log_recipient', 'recipient_email'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    conference_id = Column(Integer, ForeignKey('conferences.id'), nullable=True)
    template_id = Column(Integer, ForeignKey('email_templates.id'), nullable=True)
    
    # Recipient info
    recipient_user_id = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(255), nullable=True)
    
    # Email content
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=True)
    
    # Related entities
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=True)
    
    # Status
    status = Column(String(50), default='pending')  # pending, sent, failed, bounced
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
