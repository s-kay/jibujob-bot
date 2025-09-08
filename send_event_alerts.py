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
    """
    Checks for upcoming events and sends a 'Reminder' alert (1 day before) to all users.
    This version uses a robust, calendar-day-based check.
    """
    logging.info("Starting event alert check...")
    db = SessionLocal()
    
    try:
        # 1. Get all real user phone numbers
        all_users = db.query(UserSession.phone_number).filter(
            UserSession.phone_number.notlike('cli_%'),
            UserSession.phone_number.notlike('web-%')
        ).all()
        
        if not all_users:
            logging.info("No real users found to send alerts to. Exiting.")
            return
            
        phone_numbers = [user.phone_number for user in all_users]
        logging.info(f"Found {len(phone_numbers)} users to potentially notify.")

        # --- THE FIX: A more robust way to calculate "tomorrow" ---
        now_utc = datetime.now(timezone.utc)
        
        # Calculate the start of tomorrow in UTC
        start_of_tomorrow = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate the start of the day after tomorrow in UTC
        start_of_day_after_tomorrow = start_of_tomorrow + timedelta(days=1)
        
        logging.info(f"Checking for events between {start_of_tomorrow.isoformat()} and {start_of_day_after_tomorrow.isoformat()}")

        # 3. Find events happening anytime tomorrow that have NOT had an alert sent yet
        events_to_notify = db.query(Event).filter(
            Event.is_alert_sent == False,
            Event.event_date >= start_of_tomorrow,
            Event.event_date < start_of_day_after_tomorrow
        ).all()
        
        if not events_to_notify:
            logging.info("No events scheduled for tomorrow that need alerts. Exiting.")
            return

        # 4. For each event, format and send the alert to all users
        for event in events_to_notify:
            logging.info(f"Found event for 'Reminder' alert: '{event.title}'")
            # Convert event time to EAT for the message
            event_time_eat = event.event_date.astimezone(timezone(timedelta(hours=3)))
            
            message = (
                f"❗ Don't Forget! The *{event.title}* is tomorrow!\n\n"
                f"Hosted by *{event.partner_name}*.\n"
                f"🗓️ When: {event_time_eat.strftime('%A, %B %d at %I:%M %p EAT')}\n"
                f"📍 Where: {event.location}\n\n"
                f"Description: {event.description}\n\n"
                f"This is a great opportunity. Hope to see you there!"
            )
            
            for phone in phone_numbers:
                await send_whatsapp_message(phone, message)
            
            # 5. Mark the event as "sent" so we don't send this alert again
            event.is_alert_sent = True
            db.add(event)
            db.commit()
            logging.info(f"Reminder for event ID {event.id} ('{event.title}') sent and marked as complete.")
            
        logging.info("Event alert check finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the event alert process: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(send_event_alerts())

