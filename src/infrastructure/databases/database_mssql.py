

from infrastructure.databases.abstract_database import AbstractDatabase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from infrastructure.databases.base import Base
class DatabaseMSSQL(AbstractDatabase):
    def __innit__(self):
        super().__init__()
        
    def init_database(self, app):
        Base.metadata.create_all(bind=self.engine)