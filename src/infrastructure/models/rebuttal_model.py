from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from infrastructure.databases.base import Base
from datetime import datetime


class RebuttalModel(Base):
    """
    Rebuttal model for author responses to reviews.
    Allows authors to address reviewer concerns before final decisions.
    """
    __tablename__ = 'rebuttals'
    __table_args__ = (
        Index('idx_rebuttal_paper', 'paper_id'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    
    # Rebuttal content
    response_text = Column(Text, nullable=False)
    
    # Author who submitted
    submitted_by = Column(Integer, ForeignKey('flask_user.id'), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional response to specific review
    review_id = Column(Integer, ForeignKey('reviews.id'), nullable=True)
    
    # Version tracking (if multiple revisions allowed)
    version = Column(Integer, default=1)
    
    # Word/character limits
    word_count = Column(Integer, nullable=True)
    
    # Status
    is_submitted = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
