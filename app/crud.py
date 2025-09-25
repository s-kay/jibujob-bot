import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, attributes
from sqlalchemy import inspect
from app import models
from app.config import settings
from typing import List, Dict, Any, Set

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
    Flags mutable fields as modified before committing.
    This version is more robust and checks if attributes are present.
    """
    # Use SQLAlchemy's inspect utility to get the object's state
    ins = inspect(session)
    
    # flag attributes that are actually loaded in the session's state.
    if 'session_data' in ins.attrs and session.session_data is not None:
        attributes.flag_modified(session, "session_data")
    if 'resume_data' in ins.attrs and session.resume_data is not None:
        attributes.flag_modified(session, "resume_data")
    if 'interview_data' in ins.attrs and session.interview_data is not None:
        attributes.flag_modified(session, "interview_data")
    if 'cover_letter_data' in ins.attrs and session.cover_letter_data is not None:
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

# --- NEW FUNCTION FOR PARTNER AUTHENTICATION ---
def get_partner_by_username(db: Session, username: str) -> models.Partner | None:
    """Fetches a partner from the database by their username."""
    return db.query(models.Partner).filter(models.Partner.username == username).first()    


# --- CRUD FUNCTIONS FOR THE DASHBOARD ---

def get_events_by_partner(db: Session, partner_id: int) -> List[models.Event]:
    """Fetches all events for a specific partner."""
    return db.query(models.Event).filter(models.Event.partner_id == partner_id).order_by(models.Event.event_date.desc()).all()

def create_event(db: Session, event_data: Dict[str, Any], partner: models.Partner) -> models.Event:
    """Creates a new event for a partner."""
    new_event = models.Event(
        title=event_data["title"],
        description=event_data["description"],
        event_date=datetime.fromisoformat(event_data["date"]),
        location=event_data["location"],
        partner_name=partner.partner_name,
        partner_id=partner.id
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def delete_event(db: Session, event_id: int, partner_id: int) -> bool:
    """Deletes an event, ensuring it belongs to the correct partner."""
    event_to_delete = db.query(models.Event).filter(models.Event.id == event_id, models.Event.partner_id == partner_id).first()
    if event_to_delete:
        db.delete(event_to_delete)
        db.commit()
        return True
    return False

def get_featured_jobs_by_partner(db: Session, partner_id: int) -> List[models.FeaturedJob]:
    """Fetches all featured jobs for a specific partner."""
    return db.query(models.FeaturedJob).filter(models.FeaturedJob.partner_id == partner_id).order_by(models.FeaturedJob.created_at.desc()).all()

def get_featured_job_by_id(db: Session, job_id: int) -> models.FeaturedJob | None:
    """Fetches a single featured job by its unique ID."""
    return db.query(models.FeaturedJob).filter(models.FeaturedJob.id == job_id).first()

def create_featured_job(db: Session, job_data: Dict[str, Any], partner: models.Partner) -> models.FeaturedJob:
    """Creates a new featured job for a partner."""
    new_job = models.FeaturedJob(
        title=job_data["title"],
        description=job_data["description"],
        keywords=job_data["keywords"],
        link=job_data["link"],
        partner_name=partner.partner_name,
        partner_id=partner.id
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

def delete_featured_job(db: Session, job_id: int, partner_id: int) -> bool:
    """Deletes a featured job, ensuring it belongs to the correct partner."""
    job_to_delete = db.query(models.FeaturedJob).filter(models.FeaturedJob.id == job_id, models.FeaturedJob.partner_id == partner_id).first()
    if job_to_delete:
        db.delete(job_to_delete)
        db.commit()
        return True
    return False

# --- THE SMART ALERT SYSTEM ---

def get_sent_job_links_for_user(db: Session, user_phone_number: str) -> Set[str]:
    """
    Retrieves a set of all job links that have already been sent to a user.
    Using a set provides a fast O(1) average time complexity for checking existence.
    """
    alerts = db.query(models.SentJobAlert.job_link).filter(models.SentJobAlert.user_phone_number == user_phone_number).all()
    return {alert[0] for alert in alerts}

def mark_job_as_sent(db: Session, user_phone_number: str, job_link: str):
    """
    Records that a specific job alert has been sent to a user.
    """
    new_alert = models.SentJobAlert(
        user_phone_number=user_phone_number,
        job_link=job_link
    )
    db.add(new_alert)
    # The commit will happen in the main alert script after all users are processed.
