from sqlalchemy import Integer, String, JSON, DateTime, func, ForeignKey, Boolean
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

    # --- Feature Data ---
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
    feedbacks: Mapped[List["Feedback"]] = relationship(back_populates="user")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_phone_number: Mapped[str] = mapped_column(String, ForeignKey("user_sessions.phone_number"), index=True)
    
    likes: Mapped[Optional[str]] = mapped_column(String)
    dislikes: Mapped[Optional[str]] = mapped_column(String)
    suggestions: Mapped[Optional[str]] = mapped_column(String)
    rating: Mapped[Optional[int]] = mapped_column(Integer)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["UserSession"] = relationship(back_populates="feedbacks")

# --- NEW TABLE FOR TVET EVENT ALERTS ---
class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str] = mapped_column(String, default="Online")
    partner_name: Mapped[str] = mapped_column(String, nullable=False)
    heads_up_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

