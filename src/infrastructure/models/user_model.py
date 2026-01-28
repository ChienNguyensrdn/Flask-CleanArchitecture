from sqlalchemy import Column, Integer, String, DateTime, Boolean
from infrastructure.databases.base import Base
from werkzeug.security import generate_password_hash, check_password_hash


class UserModel(Base):
    __tablename__ = 'flask_user'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_name = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)  # Stores hashed password
    description = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def set_password(self, password: str):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password) 