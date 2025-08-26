# app/crud.py
from sqlalchemy.orm import Session
from . import models
import time
from datetime import datetime, timedelta
from .config import settings

def get_or_create_session(db: Session, phone_number: str, user_name: str) -> models.UserSession:
    """
    Retrieves an existing user session or creates a new one.
    Also handles session expiration logic.
    """
    session = db.query(models.UserSession).filter(models.UserSession.phone_number == phone_number).first()

    if session:
        # Check if the session has expired
        session_timeout = timedelta(seconds=settings.SESSION_TIMEOUT)
        if datetime.utcnow() - session.last_active.replace(tzinfo=None) > session_timeout:
            # Session expired, reset its state
            session.current_menu = "main"
            session.session_data = {}
            db.commit()
            db.refresh(session)
    else:
        # Create a new session for a new user
        session = models.UserSession(phone_number=phone_number, user_name=user_name)
        db.add(session)
        db.commit()
        db.refresh(session)
        
    return session

def update_session(db: Session, session: models.UserSession):
    """
    Commits changes made to a session object to the database.
    """
    db.commit()
    db.refresh(session)
