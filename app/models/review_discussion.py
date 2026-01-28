"""Review discussion model for internal PC discussions."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ReviewDiscussion(Base):
    """
    Internal discussion between PC members about a review/paper.
    Only visible to PC members and chairs.
    """
    __tablename__ = "review_discussions"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    message = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    review = relationship("Review", back_populates="discussions")
