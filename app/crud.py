# app/crud.py
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import Dict, Any, Tuple

from . import models
from .config import settings

# --- NEW FUNCTION TO SAVE FEEDBACK ---
def save_feedback(db: Session, user_phone_number: str, feedback_data: Dict[str, Any]):
    """
    Creates a new feedback record and saves it to the database.
    """
    new_feedback = models.Feedback(
        user_phone_number=user_phone_number,
        rating=feedback_data.get("rating"),
        what_liked=feedback_data.get("what_liked"),
        what_confusing=feedback_data.get("what_confusing"),
        feature_requests=feedback_data.get("feature_requests")
    )
    db.add(new_feedback)
    db.commit()
    logging.info(f"Feedback saved for user {user_phone_number}")

def get_or_create_session(db: Session, phone_number: str, user_name: str) -> Tuple[models.UserSession, bool]:
    """
    Retrieves an existing user session or creates a new one.
    Also returns a boolean indicating if the user is new.
    """
    session = db.query(models.UserSession).filter(models.UserSession.phone_number == phone_number).first()
    is_new = False

    if session:
        # Check for session timeout
        session_timeout = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        
        # Ensure last_active has a timezone before comparing
        last_active_aware = session.last_active.replace(tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)

        if now_utc - last_active_aware > session_timeout:
            logging.info(f"Session expired for {phone_number}, resetting menu.")
            session.current_menu = "main"
            session.session_data = {} # Reset temporary state, but keep preferences
    else:
        logging.info(f"New user session created for {phone_number}")
        session = models.UserSession(phone_number=phone_number, user_name=user_name)
        db.add(session)
        db.commit()
        db.refresh(session)
        is_new = True
    
    return session, is_new

def update_session(db: Session, session: models.UserSession):
    """
    Commits any changes made to the session object to the database.
    This is crucial for persisting the conversation state.
    """
    # Explicitly flag JSON fields as modified to ensure they are saved.
    flag_modified(session, "session_data")
    flag_modified(session, "resume_data")
    flag_modified(session, "interview_data")
    flag_modified(session, "cover_letter_data")

    db.add(session)
    db.commit()
    db.refresh(session)

