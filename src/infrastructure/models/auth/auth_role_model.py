from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from infrastructure.databases.base import Base
class AuthRoleModel(Base):
    __tablename__ = 'auth_roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
class AuthUserRoleModel(Base):
    __tablename__ = 'auth_user_roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('auth_users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('auth_roles.id'), nullable=False)

    def __repr__(self):
        return f"<AuthUserRoleModel(user_id='{self.user_id}', role_id='{self.role_id}')>"