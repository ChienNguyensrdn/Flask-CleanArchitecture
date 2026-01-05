from domain.models.iauth_repository import IAuthRepository
from domain.models.auth import Auth
from infrastructure.databases import Base
from typing import List, Optional
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config
from sqlalchemy import Column, Integer, String, DateTime
from infrastructure.databases.mssql import session
from sqlalchemy.orm import Session
from infrastructure.models.user_model import UserModel
load_dotenv()

class AuthRepository(IAuthRepository):
    def __init__(self, session: Session = session):
        self._users = []
        self._id_counter = 1
        self.session = session
    
    def login(self, auth: Auth) -> Auth:
        # Implement login logic here
        # For demonstration, we will just return the auth object
        return auth
    def register(self, auth: Auth) -> Optional[Auth]:
        # Implement registration logic here
        # For demonstration, we will just return the auth object
        auth.id = 1  # Simulate setting an ID after registration
        return auth
    def remember_password(self) -> Optional[Auth]:
        # Implement remember password logic here
        return None
    def look_account(self, Id: int) -> bool:
        # Implement look account logic here
        return True
    def un_look_account(self, course_id: int) -> None:
        # Implement un-look account logic here
        pass
    def check_exist(self, user_name: str) -> bool:
        # Implement check exist logic here
        existing_user = self.session.query(UserModel).filter_by(user_name = user_name).first()
        if existing_user:
            return False
        return True
    

    

