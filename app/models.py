# app/models.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from .database import Base

class UserSession(Base):
    """
    SQLAlchemy model for storing user session data.
    This replaces the in-memory dictionary.
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    user_name = Column(String, nullable=True)
    
    # Stores the user's current menu location (e.g., "main", "jobs", "training")
    current_menu = Column(String, default="main")
    
    # A JSON field to store all dynamic state information
    # e.g., {"awaiting_job_role": true, "job_interest": "developer"}
    session_data = Column(JSON, default={})
    
    # Timestamps for session management
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

