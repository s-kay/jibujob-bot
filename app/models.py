from sqlalchemy import Integer, String, JSON, DateTime, func, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Dict, Any, Optional, List

from .database import Base

class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=True)
    
    # --- Long-Term Preferences ---
    job_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    training_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mentorship_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    entrepreneurship_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # --- Feature-Specific Data ---
    resume_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    interview_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    cover_letter_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # --- Session State ---
    current_menu: Mapped[str] = mapped_column(String, default="main")
    session_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    
    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # --- Relationship to Feedback ---
    feedbacks: Mapped[List["Feedback"]] = relationship(back_populates="user_session")


# --- NEW FEEDBACK TABLE ---
class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign key to link to the UserSession table
    user_phone_number: Mapped[str] = mapped_column(String, ForeignKey("user_sessions.phone_number"))
    
    # The actual feedback content
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    what_liked: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    what_confusing: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feature_requests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship back to UserSession
    user_session: Mapped["UserSession"] = relationship(back_populates="feedbacks")

