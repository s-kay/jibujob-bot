# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from . import models
from datetime import datetime, timedelta, timezone
from typing import Tuple

from .config import settings

def get_or_create_session(db: Session, phone_number: str, user_name: str) -> Tuple[models.UserSession, bool]:
    """
    Retrieves an existing user session or creates a new one.
    Returns the session object and a boolean indicating if the user is new.
    """
    session = db.query(models.UserSession).filter(models.UserSession.phone_number == phone_number).first()
    is_new = False

    if session:
        session_timeout = timedelta(seconds=settings.SESSION_TIMEOUT)
        now_utc = datetime.now(timezone.utc)
        last_active_aware = session.last_active.replace(tzinfo=timezone.utc)
        
        if now_utc - last_active_aware > session_timeout:
            # Session expired: Reset temporary state but keep interests.
            session.current_menu = "main"
            session.session_data = {}
            # We commit the reset here immediately
            db.commit()
            db.refresh(session)
    else:
        is_new = True
        session = models.UserSession(phone_number=phone_number, user_name=user_name)
        db.add(session)
        db.commit()
        db.refresh(session)
        
    return session, is_new

def update_session(db: Session, session: models.UserSession):
    """
    Commits changes made to a session object to the database.
    Flags all JSON fields as modified to ensure changes are saved.
    """
    # These lines are crucial. They explicitly tell the database that the
    # content inside our JSON fields may have changed and needs to be saved.
    flag_modified(session, "session_data")
    flag_modified(session, "resume_data")
    flag_modified(session, "interview_data")
    flag_modified(session, "cover_letter_data")
    
    db.commit()
    db.refresh(session)
