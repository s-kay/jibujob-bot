import logging

# This is a more structured mock database that includes a "featured" flag.
MOCK_GUIDES = {
    "featured": [
        {
            "title": "Register Your Business Name in Kenya (eCitizen Guide)",
            "keywords": ["register", "business", "legal", "ecitizen", "kenya"],
            "link": "https://www.businessdailyafrica.com/bd/lifestyle/personal-finance/how-to-register-your-business-name-on-ecitizen-3333334", # Example link
            "partner": "Government Services"
        },
        {
            "title": "Accessing the Youth Enterprise Development Fund (YEDF)",
            "keywords": ["funding", "loan", "grant", "youth fund", "yedf", "capital"],
            "link": "https://www.youthfund.go.ke/en/loans", # Example link
            "partner": "Government Funding"
        }
    ],
    "standard": [
        {
            "title": "Beginner's Guide to Poultry Farming in Kenya",
            "keywords": ["agribusiness", "poultry", "farming", "chicken", "kuku"],
            "link": "https://www.farmers.co.ke/article/2001438286/a-beginner-s-guide-to-poultry-farming-in-kenya"
        },
        {
            "title": "How to Start a Successful Salon or Kinyozi Business",
            "keywords": ["salon", "barbershop", "kinyozi", "beauty", "hair"],
            "link": "https://www.tuko.co.ke/business-ideas/447605-how-start-barbershop-kenya-2022-cost-profitability-more/"
        },
        {
            "title": "Starting an E-commerce Business with a Small Budget",
            "keywords": ["ecommerce", "online store", "selling online", "digital"],
            "link": "https://www.youtube.com/watch?v=k-y-4-g-y-w" # Example YouTube link
        },
        {
            "title": "Marketing Your 'Jua Kali' or Artisan Business on Social Media",
            "keywords": ["jua kali", "artisan", "marketing", "social media", "crafts"],
            "link": "https://www.yellow.co.ke/blog/posts/social-media-marketing-for-small-businesses-in-kenya"
        },
        {
            "title": "A Guide to Starting a Catering Business",
            "keywords": ["catering", "food", "hospitality", "events"],
            "link": "https://www.standardmedia.co.ke/entertainment/lifestyle/article/2001423851/seven-steps-to-starting-a-successful-catering-business"
        }
    ]
}

async def fetch_entrepreneurship_guides(keyword: str) -> list[str] | None:
    """
    Searches the mock database for entrepreneurship guides based on a keyword.
    It now prioritizes and formats "featured" partner resources.
    """
    if not keyword:
        return None
        
    keyword_lower = keyword.lower()
    found_guides = []
    
    try:
        # 1. Search for and format featured resources
        for guide in MOCK_GUIDES["featured"]:
            if any(kw in keyword_lower for kw in guide["keywords"]):
                formatted_string = f"⭐ *{guide['title']}* (Partner: {guide['partner']})\n{guide['link']}"
                found_guides.append(formatted_string)

        # 2. Search for and format standard resources
        for guide in MOCK_GUIDES["standard"]:
            if any(kw in keyword_lower for kw in guide["keywords"]):
                formatted_string = f"*{guide['title']}*\n{guide['link']}"
                found_guides.append(formatted_string)
                
        logging.info(f"Found {len(found_guides)} entrepreneurship guides for keyword: '{keyword}'")
        return found_guides if found_guides else []

    except Exception as e:
        logging.error(f"Error fetching entrepreneurship guides: {e}", exc_info=True)
        return None

