# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Create the SQLAlchemy engine using the URL from settings.
# The SQLite-specific connect_args have been removed to support PostgreSQL.
engine = create_engine(
    settings.DATABASE_URL
)

# Each instance of SessionLocal will be a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy models to inherit from
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session for each request.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
