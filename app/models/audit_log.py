"""Audit log model for activity tracking."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    """
    Audit log model for tracking all system activities.
    Provides full audit trail for compliance and debugging.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Actor
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    
    # Action
    action = Column(String(100), nullable=False)  # e.g., "paper.submit", "review.create"
    entity_type = Column(String(100), nullable=False)  # e.g., "paper", "review"
    entity_id = Column(Integer, nullable=True)
    
    # Details
    description = Column(Text, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # AI-related (if applicable)
    ai_model = Column(String(100), nullable=True)
    ai_prompt_hash = Column(String(64), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
