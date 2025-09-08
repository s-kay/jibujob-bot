import argparse
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.models import Base, Event
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- Timezone Definitions ---
# THE FIX: We use Python's built-in timezone objects for consistency.
UTC_TZ = timezone.utc
EAT_TZ = timezone(timedelta(hours=3), 'EAT')


def add_event(args):
    """Adds a new event to the database, converting the date to UTC."""
    db = SessionLocal()
    try:
        # 1. Parse the naive datetime string from the user's input
        naive_event_date = datetime.fromisoformat(args.date)
        
        # 2. Assume the user's input is in EAT and make it timezone-aware
        aware_event_date_eat = naive_event_date.replace(tzinfo=EAT_TZ)
        
        # 3. Convert the EAT datetime to UTC for storage
        event_date_utc = aware_event_date_eat.astimezone(UTC_TZ)

        logging.info(f"Received date {args.date} (EAT), converting to {event_date_utc.isoformat()} (UTC) for storage.")

        new_event = Event(
            title=args.title,
            description=args.description,
            event_date=event_date_utc,
            location=args.location,
            partner_name=args.partner
        )
        db.add(new_event)
        db.commit()
        logging.info(f"Successfully added event: '{args.title}'")
    except Exception as e:
        logging.error(f"Failed to add event: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

def list_events(args):
    """Lists all upcoming events from the database."""
    db = SessionLocal()
    try:
        events = db.query(Event).order_by(Event.event_date.asc()).all()
        if not events:
            print("No events found in the database.")
            return

        print("\n--- Upcoming Events ---")
        for event in events:
            # THE FIX: Convert the stored UTC time back to EAT for display
            display_time = event.event_date.astimezone(EAT_TZ)
            print(f"  ID: {event.id}")
            print(f"  Title: {event.title}")
            print(f"  Partner: {event.partner_name}")
            print(f"  Date (EAT): {display_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Location: {event.location}")
            print(f"  Description: {event.description}")
            print(f"  Alert Sent: {'Yes' if event.is_alert_sent else 'No'}")
            print("-" * 20)
    finally:
        db.close()

def delete_event(args):
    """Deletes an event by its ID."""
    db = SessionLocal()
    try:
        event_to_delete = db.query(Event).filter(Event.id == args.id).first()
        if event_to_delete:
            db.delete(event_to_delete)
            db.commit()
            logging.info(f"Successfully deleted event with ID: {args.id}")
        else:
            logging.error(f"No event found with ID: {args.id}")
    except Exception as e:
        logging.error(f"Failed to delete event: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="KaziLeo Event Management Tool")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    parser_add = subparsers.add_parser("add", help="Add a new event")
    parser_add.add_argument("--title", required=True)
    parser_add.add_argument("--description", required=True)
    parser_add.add_argument("--date", required=True, help="Event date/time in ISO format (YYYY-MM-DDTHH:MM:SS), assumed EAT.")
    parser_add.add_argument("--location", default="Online")
    parser_add.add_argument("--partner", required=True)
    parser_add.set_defaults(func=add_event)
    parser_list = subparsers.add_parser("list", help="List all upcoming events")
    parser_list.set_defaults(func=list_events)
    parser_delete = subparsers.add_parser("delete", help="Delete an event by ID")
    parser_delete.add_argument("--id", type=int, required=True)
    parser_delete.set_defaults(func=delete_event)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

