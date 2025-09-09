import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import asyncio

# Add the project root to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.models import Base, UserSession
from app.config import settings
from app.job_client import fetch_jobs
# THE FIX: We now import the correct function for sending templates
from app.whatsapp_client import send_template_message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- Smarter Keyword Mapping ---
INTEREST_KEYWORDS = {
    "it": ["it", "software", "developer", "tech", "engineer", "SOC", "support", "AI engineer", "automation"],
    "sales": ["sales", "business development", "retail", "agent"],
    "admin": ["admin", "assistant", "clerical", "office support", "HR", "Human Resource", "People","Culture"],
    "accountant": ["accountant", "finance", "audit", "bookkeeping"],
    "driver": ["driver", "driving", "logistics"]
}

async def fetch_jobs_for_interest(interest: str) -> list[str]:
    """Fetches jobs for a given interest using multiple related keywords."""
    search_terms = INTEREST_KEYWORDS.get(interest.lower(), [interest])
    all_found_jobs = set()
    for term in search_terms:
        jobs = await fetch_jobs(term)
        if jobs:
            for job in jobs:
                all_found_jobs.add(job)
    return list(all_found_jobs)

async def send_job_alerts():
    """The main function to find and send job alerts using pre-approved templates."""
    logging.info("Starting job alert check...")
    db = SessionLocal()
    
    try:
        users_with_interest = db.query(UserSession).filter(UserSession.job_interest.isnot(None)).all()
        
        if not users_with_interest:
            logging.info("No users with saved job interests found. Exiting.")
            return

        logging.info(f"Found {len(users_with_interest)} users with job interests.")

        for user in users_with_interest:
            if not user.job_interest or not user.user_name:
                continue

            interest = user.job_interest.strip()
            logging.info(f"Searching for new jobs for user {user.phone_number} with interest: '{interest}'")
            
            new_jobs = await fetch_jobs_for_interest(interest)
            
            if new_jobs:
                logging.info(f"Found {len(new_jobs)} new jobs for '{interest}'. Sending alert to {user.phone_number}...")
                
                # --- THE FIX: Dynamically build parameters to avoid newlines ---
                # We only show the top 3 jobs in the alert
                jobs_to_send = new_jobs[:3]
                
                # Create a list of parameters, ensuring we have exactly 3 for the template
                job_params = []
                for i in range(3):
                    if i < len(jobs_to_send):
                        # Use a bullet point for nice formatting
                        job_params.append(f"• {jobs_to_send[i]}")
                    else:
                        # If there are fewer than 3 jobs, fill the rest with empty strings
                        job_params.append("")

                components = [{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": user.user_name},      # {{1}} - User's Name
                        {"type": "text", "text": interest.title()},    # {{2}} - Job Interest
                        {"type": "text", "text": job_params[0]},       # {{3}} - Job 1
                        {"type": "text", "text": job_params[1]},       # {{4}} - Job 2
                        {"type": "text", "text": job_params[2]},       # {{5}} - Job 3
                    ]
                }]
                
                # Use the new, more robust template name
                await send_template_message(user.phone_number, "job_alert_v2", components)
            else:
                logging.info(f"No new jobs found for '{interest}'.")

        logging.info("Job alert check finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the alert process: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(send_job_alerts())

