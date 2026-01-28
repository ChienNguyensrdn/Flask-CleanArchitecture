"""User schemas for API requests/responses."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    affiliation: Optional[str] = None
    country: Optional[str] = None
    orcid: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)
    tenant_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    affiliation: Optional[str] = None
    country: Optional[str] = None
    orcid: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    tenant_id: Optional[int]
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: int  # user_id
    exp: datetime
    type: str  # "access" or "refresh"
