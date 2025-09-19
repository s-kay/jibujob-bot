import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import FeaturedJob

# THE UPGRADE: The mock data is now a list of dictionaries, each with a full description.
MOCK_JOBS: List[Dict[str, Any]] = [
    {
        "title": "Junior Accountant",
        "keywords": ["accountant", "finance", "accounts", "junior", "CPA"],
        "link": "https://www.brightermonday.co.ke/listings/junior-accountant-w7q4mp",
        "description": "Responsibilities include assisting with the preparation of financial statements, reconciling bank statements, and managing accounts payable/receivable. Must have a CPA Part 2 and be proficient in QuickBooks."
    },
    {
        "title": "Administrative Assistant",
        "keywords": ["admin", "assistant", "clerical", "office support", "receptionist"],
        "link": "https://www.fuzu.com/kenya/jobs/administrative-assistant-nairobi",
        "description": "Seeking a highly organized Administrative Assistant to manage office supplies, schedule meetings, and support our team. Strong communication skills and proficiency in MS Office are required."
    },
    {
        "title": "Sales Representative (FMCG)",
        "keywords": ["sales", "fmcg", "retail", "business development"],
        "link": "https://www.fuzu.com/kenya/jobs/sales-representative-nairobi-1",
        "description": "Join our team to drive sales of our consumer goods. Responsibilities include visiting clients, managing orders, and achieving sales targets. Previous experience in FMCG is a plus."
    },
    {
        "title": "Junior Software Developer",
        "keywords": ["software", "developer", "tech", "it", "python", "engineer"],
        "link": "https://www.brightermonday.co.ke/listings/junior-software-developer-nairobi-vyq52p",
        "description": "We are looking for a passionate Junior Developer to join our team. You will be working with Python and Django to build and maintain our web applications. A degree in Computer Science is preferred."
    },
    {
        "title": "Certified Plumber Grade III (Partner: NITA)",
        "keywords": ["plumbing", "artisan", "technical", "craft", "construction"],
        "link": "https://www.brightermonday.co.ke/listings/certified-plumber-vwrj9p",
        "description": "Our partner requires a certified Grade III Plumber for commercial and residential installation projects. Must have a valid NITA trade test certificate."
    },
    {
        "title": "Automotive Mechanic (Partner: Kabete Poly)",
        "keywords": ["mechanic", "automotive", "technician", "garage", "vehicle"],
        "link": "https://www.brightermonday.co.ke/listings/automotive-technician-p5w86v",
        "description": "A busy garage is seeking an experienced automotive mechanic. Responsibilities include vehicle diagnosis, repair, and maintenance. A diploma from a recognized TVET institution is required."
    }
]

async def fetch_jobs(db: Session, keyword: str) -> List[Dict[str, Any]]:
    """
    Searches for jobs from both the live partner database and the fallback mock list.
    """
    if not keyword:
        return []
        
    keyword_lower = keyword.lower()
    found_jobs = []
    found_links = set() # To prevent duplicates

    try:
        # --- PRIORITY 1: Search the live database for partner-submitted jobs ---
        # The '%' are wildcards for a 'LIKE' search in SQL
        db_jobs = db.query(FeaturedJob).filter(
            (FeaturedJob.title.ilike(f"%{keyword_lower}%")) |
            (FeaturedJob.keywords.ilike(f"%{keyword_lower}%")) |
            (FeaturedJob.description.ilike(f"%{keyword_lower}%"))
        ).order_by(FeaturedJob.created_at.desc()).all()

        for job in db_jobs:
            job_data = {
                "title": f"⭐ *{job.title}* (Partner: {job.partner_name})",
                "link": job.link,
                "description": job.description,
                # We can add other fields here if needed in the future
            }
            found_jobs.append(job_data)
            found_links.add(job.link)

        # --- PRIORITY 2: Search the fallback mock list for standard jobs ---
        for job in MOCK_JOBS:
            searchable_text = job['title'].lower() + " " + " ".join(job.get('keywords', []))
            if keyword_lower in searchable_text and job['link'] not in found_links:
                # We create a dictionary with the same structure for consistency
                job_data = {
                    "title": f"*{job['title']}*",
                    "link": job['link'],
                    "description": job.get('description', '')
                }
                found_jobs.append(job_data)
                
        logging.info(f"Found {len(found_jobs)} total jobs for keyword: '{keyword}'")
        return found_jobs

    except Exception as e:
        logging.error(f"Error fetching jobs: {e}", exc_info=True)
        return []



