"""Camera ready model for final paper versions."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class CameraReady(Base):
    """
    Camera-ready submission model.
    Stores final version of accepted papers.
    """
    __tablename__ = "camera_ready"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, unique=True)
    
    # Files
    pdf_path = Column(String(500), nullable=True)
    source_path = Column(String(500), nullable=True)  # LaTeX/Word source
    supplementary_path = Column(String(500), nullable=True)
    
    # Copyright
    copyright_signed = Column(Boolean, default=False)
    copyright_form_path = Column(String(500), nullable=True)
    
    # Metadata
    final_title = Column(String(1000), nullable=True)  # If changed from submission
    page_count = Column(Integer, nullable=True)
    
    # Status
    is_submitted = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    
    # Feedback
    chair_notes = Column(Text, nullable=True)
    revision_requested = Column(Boolean, default=False)
    
    # Timestamps
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paper = relationship("Paper", back_populates="camera_ready")
