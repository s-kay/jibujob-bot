# app/job_client.py
import httpx
import logging
from typing import List, Optional

# --- Uncategorized Mock Job Database with REAL Data ---
# This is now a single list, allowing for more flexible keyword searching.
MOCK_JOBS_LIST = [
    # Tech
    "*Software Developer* at Buy Domain Kenya - https://www.brightermonday.co.ke/listings/software-developer-4nznmv",
    "*Senior Full Stack Software Engineer* at Bluecollar Technologies - https://www.brightermonday.co.ke/listings/senior-full-stack-software-engineer-d8kngv",
    "*Software Developer* at Enfinite Solutions Limited - https://www.brightermonday.co.ke/listings/software-developer-20e0nq",
    "*IT Support* at Reeds Africa Consult* - https://www.myjobmag.co.ke/job/school-it-support-reeds-africa-consult",
    "*Core Network Support Engineer - Packet Core* at Safaricom Kenya - https://www.myjobmag.co.ke/job/core-network-support-engineer-packet-core-safaricom-kenya-2",
    "*Senior Systems and Support Engineer* at Poa Internet- https://www.myjobmag.co.ke/job/senior-systems-and-support-engineer-poa-internet-1",
    "*Tier 2 Security Operations Centre (SOC) Analyst* at NTT Ltd - https://www.myjobmag.co.ke/job/tier-2-security-operations-centre-soc-analyst-ntt-ltd-3",

    # Accountant
    "*Accountant* at Burhani Engineers Ltd - https://www.fuzu.com/kenya/jobs/accountant-burhani-engineers-ltd",
    "*Project Accountant* at Tatu City - https://www.fuzu.com/kenya/jobs/project-accountant-tatu-city",
    "*Senior Accountant* at Kibabii University - https://www.fuzu.com/kenya/jobs/senior-accountant-kibabii-university-2",
    
    # Sales
    "*Sales Manager* at Crystal Recruitment - https://www.brightermonday.co.ke/listings/sales-manager-vx8vjp",
    "*Wholesale Laptop Sales Agent* at Kolm Solutions - https://www.brightermonday.co.ke/listings/wholesale-laptop-sales-agent-p5p8w5",
    "*Van Salesman* at Focused Human Resource Solutions - https://www.brightermonday.co.ke/listings/van-salesman-q2n5wk",
    "*Marketing & Content Development Lead* at ClerkMaster Consulting - https://www.myjobmag.co.ke/job/marketing-content-development-lead-clerkmaster-consulting",
    "*Sales Team Lead* at Bolt - https://www.myjobmag.co.ke/job/sales-team-lead-bolt-7",


    # Admin
    "*Administrative Assistant* at Oasis Outsourcing - https://www.fuzu.com/kenya/jobs/administrative-assistant-sk-oasis-outsourcing",
    "*Operations and Administration Assistant* at WUSC - https://www.fuzu.com/kenya/jobs/operations-and-administration-assistant-wusc-nairobi",
    "*Personal Assistant, Finance & Operations Administrator* at The Nairobi Women's Hospital - https://www.fuzu.com/kenya/jobs/personal-assistant-finance-operations-administrator",
    "*Operations Assistant* at EmpowerU HR Solutions- https://www.myjobmag.co.ke/job/operations-assistant-empoweru-hr-solutions",
    "*Executive Assistant* at INUA AI - https://www.myjobmag.co.ke/job/executive-assistant-inua-ai"


    #Technical
    "*Repair Technician* at ENGIE - https://www.fuzu.com/job?filters[term]=electronics&filters[country_id]=1&filters[job_id]=746500&page=1",
    "*Electrical Technician* at MSVL Group - https://www.fuzu.com/job?filters[term]=electronics&filters[country_id]=1&filters[job_id]=744929&page=1",
    "*Electrical Technician Intern* at Royal Mabati Factory Limited - https://www.fuzu.com/job?filters[term]=electronics&filters[country_id]=1&filters[job_id]=746554&page=1",
    "*Shift Operator* at Globeleq - https://www.fuzu.com/job?filters[term]=mechanic&filters[country_id]=1&filters[job_id]=745196&page=1",
    "*Automotive Technician* at AutoXpress Limited - https://www.fuzu.com/job?filters[term]=mechanic&filters[country_id]=1&filters[job_id]=727352&page=1",
    "*Mechanical Engineer - Plumbing* at Trident Plumbers - https://www.fuzu.com/job?filters[term]=mechanic&filters[country_id]=1&filters[job_id]=744892&page=1",
    "*Tuk-Tuk Drivers* at Mini Group - https://www.fuzu.com/job?filters[term]=mechanic&filters[country_id]=1&filters[job_id]=746545&page=1",
    "*Service Technician* at Ecolab - https://www.fuzu.com/job?filters[country_id]=1&filters[term]=mechanic&filters[job_id]=744109&page=2",
    "*Underwriting and Claims Assistant* at MNS Risk and Insurance Brokers Ltd - https://www.myjobmag.co.ke/job/underwriting-and-claims-assistant-mns-risk-and-insurance-brokers-ltd",
    "*Crane Operator* at Safal Group - https://www.myjobmag.co.ke/job/crane-operator-safal-group-4",

    #Hospitality
    "*Gym Instructor* at Enchula Resort - https://www.myjobmag.co.ke/job/gym-instructor-enchula-resort",
    "*Masseuse* at Enchula Resort - https://www.myjobmag.co.ke/job/masseuse-enchula-resort",
    "*Waiter/Waitress* at Sarova Hotels - https://www.myjobmag.co.ke/job/waiter-waitress-sarova-hotels",
    "*Housekeeping Supervisor* at Kempinski - https://www.myjobmag.co.ke/job/housekeeping-supervisor-kempinski",
    "*Front Office Assistant* at Marriott - https://www.myjobmag.co.ke/job/front-office-assistant-marriott"
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
