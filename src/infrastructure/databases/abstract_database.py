from abc import ABC, abstractmethod
import psycopg2
from psycopg2 import sql
# from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import DevelopmentConfig,Config, FactoryConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
class AbstractDatabase(ABC):
    def __init__(self):
        self.database_uri = FactoryConfig.get_config("development").DATABASE_URI
        self.engine = create_engine(self.database_uri)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()
    @abstractmethod
    def init_database(app):
        pass