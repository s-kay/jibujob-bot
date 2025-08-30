import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, attributes
from app import models
from app.config import settings

def get_or_create_session(db: Session, phone_number: str, user_name: str) -> tuple[models.UserSession, bool]:
    """
    Retrieves a user's session from the database or creates a new one.
    Also checks if the session has expired and resets it if necessary.
    Returns the session object and a boolean indicating if it's a new user.
    """
    session = db.query(models.UserSession).filter(models.UserSession.phone_number == phone_number).first()
    is_new = False

    if session:
        # Check for session expiration
        session_timeout = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        
        # Make the database timestamp timezone-aware before comparison
        last_active_aware = session.last_active.replace(tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)

        if now_utc - last_active_aware > session_timeout:
            logging.info(f"Session for {phone_number} expired. Resetting menu.")
            session.current_menu = "main"
            session.session_data = {}
            # We don't reset their long-term interests here, just the temp state.
    else:
        logging.info(f"New user session created for {phone_number}")
        session = models.UserSession(
            phone_number=phone_number,
            user_name=user_name,
            # Explicitly set default values for optional JSON fields
            resume_data={},
            interview_data={},
            cover_letter_data={},
            session_data={}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        is_new = True
    
    return session, is_new

def update_session(db: Session, session: models.UserSession):
    """
    Flags the session data as modified before committing.
    This is crucial for making sure changes to JSON fields are saved.
    """
    attributes.flag_modified(session, "session_data")
    attributes.flag_modified(session, "resume_data")
    attributes.flag_modified(session, "interview_data")
    attributes.flag_modified(session, "cover_letter_data")
    db.commit()

def save_feedback(db: Session, user_phone_number: str, feedback_data: dict):
    """Saves a user's feedback to the database."""
    if not feedback_data:
        return
    
    # Explicitly map dictionary keys to model attributes for robustness
    new_feedback = models.Feedback(
        user_phone_number=user_phone_number,
        likes=feedback_data.get("likes"),
        dislikes=feedback_data.get("dislikes"),
        suggestions=feedback_data.get("suggestions"),
        rating=feedback_data.get("rating")
    )
    
    db.add(new_feedback)
    db.commit()
    logging.info(f"Feedback saved for user {user_phone_number}")

