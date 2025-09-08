import os
import logging
import sys
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add timeout to prevent hanging
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Script timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)  # 60 second timeout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from app.models import Base, Event, UserSession
    from app.config import settings
    logging.info("Imports successful")
    
    # Test database connection
    engine = create_engine(settings.DATABASE_URL, pool_timeout=10, pool_recycle=3600)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logging.info("Database connection created")
    
    def send_event_alerts_sync():
        """Synchronous version to avoid async issues"""
        logging.info("Starting event alert check...")
        db = SessionLocal()
        
        try:
            # Quick test query
            event_count = db.query(Event).count()
            logging.info(f"Total events in database: {event_count}")
            
            if event_count == 0:
                logging.info("No events in database")
                return
                
            # Get first event for testing
            first_event = db.query(Event).first()
            if first_event:
                logging.info(f"First event: ID={first_event.id}, Title={first_event.title}, Date={first_event.event_date}")
            
            # Simple date check
            now_utc = datetime.now(timezone.utc)
            logging.info(f"Current UTC time: {now_utc}")
            
            tomorrow = now_utc.date() + timedelta(days=1)
            logging.info(f"Tomorrow's date: {tomorrow}")
            
            # Check for tomorrow's events (simple version)
            tomorrow_events = db.query(Event).filter(
                Event.event_date >= datetime.combine(tomorrow, datetime.min.time()),
                Event.event_date < datetime.combine(tomorrow + timedelta(days=1), datetime.min.time()),
                Event.is_alert_sent == False
            ).all()
            
            logging.info(f"Events found for tomorrow: {len(tomorrow_events)}")
            for event in tomorrow_events:
                logging.info(f"Tomorrow event: {event.title} at {event.event_date}")
            
        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
        finally:
            db.close()
            logging.info("Database connection closed")
    
    # Run the function
    send_event_alerts_sync()
    logging.info("Script completed successfully")
    
except Exception as e:
    logging.error(f"Script failed: {e}", exc_info=True)
finally:
    signal.alarm(0)  # Cancel the alarm