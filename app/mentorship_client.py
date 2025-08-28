# app/mentorship_client.py
import logging
from typing import List, Optional

# --- Uncategorized Mock Mentorship Database ---
# This is now a single list, allowing for more flexible keyword searching.
MOCK_MENTORS_LIST = [
    # Tech
    "*Jane Doe*, Senior Software Engineer at Safaricom",
    "*John Smith*, Cybersecurity Analyst at Equity Bank",
    "*Alex Kiprop*, AI/ML Specialist at a startup",
    
    # Business
    "*Mary Wanjiku*, Startup Founder & CEO",
    "*David Odhiambo*, Small Business Finance Coach",
    "*Christine Achieng*, Marketing & Brand Strategist",
    
    # Agribusiness
    "*Peter Kamau*, Experienced Poultry Farmer",
    "*Susan Njeri*, Agribusiness Value Chain Expert",
]

async def fetch_mentors(field: str) -> Optional[List[str]]:
    """
    Fetches mentor listings by performing a keyword search on the mock database.
    """
    logging.info(f"Fetching mock mentors for keyword: '{field}'")
    
    search_term = field.lower()
    
    # Find all mentors in the list that contain the search term
    found_mentors = [mentor for mentor in MOCK_MENTORS_LIST if search_term in mentor.lower()]
    
    if not found_mentors:
        logging.warning(f"No mock mentors found for keyword '{field}'")
        return []
        
    return found_mentors
