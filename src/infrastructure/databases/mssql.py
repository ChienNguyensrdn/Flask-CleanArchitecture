from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from config import Config
from infrastructure.databases.base import Base
import time

# Database configuration - initialized in init_mssql
engine = None
SessionLocal = None
session = None

def init_mssql(app):
    global engine, SessionLocal, session
    DATABASE_URI = Config.DATABASE_URI
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempting database connection (attempt {retry_count + 1}/{max_retries})...")
            print(f"Connecting to database: {DATABASE_URI}")
            
            engine = create_engine(DATABASE_URI, echo=False, pool_pre_ping=True)
            
            # Test connection
            with engine.connect() as conn:
                print("Database connection successful!")
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            session = SessionLocal()
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully!")
            return
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"Connection failed: {str(e)[:100]}...")
                print(f"Retrying in 3 seconds...")
                time.sleep(3)
            else:
                print(f"Database initialization failed after {max_retries} attempts: {e}")
                raise