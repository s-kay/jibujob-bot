# app/job_client.py
import httpx
import logging
from typing import List, Optional

# --- Enhanced Mock Job Database with REAL Data ---
# This data is hardcoded but represents actual recent job listings from Kenyan job boards.
# Job titles are now bolded for better presentation in WhatsApp.
MOCK_JOBS = {
    "software developer": [
        "*Software Developer* at Buy Domain Kenya - https://www.brightermonday.co.ke/listings/software-developer-4nznmv",
        "*Senior Full Stack Software Engineer* at Bluecollar Technologies - https://www.brightermonday.co.ke/listings/senior-full-stack-software-engineer-d8kngv",
        "*Software Developer* at Enfinite Solutions Limited - https://www.brightermonday.co.ke/listings/software-developer-20e0nq",
    ],
    "accountant": [
        "*Accountant* at Burhani Engineers Ltd - https://www.fuzu.com/kenya/jobs/accountant-burhani-engineers-ltd",
        "*Project Accountant* at Tatu City - https://www.fuzu.com/kenya/jobs/project-accountant-tatu-city",
        "*Senior Accountant* at Kibabii University - https://www.fuzu.com/kenya/jobs/senior-accountant-kibabii-university-2",
    ],
    "sales": [
        "*Sales Manager* at Crystal Recruitment - https://www.brightermonday.co.ke/listings/sales-manager-vx8vjp",
        "*Wholesale Laptop Sales Agent* at Kolm Solutions - https://www.brightermonday.co.ke/listings/wholesale-laptop-sales-agent-p5p8w5",
        "*Van Salesman* at Focused Human Resource Solutions - https://www.brightermonday.co.ke/listings/van-salesman-q2n5wk",
    ],
    "admin": [
        "*Administrative Assistant* at Oasis Outsourcing - https://www.fuzu.com/kenya/jobs/administrative-assistant-sk-oasis-outsourcing",
        "*Operations and Administration Assistant* at WUSC - https://www.fuzu.com/kenya/jobs/operations-and-administration-assistant-wusc-nairobi",
        "*Personal Assistant, Finance & Operations Administrator* at The Nairobi Women's Hospital - https://www.fuzu.com/kenya/jobs/personal-assistant-finance-operations-administrator",
    ],
}


async def fetch_jobs(job_title: str) -> Optional[List[str]]:
    """
    Fetches job listings. 
    Currently uses an internal mock database with improved search logic.
    """
    logging.info(f"Fetching mock jobs for query: '{job_title}'")
    
    search_term = job_title.lower()
    best_match_key = None
    for key in MOCK_JOBS:
        if search_term in key or key in search_term:
            best_match_key = key
            break
            
    if best_match_key:
        return MOCK_JOBS[best_match_key]
    
    logging.warning(f"No mock job category found for '{job_title}'")
    return []
