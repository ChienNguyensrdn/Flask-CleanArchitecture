"""User repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.user_model import UserModel
from infrastructure.databases.mssql import get_session


class UserRepository:
    """Repository for managing User database operations."""
    
    def __init__(self, session: Session = None):
        self._session = session
    
    @property
    def session(self):
        """Get session - use provided session or create new one."""
        if self._session:
            return self._session
        return get_session()
    
    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """Get user by ID."""
        return self.session.query(UserModel).filter(
            UserModel.id == user_id
        ).first()
    
    def get_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username."""
        return self.session.query(UserModel).filter(
            UserModel.user_name == username
        ).first()
    
    def list_all(self) -> List[UserModel]:
        """Get all users."""
        return self.session.query(UserModel).all()
    
    def create(self, user_data: dict) -> UserModel:
        """Create a new user."""
        user = UserModel(
            user_name=user_data['user_name'],
            description=user_data.get('description'),
            status=user_data.get('status', True),
            created_at=user_data.get('created_at'),
            updated_at=user_data.get('updated_at')
        )
        user.set_password(user_data['password'])
        
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def update(self, user_id: int, user_data: dict) -> Optional[UserModel]:
        """Update user."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        if 'user_name' in user_data:
            user.user_name = user_data['user_name']
        if 'description' in user_data:
            user.description = user_data['description']
        if 'status' in user_data:
            user.status = user_data['status']
        if 'password' in user_data:
            user.set_password(user_data['password'])
        if 'updated_at' in user_data:
            user.updated_at = user_data['updated_at']
        
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.session.delete(user)
        self.session.commit()
        return True