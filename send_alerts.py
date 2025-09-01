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
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Smarter Keyword Mapping ---
# This makes our search more intelligent.
INTEREST_KEYWORDS = {
    "it": ["it", "software", "developer", "tech", "engineer", "SOC", "support", "AI engineer", "automation"],
    "sales": ["sales", "business development", "retail", "agent"],
    "admin": ["admin", "assistant", "clerical", "office support", "HR", "Human Resource", "People","Culture"],
    "accountant": ["accountant", "finance", "audit", "bookkeeping"],
    "driver": ["driver", "driving", "logistics"],
    "intern": ["intern", "internship", "trainee"],
    "attachment": ["attachment", "attach", "attachment", "attach"],
    # Add more mappings as needed
}

async def fetch_jobs_for_interest(interest: str) -> list[str]:
    """Fetches jobs for a given interest using multiple related keywords."""
    search_terms = INTEREST_KEYWORDS.get(interest.lower(), [interest]) # Fallback to the interest itself
    all_found_jobs = set() # Use a set to automatically handle duplicates

    for term in search_terms:
        jobs = await fetch_jobs(term)
        if jobs:
            for job in jobs:
                all_found_jobs.add(job)
    
    return list(all_found_jobs)

async def send_job_alerts():
    """The main function to find and send job alerts."""
    logging.info("Starting job alert check...")
    db = SessionLocal()
    
    try:
        # 1. Get all users with a saved job interest
        users_with_interest = db.query(UserSession).filter(UserSession.job_interest.isnot(None)).all()
        
        if not users_with_interest:
            logging.info("No users with saved job interests found. Exiting.")
            return

        logging.info(f"Found {len(users_with_interest)} users with job interests.")

        # 2. Group users by their job interest
        interest_groups = {}
        for user in users_with_interest:
            if user.job_interest:
                interest = user.job_interest.lower().strip() # Clean the interest
                if interest not in interest_groups:
                    interest_groups[interest] = []
                interest_groups[interest].append(user.phone_number)
            
        # 3. For each interest, find jobs and send alerts
        for interest, phone_numbers in interest_groups.items():
            logging.info(f"Searching for new jobs for interest: '{interest}'")
            
            new_jobs = await fetch_jobs_for_interest(interest)
            
            if new_jobs:
                logging.info(f"Found {len(new_jobs)} new jobs for '{interest}'. Sending alerts...")
                
                job_list_str = "\n".join(new_jobs[:3])
                message = (
                    f"Habari! 👋 Some new jobs matching your interest in *{interest.title()}* have just come up:\n\n"
                    f"{job_list_str}\n\n"
                    "Type '1' to search for more roles at any time."
                )
                
                for phone_number in phone_numbers:
                    await send_whatsapp_message(phone_number, message)
                    logging.info(f"Alert sent to {phone_number} for interest '{interest}'.")
            else:
                logging.info(f"No new jobs found for '{interest}'.")

        logging.info("Job alert check finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the alert process: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(send_job_alerts())

