from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from infrastructure.databases.base import Base
from datetime import datetime

class TenantModel(Base):
    __tablename__ = 'Tenant'
    __table_args__ = (
        Index('idx_name', 'Name'),
        {'extend_existing': True}
    )

    Tenant_ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(255), nullable=False)
    Email = Column(String(255))
    Created_at = Column(DateTime, default=datetime.utcnow)
    Updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    Active = Column(Boolean, default=True)
