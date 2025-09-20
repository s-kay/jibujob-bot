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
    "other": ["other", "miscellaneous", "various"], # Catch-all for uncategorized interests
}

# THE FIX: The type hint for `db` is now correctly set to `Session`.
async def fetch_jobs_for_interest(db: Session, interest: str) -> list[str]:
    """Helper function to fetch jobs using multiple related keywords."""
    search_terms = INTEREST_KEYWORDS.get(interest.lower(), [interest])
    all_found_jobs = set()
    
    # --- Fetch from Database ---
    for term in search_terms:
        db_jobs = db.query(FeaturedJob).filter(
            (FeaturedJob.keywords.ilike(f"%{term}%")) |
            (FeaturedJob.title.ilike(f"%{term}%"))
        ).all()
        for job in db_jobs:
            formatted_job = f"⭐ *{job.title}* (Partner: {job.partner_name}) - {job.link}"
            all_found_jobs.add(formatted_job)

    # --- Fetch from Mock Fallback ---
    for term in search_terms:
        for job in MOCK_JOBS:
            searchable_text = job['title'].lower() + " " + " ".join(job.get('keywords', []))
            if term in searchable_text:
                formatted_job = f"*{job['title']}* - {job['link']}"
                all_found_jobs.add(formatted_job)

    return list(all_found_jobs)

async def send_job_alerts():
    """Finds and sends job alerts using the new unified job client."""
    logging.info("Starting job alert check...")
    db = SessionLocal()
    
    try:
        users_with_interest = db.query(UserSession).filter(UserSession.job_interest.isnot(None)).all()
        
        if not users_with_interest:
            logging.info("No users with saved job interests found. Exiting.")
            return

        for user in users_with_interest:
            if not user.job_interest or not user.user_name:
                continue

            interest = user.job_interest.strip()
            new_jobs = await fetch_jobs_for_interest(db, interest)
            
            if new_jobs:
                logging.info(f"Found {len(new_jobs)} new jobs for '{interest}'. Sending alert to {user.phone_number}...")
                
                job_params = []
                for i in range(3):
                    if i < len(new_jobs):
                        job_params.append(f"• {new_jobs[i]}")
                    else:
                        job_params.append(" ")

                components = [{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": user.user_name},
                        {"type": "text", "text": interest.title()},
                        {"type": "text", "text": job_params[0]},
                        {"type": "text", "text": job_params[1]},
                        {"type": "text", "text": job_params[2]},
                    ]
                }]
                
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

