from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime


class CameraReadyModel(Base):
    """
    Camera-Ready submission model.
    Handles final version uploads for accepted papers.
    """
    __tablename__ = 'camera_ready'
    __table_args__ = (
        Index('idx_camera_ready_paper', 'paper_id'),
        Index('idx_camera_ready_status', 'status'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False, unique=True)
    
    # Final version files
    pdf_path = Column(String(500), nullable=True)
    source_files_path = Column(String(500), nullable=True)  # LaTeX/Word source
    supplementary_path = Column(String(500), nullable=True)
    
    # Copyright/agreement
    copyright_signed = Column(Boolean, default=False)
    copyright_signed_by = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    copyright_signed_at = Column(DateTime, nullable=True)
    copyright_form_path = Column(String(500), nullable=True)
    
    # Registration check
    registration_verified = Column(Boolean, default=False)
    registration_id = Column(String(100), nullable=True)
    
    # Final paper metadata
    final_title = Column(String(1000), nullable=True)  # May differ from submission
    final_abstract = Column(Text, nullable=True)
    final_authors = Column(Text, nullable=True)  # JSON string of final author list
    page_count = Column(Integer, nullable=True)
    
    # Formatting check
    format_check_status = Column(String(50), default='pending')  
    # pending, passed, failed, needs_revision
    format_check_comments = Column(Text, nullable=True)
    format_checked_by = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    format_checked_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), default='pending')  
    # pending, submitted, under_review, approved, revision_needed
    
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey('flask_user.id'), nullable=True)
    
    # Proceedings info
    proceedings_page_start = Column(Integer, nullable=True)
    proceedings_page_end = Column(Integer, nullable=True)
    doi = Column(String(255), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paper = relationship("PaperModel", back_populates="camera_ready")
