import logging

# This is a more structured mock database that includes a "featured" flag.
# This allows us to simulate a partnership with a TVET institution for job listings.
MOCK_JOBS = {
    "featured": [
        {
            "title": "Certified Plumber Grade III",
            "keywords": ["plumbing", "artisan", "technical", "craft", "construction"],
            "link": "https://www.brightermonday.co.ke/listings/certified-plumber-vwrj9p", # Example link
            "partner": "NITA Graduate Placement"
        },
        {
            "title": "Hotel Chef / Cook",
            "keywords": ["catering", "hospitality", "hotel", "chef", "food", "cook"],
            "link": "https://www.fuzu.com/kenya/jobs/cook-nairobi-4", # Example link
            "partner": "Nairobi TTI Careers"
        },
        {
            "title": "Automotive Mechanic",
            "keywords": ["mechanic", "automotive", "technician", "garage", "vehicle"],
            "link": "https://www.brightermonday.co.ke/listings/automotive-technician-p5w86v", # Example link
            "partner": "Kabete Poly Placement"
        }
    ],
    "standard": [
        {
            "title": "Electrical Technician",
            "keywords": ["electrical", "electronics", "engineering", "power", "technician"],
            "link": "https://www.fuzu.com/kenya/jobs/electrical-technician-kenya-2"
        },
        {
            "title": "Web Developer",
            "keywords": ["web developer", "web development", "web", "developer", "development"],
            "link": "https://www.myjobmag.co.ke/job/web-developer-team-lead-agency-yellow-pages-kenya-1"
        },
        {
            "title": "Building and Construction Mason",
            "keywords": ["construction", "mason", "building", "artisan"],
            "link": "https://www.brightermonday.co.ke/listings/construction-foreman-q2v7jp"
        },
        {
            "title": "Network Administrator",
            "keywords": ["network", "administrator", "IT", "infrastructure", "networking", "systems", "network admin", "network administrator", "it"],
            "link": "https://www.myjobmag.co.ke/job/network-administrator-safaricom-kenya-5"
        },
        {
            "title": "Accountant",
            "keywords": ["accountant", "finance", "accounts", "accounting"],
            "link": "https://www.myjobmag.co.ke/job/accountant-groots-kenya"
        },
        {
            "title": "Sales Representative",
            "keywords": ["sales", "representative", "marketing", "business development"],
            "link": "https://www.brightermonday.co.ke/listings/sales-representative-gwnd84"
        },
        {
            "title": "Interior Design Specialist",
            "keywords": ["interior design", "design", "architecture", "space planning"],
            "link": "https://www.myjobmag.co.ke/job/interior-design-specialist-prestige-bluestar-holdings-ltd"
        },
        {
            "title": "Senior Android Developer",
            "keywords": ["android", "developer", "mobile", "app", "development", "android developer"],
            "link": "https://www.myjobmag.co.ke/job/senior-android-developer-equity-bank-kenya-3"
        },
        {
            "title": "Welding and Fabrication Technician",
            "keywords": ["welding", "fabrication", "metalwork", "artisan"],
            "link": "https://www.fuzu.com/kenya/jobs/welder-nairobi"
        },
        {
            "title": "Front Office Administrator (Hotel)",
            "keywords": ["admin", "hospitality", "hotel", "receptionist", "front office"],
            "link": "https://www.brightermonday.co.ke/listings/front-office-administrator-xv8g5p"
        },
        {
            "title": "Junior Software Developer",
            "keywords": ["software", "developer", "tech", "it"],
            "link": "https://www.brightermonday.co.ke/listings/junior-software-developer-nairobi-vyq52p"
        },
        {
            "title": "Sales Representative (FMCG)",
            "keywords": ["sales", "fmcg", "retail"],
            "link": "https://www.fuzu.com/kenya/jobs/sales-representative-nairobi-1"
        },
        {
            "title": "Junior Accountant",
            "keywords": ["accountant", "finance", "accounts", "accounting"],
            "link": "https://www.brightermonday.co.ke/listings/junior-accountant-w7q4mp", 
        }
    ]
}

async def fetch_jobs(keyword: str) -> list[str] | None:
    """
    Searches the mock database for jobs based on a keyword.
    It now prioritizes and formats "featured" partner jobs.
    """
    if not keyword:
        return None
        
    keyword_lower = keyword.lower()
    found_jobs = []
    
    try:
        # 1. Search for and format featured jobs
        for job in MOCK_JOBS["featured"]:
            if any(kw in keyword_lower for kw in job["keywords"]):
                # THE FIX IS HERE: Replaced the newline character with a hyphen.
                formatted_string = f"⭐ *{job['title']}* (Partner: {job['partner']}) - {job['link']}"
                found_jobs.append(formatted_string)

        # 2. Search for and format standard jobs
        for job in MOCK_JOBS["standard"]:
            if any(kw in keyword_lower for kw in job["keywords"]):
                # THE FIX IS HERE: Replaced the newline character with a hyphen.
                formatted_string = f"*{job['title']}* - {job['link']}"
                found_jobs.append(formatted_string)
                
        logging.info(f"Found {len(found_jobs)} jobs for keyword: '{keyword}'")
        return found_jobs if found_jobs else []

    except Exception as e:
        logging.error(f"Error fetching jobs: {e}", exc_info=True)
        return None

