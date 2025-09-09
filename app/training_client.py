import logging

# This is a more structured mock database that includes a "featured" flag.
# This allows us to simulate a partnership with a TVET institution.
MOCK_COURSES = {
    "featured": [
        {
            "title": "Grade III Certificate in Plumbing",
            "keywords": ["plumbing", "artisan", "technical", "craft"],
            "link": "https://www.nita.go.ke/courses/plumbing.aspx", # Example link
            "partner": "NITA"
        },
        {
            "title": "Diploma in Electrical & Electronics Engineering (Power Option)",
            "keywords": ["electrical", "electronics", "engineering", "power", "technician"],
            "link": "https://www.kabete.ac.ke/electrical-electronics-engineering/", # Example link
            "partner": "Kabete National Polytechnic"
        },
        {
            "title": "Artisan Certificate in Catering & Hospitality",
            "keywords": ["catering", "hospitality", "hotel", "chef", "food"],
            "link": "https://www.ntti.ac.ke/hospitality/", # Example link
            "partner": "Nairobi TTI"
        }
    ],
    "standard": [
        {
            "title": "Google Digital Skills for Africa (Free)",
            "keywords": ["digital marketing", "online", "google", "seo", "Digital skills"],
            "link": "https://skillshop.exceedlms.com/student/collection/1384851"
        },
        {
            "title": "Introduction to Graphic Design (Free Course)",
            "keywords": ["graphic design", "design", "creative", "photoshop"],
            "link": "https://alison.com/course/graphic-design"
        },
        {
            "title": "Social Media Marketing Certification (Free)",
            "keywords": ["social media", "marketing", "facebook", "instagram"],
            "link": "https://academy.hubspot.com/courses/social-media"
        },
        {
            "title": "Public Speaking Fundamentals (Free Course)",
            "keywords": ["public speaking", "communication", "soft skills"],
            "link": "https://www.coursera.org/learn/public-speaking"
        },
        {
            "title": "Communication and Negotiation Skills (Free Course)",
            "keywords": ["communication", "negotiation", "soft skills"],
            "link": "https://alison.com/tag/communication-skills"
        },
        {
            "title": "Financial Literacy & Personal Finance",
            "keywords": ["finance", "budgeting", "pesa", "money"],
            "link": "https://alison.com/tag/financial-literacy"
        }
    ]
}

async def fetch_trainings(keyword: str) -> list[str] | None:
    """
    Searches the mock database for training courses based on a keyword.
    It now prioritizes and formats "featured" partner courses.
    """
    if not keyword:
        return None
        
    keyword_lower = keyword.lower()
    found_courses = []
    
    try:
        # 1. Search for and format featured courses
        for course in MOCK_COURSES["featured"]:
            if any(kw in keyword_lower for kw in course["keywords"]):
                # Add a star and the partner name to highlight it
                formatted_string = f"⭐ *{course['title']}* (Partner: {course['partner']})\n{course['link']}"
                found_courses.append(formatted_string)

        # 2. Search for and format standard courses
        for course in MOCK_COURSES["standard"]:
            if any(kw in keyword_lower for kw in course["keywords"]):
                formatted_string = f"*{course['title']}*\n{course['link']}"
                found_courses.append(formatted_string)
                
        logging.info(f"Found {len(found_courses)} courses for keyword: '{keyword}'")
        return found_courses if found_courses else []

    except Exception as e:
        logging.error(f"Error fetching trainings: {e}", exc_info=True)
        return None

