# app/mentorship_client.py
import asyncio
from typing import List, Optional

# --- High-Quality Mock Database of Real, Relevant Mentorship Resources ---
# This list is manually curated to provide real value to users in the pilot program.
# It links to public profiles and content from respected Kenyan professionals.
MOCK_MENTORS_LIST = [
    # Tech & Innovation
    "*Juliana Rotich* - A respected technologist and entrepreneur. Follow her insights on tech in Africa. (Tech) https://www.linkedin.com/in/julianarotich/",
    "*Dr. Bitange Ndemo* - Professor and expert on technology, innovation, and governance in Kenya. (Tech/Business) https://www.linkedin.com/in/bitange-ndemo-4b491125/",
    "*The Kenyan Coder* - A popular YouTube channel with practical coding tutorials and tech career advice in Kenya. (Tech) https://www.youtube.com/@TheKenyanCoder",

    # Business & Entrepreneurship
    "*Wandia Gichuru* - Co-founder of VIVO Fashion Group. A great resource for retail and entrepreneurship insights. (Business) https://www.linkedin.com/in/wandia-gichuru-93448410/",
    "*Julian Kyula* - Founder of MODE, offers sharp insights on entrepreneurship and finance. (Business/Finance) https://www.linkedin.com/in/julian-kyula-26b2b73/",
    "*Kenyan Wallstreet* - A great YouTube channel for learning about investment, finance, and business trends in Kenya. (Finance/Business) https://www.youtube.com/@KenyanWallstreet",

    # Sales & Marketing
    "*Muthoni Maingi* - Digital marketing expert and leader. Follow for insights on brand strategy. (Marketing) https://www.linkedin.com/in/muthonimaingi/",
    "*Chris Gathingu* - Founder of Tangazoletu, a leader in mobile and digital solutions. (Tech/Sales) https://www.linkedin.com/in/chris-gathingu-a1b73b24/",

    # General Career Advice
    "*'Your Next Move' with Patricia Ithau* - A YouTube series with career stories from Kenyan leaders. (Career) https://www.youtube.com/playlist?list=PLpsl_29oVz_b5q4-q-J-Y-z-8-s-k-b-z",
    "*Cynthia Nyongesa* - Offers practical and relatable career advice for young Kenyans on YouTube. (Career) https://www.youtube.com/@CynthiaNyongesa",
]

async def fetch_mentors(keyword: str) -> Optional[List[str]]:
    """
    Simulates fetching mentorship resources based on a keyword search.
    """
    await asyncio.sleep(1) # Simulate network latency
    
    try:
        # A simple keyword search logic
        keyword = keyword.lower()
        results = [
            mentor for mentor in MOCK_MENTORS_LIST 
            if keyword in mentor.lower()
        ]
        return results if results else []
    except Exception as e:
        print(f"Error fetching mentor data: {e}")
        return None

