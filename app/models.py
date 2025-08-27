# app/models.py
from sqlalchemy import Integer, String, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Dict, Any, Optional

from .database import Base

class UserSession(Base):
    """
    SQLAlchemy model for storing user session data.

    Now includes a dedicated JSON field for the cover letter generator.
    """
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=True)
    
    # --- Long-Term Preferences ---
    job_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    training_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mentorship_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    entrepreneurship_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # --- Feature Data ---
    resume_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    interview_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    cover_letter_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    # --- Session State ---
    current_menu: Mapped[str] = mapped_column(String, default="main")
    session_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    
    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
