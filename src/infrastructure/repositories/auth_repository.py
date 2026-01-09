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
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.databases.mssql import session
from sqlalchemy.orm import Session
from infrastructure.models.auth.auth_user_model import AuthUserModel
from infrastructure.models.user_model import UserModel
load_dotenv()


class AuthRepository(IAuthRepository):
    def __init__(self, session: Session = session):
        self._users = []
        self._id_counter = 1
        self.session = db_factory.get_database('POSTGREE').session
    
    def login(self, auth: Auth) -> Auth:
        # Implement login logic here
        # For demonstration, we will just return the auth object
        selfed_user = self.session.query(AuthUserModel).filter_by(
            username=auth.username,
            password_hash=auth.password
        ).first()
        if not selfed_user:
            return None
        auth.id = selfed_user.id
        return auth
   
    def register(self, auth: Auth) -> Optional[Auth]:
        # Implement registration logic here
        # For demonstration, we will just return the auth object
        try:
            new_user = AuthUserModel(
                username=auth.username,
                password_hash=auth.password,
                email=auth.email
            )
            self.session.add(new_user)
            self.session.commit()
            self.session.refresh(new_user)
            auth.id = new_user.id
            return auth
        except Exception as e:
            self.session.rollback()
            return None
        finally:
            self.session.close()
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
    def check_exist(self, username: str) -> bool:
        # Implement check exist logic here
        existing_user = self.session.query(AuthUserModel).filter_by(username = username).first()
        if existing_user:
            return True
        return False
    

    

