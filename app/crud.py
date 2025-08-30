import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, attributes
from app import models
from app.config import settings

def get_or_create_session(db: Session, phone_number: str, user_name: str) -> tuple[models.UserSession, bool]:
    """
    Retrieves an existing user session or creates a new one.
    Also returns a boolean indicating if the session is new.
    """
    session = db.query(models.UserSession).filter(models.UserSession.phone_number == phone_number).first()
    is_new = False

    if session:
        # Check for session timeout
        session_timeout = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        now_utc = datetime.now(timezone.utc)
        
        last_active_aware = session.last_active.replace(tzinfo=timezone.utc)

        if now_utc - last_active_aware > session_timeout:
            logging.info(f"Session for {phone_number} expired. Resetting menu.")
            session.current_menu = "main"
            session.session_data = {}
    else:
        logging.info(f"New user session created for {phone_number}")
        # We no longer pass feedback_data here
        session = models.UserSession(
            phone_number=phone_number,
            user_name=user_name,
            current_menu="main",
            session_data={},
            resume_data={},
            cover_letter_data={},
            interview_data={}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        is_new = True
        
    return session, is_new

def update_session(db: Session, session: models.UserSession):
    """
    Marks session_data as modified to ensure changes are persisted.
    """
    attributes.flag_modified(session, "session_data")
    attributes.flag_modified(session, "resume_data")
    attributes.flag_modified(session, "cover_letter_data")
    attributes.flag_modified(session, "interview_data")
    # We no longer flag feedback_data here
    db.commit()

def save_feedback(db: Session, user_phone_number: str, feedback_data: dict):
    """Saves user feedback to the database."""
    user_session = db.query(models.UserSession).filter(models.UserSession.phone_number == user_phone_number).first()
    if user_session:
        new_feedback = models.Feedback(
            rating=feedback_data.get("rating"),
            likes=feedback_data.get("likes"),
            dislikes=feedback_data.get("dislikes"),
            suggestions=feedback_data.get("suggestions"),
            user_session_id=user_session.id
        )
        db.add(new_feedback)
        db.commit()
        logging.info(f"Feedback saved for user {user_phone_number}")

