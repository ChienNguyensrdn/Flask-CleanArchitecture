"""Paper author model for co-author management."""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class PaperAuthor(Base):
    """
    Paper author model for managing co-authors.
    Supports both registered and external authors.
    """
    __tablename__ = "paper_authors"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for external authors
    
    # Author order
    order = Column(Integer, nullable=False, default=1)
    is_corresponding = Column(Boolean, default=False)
    
    # For external authors (not registered)
    email = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    affiliation = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Relationships
    paper = relationship("Paper", back_populates="authors")
    user = relationship("User", back_populates="authored_papers")
    
    @property
    def full_name(self) -> str:
        if self.user:
            return self.user.full_name
        return f"{self.first_name} {self.last_name}"
    
    @property
    def author_email(self) -> str:
        if self.user:
            return self.user.email
        return self.email
