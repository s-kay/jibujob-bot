import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
import sys
import asyncio
import pytz  # For robust timezone handling

# Add the project root to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.models import Base, Event, UserSession
from app.config import settings
# Import the template message sender
from app.whatsapp_client import send_template_message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables are created
Base.metadata.create_all(bind=engine)


async def send_event_alerts():
    """
    Checks for upcoming events and sends 'Heads-Up' (3 days before) and
    'Reminder' (1 day before) alerts to all users using WhatsApp templates.
    """
    logging.info("Starting event alert check...")
    db = SessionLocal()

    try:
        # 1. Get all real user phone numbers (excluding test users)
        all_users = db.query(UserSession.phone_number).filter(
            UserSession.phone_number.notlike('cli_%'),
            UserSession.phone_number.notlike('web-%')
        ).all()

        if not all_users:
            logging.info("No real users found to send alerts to. Exiting.")
            return

        phone_numbers = [user.phone_number for user in all_users]
        logging.info(f"Found {len(phone_numbers)} users to potentially notify.")

        now_utc = datetime.now(pytz.utc)
        eat_tz = pytz.timezone("Africa/Nairobi")

        # --- 2. Define time windows for alerts (calendar day based) ---
        three_days_from_now_start = (now_utc + timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        four_days_from_now_start = three_days_from_now_start + timedelta(days=1)

        one_day_from_now_start = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        two_days_from_now_start = one_day_from_now_start + timedelta(days=1)

        # --- 3. Find and send "Heads-Up" alerts (3 days out) ---
        logging.info(f"Checking for 'Heads-Up' alerts between {three_days_from_now_start.isoformat()} and {four_days_from_now_start.isoformat()}")
        heads_up_events = db.query(Event).filter(
            Event.heads_up_sent == False,
            Event.event_date >= three_days_from_now_start,
            Event.event_date < four_days_from_now_start
        ).all()

        for event in heads_up_events:
            logging.info(f"Found event for 'Heads-Up' alert: '{event.title}'")
            event_time_eat = event.event_date.astimezone(eat_tz)
            # Component parameters must be in the correct order for the template
            components = [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": event.title},
                    {"type": "text", "text": event.partner_name},
                    {"type": "text", "text": event_time_eat.strftime('%A, %B %d')}, # e.g., "Tuesday, September 09"
                ]
            }]
            for phone in phone_numbers:
                await send_template_message(phone, "event_heads_up_v1", components)

            event.heads_up_sent = True
            db.commit()
            logging.info(f"Heads-Up alert for event ID {event.id} sent and marked as complete.")

        # --- 4. Find and send "Reminder" alerts (1 day out) ---
        logging.info(f"Checking for 'Reminder' alerts between {one_day_from_now_start.isoformat()} and {two_days_from_now_start.isoformat()}")
        reminder_events = db.query(Event).filter(
            Event.reminder_sent == False,
            Event.event_date >= one_day_from_now_start,
            Event.event_date < two_days_from_now_start
        ).all()

        for event in reminder_events:
            logging.info(f"Found event for 'Reminder' alert: '{event.title}'")
            event_time_eat = event.event_date.astimezone(eat_tz)
            components = [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": event.title},
                    {"type": "text", "text": event.partner_name},
                    {"type": "text", "text": event_time_eat.strftime('%A, %B %d at %I:%M %p EAT')},
                    {"type": "text", "text": event.location},
                    {"type": "text", "text": event.description},
                ]
            }]
            for phone in phone_numbers:
                await send_template_message(phone, "event_reminder_v1", components)

            event.reminder_sent = True
            db.commit()
            logging.info(f"Reminder alert for event ID {event.id} sent and marked as complete.")

        logging.info("Event alert check finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the event alert process: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(send_event_alerts())

