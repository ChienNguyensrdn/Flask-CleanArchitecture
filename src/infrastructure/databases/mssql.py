from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from config import Config
from infrastructure.databases.base import Base
import time
import logging

logger = logging.getLogger(__name__)

# Database configuration - initialized in init_mssql
engine = None
SessionLocal = None
_scoped_session = None


def get_session():
    """
    Get a new database session.
    Each caller should close the session when done.
    
    Usage:
        session = get_session()
        try:
            # use session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_mssql first.")
    return SessionLocal()


def get_scoped_session():
    """
    Get a thread-local scoped session.
    Useful for web requests where you want one session per request.
    """
    if _scoped_session is None:
        raise RuntimeError("Database not initialized. Call init_mssql first.")
    return _scoped_session


class SessionManager:
    """Context manager for database sessions"""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        self.session = get_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        self.session.close()
        return False


def init_mssql(app):
    global engine, SessionLocal, _scoped_session
    DATABASE_URI = Config.DATABASE_URI
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting database connection (attempt {retry_count + 1}/{max_retries})...")
            
            # Mask password in log output
            safe_uri = DATABASE_URI
            if '@' in DATABASE_URI:
                parts = DATABASE_URI.split('@')
                safe_uri = parts[0].rsplit(':', 1)[0] + ':****@' + parts[1]
            logger.info(f"Connecting to database: {safe_uri}")
            
            engine = create_engine(
                DATABASE_URI, 
                echo=False, 
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600  # Recycle connections after 1 hour
            )
            
            # Test connection
            with engine.connect() as conn:
                logger.info("Database connection successful!")
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            _scoped_session = scoped_session(SessionLocal)
            
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully!")
            return
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"Connection failed: {str(e)[:100]}...")
                logger.info(f"Retrying in 3 seconds...")
                time.sleep(3)
            else:
                logger.error(f"Database initialization failed after {max_retries} attempts: {e}")
                raise


def cleanup_session():
    """Clean up scoped session - call at end of request"""
    if _scoped_session:
        _scoped_session.remove()


# Legacy support - deprecated, use get_session() instead
session = None

def _init_legacy_session():
    """Initialize legacy global session for backward compatibility"""
    global session
    if SessionLocal:
        session = SessionLocal()
        import warnings
        warnings.warn(
            "Using global 'session' is deprecated. Use get_session() instead.",
            DeprecationWarning
        )