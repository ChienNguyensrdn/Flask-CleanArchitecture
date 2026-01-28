"""Tenant model for multi-tenancy support."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Tenant(Base):
    """
    Tenant model for multi-tenancy.
    Each tenant represents an institution/organization.
    """
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Contact info
    contact_email = Column(String(255), nullable=True)
    website_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    max_conferences = Column(Integer, default=10)
    max_users = Column(Integer, default=1000)
    
    # SMTP settings (per-tenant)
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(Integer, nullable=True)
    smtp_user = Column(String(255), nullable=True)
    smtp_password = Column(String(255), nullable=True)
    smtp_from_email = Column(String(255), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    conferences = relationship("Conference", back_populates="tenant")
