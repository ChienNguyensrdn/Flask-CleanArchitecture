"""Conflict of Interest (COI) model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class COIType(str, enum.Enum):
    """Types of conflicts of interest."""
    COAUTHOR = "coauthor"           # Recent co-authorship
    ADVISOR = "advisor"             # PhD advisor/student
    COLLEAGUE = "colleague"         # Same institution
    COLLABORATOR = "collaborator"   # Current collaboration
    FAMILY = "family"               # Family member
    OTHER = "other"                 # Other conflict


class COI(Base):
    """
    Conflict of Interest declaration model.
    Records COI between PC members and papers/authors.
    """
    __tablename__ = "coi_declarations"

    id = Column(Integer, primary_key=True, index=True)
    pc_member_id = Column(Integer, ForeignKey("pc_members.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # COI details
    coi_type = Column(SQLEnum(COIType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    declared_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pc_member = relationship("PCMember", back_populates="coi_declarations")
