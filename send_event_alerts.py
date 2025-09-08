import os
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import asyncio

# Add the project root to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.models import Base, Event, UserSession
from app.config import settings
from app.whatsapp_client import send_whatsapp_message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables are created
Base.metadata.create_all(bind=engine)

async def send_event_alerts():
    """Debug version with extensive logging"""
    logging.info("Starting event alert check...")
    db = SessionLocal()
    
    try:
        # Get all events first to see what's in the database
        all_events = db.query(Event).all()
        logging.info(f"Total events in database: {len(all_events)}")
        
        for event in all_events:
            logging.info(f"Event ID {event.id}: '{event.title}' - Date: {event.event_date} (naive UTC) - Alert sent: {event.is_alert_sent}")
        
        # Calculate tomorrow's date range
        now_utc = datetime.now(timezone.utc)
        logging.info(f"Current UTC time: {now_utc}")
        
        # Convert to Nairobi time to see what "today" and "tomorrow" are locally
        nairobi_tz = timezone(timedelta(hours=3))
        now_nairobi = now_utc.astimezone(nairobi_tz)
        logging.info(f"Current Nairobi time: {now_nairobi}")
        
        start_of_tomorrow = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day_after_tomorrow = start_of_tomorrow + timedelta(days=1)
        
        # Convert to naive for database comparison
        start_of_tomorrow_naive = start_of_tomorrow.replace(tzinfo=None)
        start_of_day_after_tomorrow_naive = start_of_day_after_tomorrow.replace(tzinfo=None)
        
        logging.info(f"Looking for events between:")
        logging.info(f"  Start: {start_of_tomorrow_naive} (naive UTC)")
        logging.info(f"  End: {start_of_day_after_tomorrow_naive} (naive UTC)")
        
        # Check each event against the range
        for event in all_events:
            in_range = (event.event_date >= start_of_tomorrow_naive and 
                        event.event_date < start_of_day_after_tomorrow_naive)
            alert_not_sent = not event.is_alert_sent
            
            logging.info(f"Event '{event.title}' ({event.event_date}):")
            logging.info(f"  In tomorrow's range: {in_range}")
            logging.info(f"  Alert not sent: {alert_not_sent}")
            logging.info(f"  Would be selected: {in_range and alert_not_sent}")
        
        # Your original query
        events_to_notify = db.query(Event).filter(
            Event.is_alert_sent == False,
            Event.event_date >= start_of_tomorrow_naive,
            Event.event_date < start_of_day_after_tomorrow_naive
        ).all()
        
        logging.info(f"Events found by query: {len(events_to_notify)}")
        
        if not events_to_notify:
            logging.info("No events scheduled for tomorrow that need alerts. Exiting.")
            return
            
        # Rest of your code...
        
    except Exception as e:
        logging.error(f"An error occurred during the event alert process: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

