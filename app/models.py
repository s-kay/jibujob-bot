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
    
    job_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    training_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mentorship_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    entrepreneurship_interest: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    resume_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    interview_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    cover_letter_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    current_menu: Mapped[str] = mapped_column(String, default="main")
    session_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str] = mapped_column(String, default="Online")
    partner_name: Mapped[str] = mapped_column(String)
    
    # THE FIX IS HERE: The old `is_alert_sent` column has been removed.
    heads_up_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# --- NEW TABLE FOR THE PARTNER DASHBOARD ---
class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    partner_name: Mapped[str] = mapped_column(String, nullable=False) # e.g., "Kabete National Polytechnic"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)    

