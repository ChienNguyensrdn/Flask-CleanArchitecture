"""User model for authentication and authorization."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"           # Site administrator
    CHAIR = "chair"           # Conference/Program chair
    PC_MEMBER = "pc_member"   # Program committee member/reviewer
    AUTHOR = "author"         # Paper author
    

class User(Base):
    """
    User model for all system users.
    Supports multiple roles and multi-tenancy.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    affiliation = Column(String(255), nullable=True)  # University/Organization
    country = Column(String(100), nullable=True)
    orcid = Column(String(50), nullable=True)  # ORCID identifier
    
    # Role and status
    role = Column(SQLEnum(UserRole), default=UserRole.AUTHOR)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # SSO support
    sso_provider = Column(String(50), nullable=True)  # google, microsoft, etc.
    sso_id = Column(String(255), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    submitted_papers = relationship("Paper", back_populates="submitter", foreign_keys="Paper.submitter_id")
    authored_papers = relationship("PaperAuthor", back_populates="user")
    pc_memberships = relationship("PCMember", back_populates="user")
    reviews = relationship("Review", back_populates="reviewer")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
