import os
import logging
from sqlalchemy import create_engine
# THE FIX: Import the Session object for correct type hinting
from sqlalchemy.orm import sessionmaker, Session
import sys
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.models import Base, UserSession, FeaturedJob
from app.config import settings
from app.whatsapp_client import send_template_message
from app.job_client import MOCK_JOBS
from app.job_client import fetch_jobs
from app import crud

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- Smarter Keyword Mapping ---
INTEREST_KEYWORDS = {
    "it": ["it", "software", "developer", "tech", "engineer", "SOC", "support", "AI engineer", "automation", "architect", "cloud", "network", "systems", "infrastructure","ict"],
    "sales": ["sales", "business development", "retail", "agent"],
    "admin": ["admin", "assistant", "clerical", "office support", "HR", "Human Resource", "People","Culture"],
    "accountant": ["accountant", "finance", "audit", "bookkeeping","accounting", "CPA", "CMA"],
    "driver": ["driver", "driving", "logistics"],
    "internship": ["internship", "intern"],
    "marketing": ["marketing", "SEO", "content", "social media", "digital"],
    "healthcare": ["healthcare", "nurse", "medical", "clinic", "hospital"],
    "education": ["education", "teacher", "tutor", "instructor"],
    "construction": ["construction", "builder", "contractor", "foreman"],
    "hospitality": ["hospitality", "hotel", "restaurant", "chef", "waiter"],
    "customer service": ["customer service", "support", "call center", "client relations", "customer"],
    "finance": ["finance", "banking", "investment", "financial analyst"],
    "engineering": ["engineering", "mechanical", "civil", "electrical", "architect"],
    "creative": ["creative", "designer", "artist", "photographer", "videographer"],
    "legal": ["legal", "lawyer", "paralegal", "legal assistant"],
    "human resources": ["human resources", "HR", "recruiter", "talent acquisition"],
    "supply chain": ["supply chain", "procurement", "logistics", "inventory", "culture", "people"],
    "research": ["research", "scientist", "laboratory", "data analyst", "data science", "data"],
    "writing": ["writing", "editor", "content creator", "copywriter"],
    "media": ["media", "journalist", "broadcaster", "public relations"],
    "real estate": ["real estate", "property", "broker", "agent"],
    "retail": ["retail", "store", "sales associate", "cashier", "warehouse"],
    "security": ["security", "guard", "surveillance", "loss prevention"],
    "transportation": ["transportation", "logistics", "fleet", "driver", "courier", "rider", "delivery", "boda boda", "taxi", "uber", "bolt"],
    "agriculture": ["agriculture", "farm", "agronomy", "field worker", "farm worker"],
    "cleaning": ["cleaning", "housekeeping", "janitor", "maid"],
    "personal care": ["personal care", "nanny", "caregiver", "babysitter", "home health aide", "elderly care", "massage", "barber", "hairdresser", "beauty therapist"],
    "event planning": ["event planning", "coordinator", "planner", "wedding", "conference", "catering", "DJ", "MC", "photographer", "videographer"],
    "non-profit": ["non-profit", "NGO", "charity", "social work"],
    "telecommunications": ["telecommunications", "network", "cable", "internet", "broadband"],
    "arts": ["arts", "museum", "gallery", "curator"],
    "sports": ["sports", "coach", "trainer", "fitness", "gym"],
    "environmental": ["environmental", "sustainability", "conservation", "ecologist"],
    "tourism": ["tourism", "travel", "tour guide", "hospitality"],
    "freelance": ["freelance", "contractor", "gig", "remote"],
    "projects": ["project", "project manager", "PMO", "scrum master"], 
    "interior design": ["interior design", "interior decorator", "furniture", "home decor"],
    "legal assistant": ["legal assistant", "paralegal", "legal secretary", "legal support", "legal", "law clerk", "legal intern", "counsel", "attorney assistant", "advocate"],
    "public relations": ["public relations", "PR", "communications", "media relations"],
    "other": ["other", "miscellaneous", "various"], # Catch-all for uncategorized interests
}

async def fetch_all_jobs_for_interest(db: Session, interest: str) -> list[dict]:
    """Helper function to fetch all jobs (DB and mock) for a given interest."""
    search_terms = INTEREST_KEYWORDS.get(interest.lower(), [interest])
    all_found_jobs = {} # Use a dictionary to avoid duplicate links
    for term in search_terms:
        jobs_data = await fetch_jobs(db, term)
        if jobs_data:
            for job in jobs_data:
                # Use the link as a unique key
                all_found_jobs[job['link']] = job
    return list(all_found_jobs.values())

async def send_job_alerts():
    """
    Finds and sends personalized job alerts, ensuring no duplicates are sent.
    """
    logging.info("Starting smart job alert check...")
    db = SessionLocal()
    
    try:
        # Get all users who have a saved job interest
        users_with_interest = db.query(UserSession).filter(UserSession.job_interest.isnot(None)).all()
        
        if not users_with_interest:
            logging.info("No users with saved job interests found. Exiting.")
            return

        logging.info(f"Found {len(users_with_interest)} users with job interests to check.")

        for user in users_with_interest:
            if not user.job_interest or not user.user_name:
                continue

            interest = user.job_interest.strip()
            
            # 1. Get all potential jobs for the user's interest
            all_potential_jobs = await fetch_all_jobs_for_interest(db, interest)

            # 2. Get the list of jobs we've already sent to this user
            sent_links = crud.get_sent_job_links_for_user(db, user.phone_number)

            # 3. Filter out the jobs that have already been sent
            new_jobs_to_send = [job for job in all_potential_jobs if job['link'] not in sent_links]
            
            if new_jobs_to_send:
                logging.info(f"Found {len(new_jobs_to_send)} NEW jobs for '{interest}'. Sending alert to {user.phone_number}...")
                
                # Format the job strings for the template
                job_strings = [f"• {job['title']}" for job in new_jobs_to_send[:3]] # Take top 3
                
                # Ensure we always have 3 parameters for the template
                while len(job_strings) < 3:
                    job_strings.append(" ") # Use a space for empty slots

                components = [{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": user.user_name},
                        {"type": "text", "text": interest.title()},
                        {"type": "text", "text": job_strings[0]},
                        {"type": "text", "text": job_strings[1]},
                        {"type": "text", "text": job_strings[2]},
                    ]
                }]
                
                await send_template_message(user.phone_number, "job_alert_v2", components)

                # 4. Mark these new jobs as "sent" for this user
                for job in new_jobs_to_send:
                    crud.mark_job_as_sent(db, user.phone_number, job['link'])
                db.commit() # Commit all the new "sent" records for this user
            else:
                logging.info(f"No new jobs found for '{interest}' for user {user.phone_number}.")

        logging.info("Job alert check finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the alert process: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(send_job_alerts())


