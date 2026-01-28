"""Bid model for reviewer bidding on papers."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class BidValue(int, enum.Enum):
    """Bid preference values."""
    CONFLICT = -2      # Conflict of interest
    NOT_WILLING = -1   # Not willing to review
    NEUTRAL = 0        # Neutral/no preference
    WILLING = 1        # Willing to review
    EAGER = 2          # Eager to review (expert)


class Bid(Base):
    """
    Bid model for PC member bidding on papers.
    Used during paper assignment phase.
    """
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    pc_member_id = Column(Integer, ForeignKey("pc_members.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    
    # Bid value
    bid_value = Column(SQLEnum(BidValue), default=BidValue.NEUTRAL)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pc_member = relationship("PCMember", back_populates="bids")
