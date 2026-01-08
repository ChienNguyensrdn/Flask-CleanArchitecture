from sqlalchemy import Column, Integer, String, DateTime, Boolean
from infrastructure.databases.base import Base

class UserModel(Base):
    __tablename__ = 'flask_user'
    # __table_args__ = {'extend_existing': True}  # Thêm dòng này

    id = Column(Integer, primary_key=True)
    username = Column(String(18), nullable=False,unique= True)
    password = Column(String(18), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime) 