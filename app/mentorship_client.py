import logging

# This is a more structured mock database that includes a "featured" flag.
MOCK_MENTORS = {
    "featured": [
        {
            "title": "E-Mobilis Technology Institute (Tech Startups)",
            "keywords": ["tech", "software", "developer", "startup", "mobile"],
            "link": "https://emobilis.ac.ke/", # Example link
            "partner": "TVET Partner Program"
        },
        {
            "title": "Kenya National Jua Kali Co-operative Society (Artisan Businesses)",
            "keywords": ["artisan", "jua kali", "craft", "technical", "business"],
            "link": "https://www.standardmedia.co.ke/business/business/article/2001382424/jua-kali-sector-to-benefit-from-new-co-operative", # Example link
            "partner": "TVET Partner Program"
        }
    ],
    "standard": [
        {
            "title": "Centonomy - Personal Finance & Entrepreneurship Courses",
            "keywords": ["business", "finance", "entrepreneurship", "money"],
            "link": "https://centonomy.com/"
        },
        {
            "title": "Mwende Gatabaki on LinkedIn (Leadership & Tech)",
            "keywords": ["tech", "leadership", "business"],
            "link": "https://www.linkedin.com/in/mwendegatabaki/"
        },
        {
            "title": "Juliana Rotich on Twitter/X (Tech & Social Enterprise)",
            "keywords": ["tech", "social enterprise", "innovation"],
            "link": "https://twitter.com/afromusing"
        },
        {
            "title": "AkiraChix - Mentoring Women in Tech",
            "keywords": ["tech", "women in tech", "software", "developer"],
            "link": "https://akirachix.com/"
        }
    ]
}

async def fetch_mentors(keyword: str) -> list[str] | None:
    """
    Searches the mock database for mentors based on a keyword.
    It now prioritizes and formats "featured" partner resources.
    """
    if not keyword:
        return None
        
    keyword_lower = keyword.lower()
    found_mentors = []
    
    try:
        # 1. Search for and format featured resources
        for mentor in MOCK_MENTORS["featured"]:
            if any(kw in keyword_lower for kw in mentor["keywords"]):
                formatted_string = f"⭐ *{mentor['title']}* (Partner: {mentor['partner']})\n{mentor['link']}"
                found_mentors.append(formatted_string)

        # 2. Search for and format standard resources
        for mentor in MOCK_MENTORS["standard"]:
            if any(kw in keyword_lower for kw in mentor["keywords"]):
                formatted_string = f"*{mentor['title']}*\n{mentor['link']}"
                found_mentors.append(formatted_string)
                
        logging.info(f"Found {len(found_mentors)} mentor resources for keyword: '{keyword}'")
        return found_mentors if found_mentors else []

    except Exception as e:
        logging.error(f"Error fetching mentors: {e}", exc_info=True)
        return None

