# app/mentorship_client.py
import logging
from typing import List, Optional

# --- Enhanced Mock Mentorship Database ---
MOCK_MENTORS = {
    "tech": [
        "Jane Doe, Senior Software Engineer at Safaricom",
        "John Smith, Cybersecurity Analyst at Equity Bank",
        "Alex Kiprop, AI/ML Specialist at a startup",
    ],
    "business": [
        "Mary Wanjiku, Startup Founder & CEO",
        "David Odhiambo, Small Business Finance Coach",
        "Christine Achieng, Marketing & Brand Strategist",
    ],
    "agribusiness": [
        "Peter Kamau, Experienced Poultry Farmer",
        "Susan Njeri, Agribusiness Value Chain Expert",
    ],
}

async def fetch_mentors(field: str) -> Optional[List[str]]:
    """
    Fetches mentor listings.
    Currently uses an internal mock database.
    """
    logging.info(f"Fetching mock mentors for query: '{field}'")
    
    best_match_key = None
    for key in MOCK_MENTORS:
        if key in field.lower():
            best_match_key = key
            break
            
    if best_match_key:
        return MOCK_MENTORS[best_match_key]
    
    logging.warning(f"No mock mentorship category found for '{field}'")
    return []
