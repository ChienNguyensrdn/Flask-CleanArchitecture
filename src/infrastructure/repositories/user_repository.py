from domain.models.itodo_repository import ITodoRepository
from domain.models.todo import Todo
from typing import List, Optional
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config
from sqlalchemy import Column, Integer, String, DateTime,Boolean
from infrastructure.databases import Base

load_dotenv()

class UserModel(Base):
    __tablename__ = 'flask_user'
    __table_args__ = {'extend_existing': True}  # Thêm dòng này

    id = Column(Integer, primary_key=True)
    username = Column(String(18), nullable=False)
    password = Column(String(18), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime) 
    