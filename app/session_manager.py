from contextlib import contextmanager
from sqlalchemy import select
from db import SessionLocal
from models import UserSession, Base
from sqlalchemy.orm import Session
from app.models import UserSession
from app.db import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()

def get_or_create_session(user_id: str) -> UserSession:
    with db_session() as db:
        sess = db.execute(select(UserSession).where(UserSession.user_id == user_id)).scalar_one_or_none()
        if not sess:
            sess = UserSession(user_id=user_id, state="start", data={})
            db.add(sess)
            db.flush()
        return sess

def save_session(sess: UserSession, *, state: str | None = None, data: dict | None = None) -> UserSession:
    with db_session() as db:
        s = db.merge(sess)
        if state is not None:
            s.state = state
        if data is not None:
            s.data  = data
        return s
    
def get_user_session(user_id: str) -> UserSession | None:
    db: Session = SessionLocal()
    return db.query(UserSession).filter(UserSession.user_id == user_id).first()

def update_user_session(user_id: str, state: str, last_message: str):
    db: Session = SessionLocal()
    session = db.query(UserSession).filter(UserSession.user_id == user_id).first()
    if not session:
        session = UserSession(user_id=user_id, state=state, last_message=last_message)
        db.add(session)
    else:
        session.state = state
        session.last_message = last_message
    db.commit()
    db.refresh(session)
    return session    
