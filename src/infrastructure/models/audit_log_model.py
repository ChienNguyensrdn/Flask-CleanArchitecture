from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from infrastructure.databases.base import Base
from datetime import datetime


class AuditLogModel(Base):
    """
    Audit Log model for tracking all system activities.
    Provides comprehensive audit trail for compliance and debugging.
    """
    __tablename__ = 'audit_logs'
    __table_args__ = (
        Index('idx_audit_log_user', 'user_id'),
        Index('idx_audit_log_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_created', 'created_at'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Who performed the action
    user_id = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    user_email = Column(String(255), nullable=True)
    user_ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # What entity was affected
    entity_type = Column(String(100), nullable=False)  
    # paper, review, conference, user, decision, etc.
    entity_id = Column(Integer, nullable=True)
    
    # What action was performed
    action = Column(String(100), nullable=False)
    # create, update, delete, view, submit, assign, etc.
    
    # Details of the change
    old_value = Column(Text, nullable=True)  # JSON of previous state
    new_value = Column(Text, nullable=True)  # JSON of new state
    description = Column(Text, nullable=True)
    
    # Context
    conference_id = Column(Integer, ForeignKey('conferences.id'), nullable=True)
    
    # For AI operations
    ai_operation = Column(Boolean, default=False)
    ai_model_id = Column(String(100), nullable=True)
    ai_prompt_hash = Column(String(64), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
