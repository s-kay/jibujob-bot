# app/job_client.py
import httpx
import logging
from typing import List, Optional

# --- Uncategorized Mock Job Database with REAL Data ---
# This is now a single list, allowing for more flexible keyword searching.
MOCK_JOBS_LIST = [
    # Software Developer
    "*Software Developer* at Buy Domain Kenya - https://www.brightermonday.co.ke/listings/software-developer-4nznmv",
    "*Senior Full Stack Software Engineer* at Bluecollar Technologies - https://www.brightermonday.co.ke/listings/senior-full-stack-software-engineer-d8kngv",
    "*Software Developer* at Enfinite Solutions Limited - https://www.brightermonday.co.ke/listings/software-developer-20e0nq",
    
    # Accountant
    "*Accountant* at Burhani Engineers Ltd - https://www.fuzu.com/kenya/jobs/accountant-burhani-engineers-ltd",
    "*Project Accountant* at Tatu City - https://www.fuzu.com/kenya/jobs/project-accountant-tatu-city",
    "*Senior Accountant* at Kibabii University - https://www.fuzu.com/kenya/jobs/senior-accountant-kibabii-university-2",
    
    # Sales
    "*Sales Manager* at Crystal Recruitment - https://www.brightermonday.co.ke/listings/sales-manager-vx8vjp",
    "*Wholesale Laptop Sales Agent* at Kolm Solutions - https://www.brightermonday.co.ke/listings/wholesale-laptop-sales-agent-p5p8w5",
    "*Van Salesman* at Focused Human Resource Solutions - https://www.brightermonday.co.ke/listings/van-salesman-q2n5wk",
    
    # Admin
    "*Administrative Assistant* at Oasis Outsourcing - https://www.fuzu.com/kenya/jobs/administrative-assistant-sk-oasis-outsourcing",
    "*Operations and Administration Assistant* at WUSC - https://www.fuzu.com/kenya/jobs/operations-and-administration-assistant-wusc-nairobi",
    "*Personal Assistant, Finance & Operations Administrator* at The Nairobi Women's Hospital - https://www.fuzu.com/kenya/jobs/personal-assistant-finance-operations-administrator",
]


async def fetch_jobs(job_title: str) -> Optional[List[str]]:
    """
    Fetches job listings by performing a keyword search on the mock database.
    """
    logging.info(f"Fetching mock jobs for keyword: '{job_title}'")
    
    search_term = job_title.lower()
    
    # Find all jobs in the list that contain the search term
    found_jobs = [job for job in MOCK_JOBS_LIST if search_term in job.lower()]
    
    if not found_jobs:
        logging.warning(f"No mock jobs found for keyword '{job_title}'")
        return []
        
    return found_jobs
