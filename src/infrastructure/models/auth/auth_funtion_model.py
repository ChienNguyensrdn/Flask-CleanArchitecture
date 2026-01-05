from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from infrastructure.databases.base import Base
class AuthFuntionModel(Base):
    __tablename__ = 'auth_functions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    url = Column(String(255), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    
class AuthRoleFunctionModel(Base):
    __tablename__ = 'auth_role_functions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('auth_roles.id'), nullable=False)
    function_id = Column(Integer, ForeignKey('auth_functions.id'), nullable=False)

    def __repr__(self):
        return f"<AuthRoleFunctionModel(role_id='{self.role_id}', function_id='{self.function_id}')>"   