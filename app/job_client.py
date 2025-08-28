# app/job_client.py
import httpx
import logging
from typing import List, Optional

# --- Enhanced Mock Job Database ---
# This acts as our stand-in for a live API for now.
MOCK_JOBS = {
    "software developer": [
        "Backend Developer (Supabase & API) at TechCorp KE (Remote)",
        "Junior Python Developer at FinInnovate (Nairobi)",
        "React Native Developer at Crystal Recruit (Remote, Contract)",
        "Senior Full Stack Engineer at BlueCollar Ltd (Nairobi)",
    ],
    "accountant": [
        "Reporting Accountant at CSS Ltd (Nairobi)",
        "Finance and Accounting Executive at Eldoret Farms (Eldoret)",
        "Accountant at Jocham Hospital (Mombasa)",
        "Junior Accountant at Brites Management (Nairobi)",
    ],
    "sales": [
        "Sales Executive (Interior Design) at CSS Ltd (Nairobi)",
        "Regional Sales Lead at Trinova Technologies (Remote)",
        "Independent Sales Executive at Ledger 360 (Remote, Commission)",
    ],
    "admin": [
        "Remote Executive Assistant at People Edge (Remote)",
        "Executive & Business Admin Assistant (Remote, US Hours)",
        "ICT Coordinator at Bestlinks Talents Hub (Nairobi)",
    ],
}


async def fetch_jobs(job_title: str) -> Optional[List[str]]:
    """
    Fetches job listings. 
    Currently uses an internal mock database with improved search logic.
    """
    logging.info(f"Fetching mock jobs for query: '{job_title}'")
    
    # Simple search logic: find the best matching key in our mock database
    search_term = job_title.lower()
    best_match_key = None
    for key in MOCK_JOBS:
        # Check if the user's input is a substring of the key, or vice-versa
        if search_term in key or key in search_term:
            best_match_key = key
            break
            
    if best_match_key:
        return MOCK_JOBS[best_match_key]
    
    # If no direct match, return an empty list
    logging.warning(f"No mock job category found for '{job_title}'")
    return []
