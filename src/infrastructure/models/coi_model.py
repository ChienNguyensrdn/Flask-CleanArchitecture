from sqlalchemy import Column, Integer, String, DateTime, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class COIModel(Base):
    """
    Conflict of Interest (COI) model.
    Tracks conflicts between PC members and paper authors/institutions.
    Used to prevent biased assignments and enforce review integrity.
    """
    __tablename__ = 'conflicts_of_interest'
    __table_args__ = (
        Index('idx_coi_pc_member', 'pc_member_id'),
        Index('idx_coi_paper', 'paper_id'),
        Index('idx_coi_author', 'author_user_id'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    pc_member_id = Column(Integer, ForeignKey('pc_members.id'), nullable=False)
    
    # Conflict can be with a specific paper or author
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=True)
    author_user_id = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    
    # Conflict type
    conflict_type = Column(String(100), nullable=False)
    # Types: 'co_author', 'same_institution', 'advisor_advisee', 'collaborator', 
    #        'personal', 'financial', 'other'
    
    # Details
    institution = Column(String(500), nullable=True)  # For institution-based conflicts
    description = Column(Text, nullable=True)
    
    # How was it declared
    declared_by = Column(String(50), default='self')  # self, chair, system
    
    # Validity period (for collaborator conflicts)
    conflict_start_date = Column(DateTime, nullable=True)
    conflict_end_date = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    verified_by = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pc_member = relationship("PCMemberModel", back_populates="conflicts")


# Import Boolean for is_active column
from sqlalchemy import Boolean
