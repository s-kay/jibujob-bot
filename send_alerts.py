import os
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import UserSession
from app.config import settings
from app.job_client import fetch_jobs
from app.whatsapp_client import send_whatsapp_message
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
# Use the DATABASE_URL from the environment variables provided by Render
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- State File to Track Last Run ---
STATE_FILE = "last_run.txt"

def get_last_run_time():
    """Reads the timestamp of the last successful run."""
    try:
        with open(STATE_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    except FileNotFoundError:
        return None

def update_last_run_time():
    """Writes the current timestamp to the state file."""
    with open(STATE_FILE, "w") as f:
        f.write(datetime.utcnow().isoformat())

async def send_job_alerts():
    """The main function to find and send job alerts."""
    logging.info("Starting job alert check...")
    db = SessionLocal()
    
    # For our manual mock data, we can't check for "new" jobs easily.
    # Instead, we will find all jobs and assume they are new for the demonstration.
    # In a real API, you would filter jobs by their posting date.
    
    try:
        # 1. Get all users with a saved job interest
        users_with_interest = db.query(UserSession).filter(UserSession.job_interest.isnot(None)).all()
        
        if not users_with_interest:
            logging.info("No users with saved job interests found. Exiting.")
            return

        logging.info(f"Found {len(users_with_interest)} users with job interests.")

        # 2. Group users by their job interest to search efficiently
        interest_groups = {}
        for user in users_with_interest:
            # THE FIX IS HERE: Add a safety check to ensure job_interest is not None
            if user.job_interest:
                interest = user.job_interest.lower()
                if interest not in interest_groups:
                    interest_groups[interest] = []
                interest_groups[interest].append(user.phone_number)
            
        # 3. For each interest, find jobs and send alerts
        for interest, phone_numbers in interest_groups.items():
            logging.info(f"Searching for new jobs for interest: '{interest}'")
            
            # In a real scenario, you'd filter by date. Here we fetch all.
            new_jobs = await fetch_jobs(interest)
            
            if new_jobs:
                logging.info(f"Found {len(new_jobs)} new jobs for '{interest}'. Sending alerts...")
                
                # Format the message
                job_list_str = "\n".join(new_jobs[:3]) # Send top 3
                message = (
                    f"Habari! 👋 Some new jobs matching your interest in *{interest.title()}* have just come up:\n\n"
                    f"{job_list_str}\n\n"
                    "Type '1' to search for more roles at any time."
                )
                
                # Send the alert to all users with this interest
                for phone_number in phone_numbers:
                    await send_whatsapp_message(phone_number, message)
                    logging.info(f"Alert sent to {phone_number} for interest '{interest}'.")
            else:
                logging.info(f"No new jobs found for '{interest}'.")

        # 4. Update the timestamp for the next run
        # update_last_run_time()
        logging.info("Job alert check finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the alert process: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(send_job_alerts())

