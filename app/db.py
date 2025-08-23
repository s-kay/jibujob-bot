from sqlalchemy import create_engine, text
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, future=True)

def init_db():
    with engine.begin() as conn:
        # Minimal phase-1 schema (can extend later)
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender TEXT,
            message TEXT,
            direction TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """))
