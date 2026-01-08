from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class PaperAuthorModel(Base):
    """
    Paper-Author relationship model.
    Maps authors to papers with ordering and affiliation info.
    Supports both registered users and external co-authors.
    """
    __tablename__ = 'paper_authors'
    __table_args__ = (
        Index('idx_paper_author_paper', 'paper_id'),
        Index('idx_paper_author_user', 'user_id'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('flask_user.id'), nullable=True)  # Null for external co-authors
    
    # Author order (1 = first author, etc.)
    author_order = Column(Integer, nullable=False, default=1)
    
    # Author info (for external co-authors or override registered user info)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    affiliation = Column(String(500), nullable=True)  # University/Organization
    country = Column(String(100), nullable=True)
    orcid = Column(String(50), nullable=True)  # ORCID identifier
    
    # Flags
    is_corresponding = Column(Boolean, default=False)
    is_presenter = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paper = relationship("PaperModel", back_populates="authors")
