import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Smarter Keyword Mapping ---
# This dictionary helps the bot understand related terms.
INTEREST_KEYWORDS = {
    "it": ["it", "software", "developer", "tech", "engineer", "soc", "support", "ai engineer", "automation", "ict", "software development","systems administrator","network","fullstack","frontend","backend","devops"],
    "sales": ["sales", "business development", "retail", "agent", "marketing"],
    "admin": ["admin", "assistant", "clerical", "office support", "hr", "human resource", "people", "culture", "receptionist"],
    "accountant": ["accountant", "finance", "audit", "bookkeeping", "accounts"],
    "driver": ["driver", "driving", "logistics", "rider"],
    "intern": ["intern", "internship", "trainee"],
    "attachment": ["attachment", "attach", "attachment", "attach"],
    "technical": ["technical", "tech", "engineering", "it", "electrical","mechanical","civil","plumbing", "construction","welder", "fabrication","construction","artisan"],
    "hospitality": ["hospitality", "hotel", "restaurant", "catering", "food service", "waiter", "chef", "barista", "bartender", "caterer", "interior", "designer"]
}

# --- Mock Database of Real, Curated Jobs ---
MOCK_JOBS_LIST = [
    # Tech
    "*Software Developer* at Buy Domain Kenya - https://www.brightermonday.co.ke/listings/software-developer-4nznmv",
    "*Senior Full Stack Software Engineer* at Bluecollar Technologies - https://www.brightermonday.co.ke/listings/senior-full-stack-software-engineer-d8kngv",
    "*Software Developer* at Enfinite Solutions Limited - https://www.brightermonday.co.ke/listings/software-developer-20e0nq",
    "*IT Support* at Reeds Africa Consult* - https://www.myjobmag.co.ke/job/school-it-support-reeds-africa-consult",
    "*Core Network Support Engineer - Packet Core* at Safaricom Kenya - https://www.myjobmag.co.ke/job/core-network-support-engineer-packet-core-safaricom-kenya-2",
    "*Senior Systems and Support Engineer* at Poa Internet- https://www.myjobmag.co.ke/job/senior-systems-and-support-engineer-poa-internet-1",
    "*Tier 2 Security Operations Centre (SOC) Analyst* at NTT Ltd - https://www.myjobmag.co.ke/job/tier-2-security-operations-centre-soc-analyst-ntt-ltd-3",
    "*Back-End Developer* at Corporate Staffing Services Ltd - https://www.brightermonday.co.ke/listings/flutter-back-end-developer-84e46p",
    "*AI Automation Enginee* at Silicon Savannah Services LLC - https://www.brightermonday.co.ke/listings/ai-automation-engineer-wpv2xj",
    "*FullStack Developer* at Prodvestor - https://www.brightermonday.co.ke/listings/fullstack-developer-7we8pq",
    "*IT Service Desk Analyst* at BrighterMonday Consulting - https://www.brightermonday.co.ke/listings/it-service-desk-analyst-5de4qr",
    "*Frontend Developer (Web)* at Prestine HR-Engine Ltd- https://www.brightermonday.co.ke/listings/frontend-developer-web-mg2zeq",
    "*IT Officer* at ACCOR - https://www.fuzu.com/job?page=1&filters[job_id]=746507",
    "*Junior Software Developer* at International Livestock Research Institute (ILRI) - https://www.fuzu.com/job?page=1&filters[job_id]=746512",
    "*Head of ICT, Data Systems and Digital Transformation* at International Livestock Research Institute (ILRI) - https://www.fuzu.com/job?filters[job_id]=743338&page=1",
    "*System Administrator* at Sipranda Capital Limited- https://www.fuzu.com/job?filters[job_id]=742815&page=1",
    "*DevOps Engineer* at Confidential Co.- https://www.linkedin.com/jobs/view/4293733758/?alternateChannel=search&eBP=NOT_ELIGIBLE_FOR_CHARGING&refId=5vJZIbb2tEMN1fbaNREN6A%3D%3D&trackingId=k1qFuRL2SSijvMSAfcB%2FbQ%3D%3D",
    "*Systems Administrator* at Cognativ. - https://careers.cognativ.com/apply/148293bb-07c2-4a32-b997-68dcdfb3a24d",


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
    "*Executive Assistant* at INUA AI - https://www.myjobmag.co.ke/job/executive-assistant-inua-ai",
    "*Human Resource Manager* at ADORA PRODUCTS LIMITED - https://www.brightermonday.co.ke/listings/human-resource-manager-xp08qj",
    "*HR Generalist* at  Manufacturing Industry - https://www.brightermonday.co.ke/listings/hr-generalist-manufacturing-industry-r8p8vx",
    "*HR Manager* at Elite Sounds Ltd - https://www.brightermonday.co.ke/listings/position-title-hr-manager-r8prxq",
    "*HR Officer* at Quality Meat Packers Ltd. - https://www.brightermonday.co.ke/listings/hr-officer-encouraging-female-candidates-7wejq5",
    "*SENIOR MANAGER-PEOPLE & CULTURE* Corporate Staffing Services Ltd - https://www.brightermonday.co.ke/listings/senior-manager-people-culture-4nz4k9",
    "*People and Culture Officer III* at International Livestock Research Institute (ILRI) -https://www.fuzu.com/job?filters[job_id]=745143&page=1",



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
    "*FIELD TECHNICIAN - POWER & INFRASTRUCTURE MAINTENANCE* at Broadband Communication Networks Ltd - https://www.brightermonday.co.ke/listings/field-technician-power-infrastructure-maintenance-q2jzqe",
    "*Fiber Technician* at NAMONET SOLUTION LIMITED - https://www.brightermonday.co.ke/listings/fiber-technician-wp4d4k",
    "*Construction Skilled Worker - Plumber* at Victory Farms - https://www.myjobmag.co.ke/job/construction-skilled-worker-plumber-victory-farms",
    "*Artisan III, (Plumber/Pipe Fitter)* at Kwale County Government - https://www.myjobmag.co.ke/job/artisan-iii-plumber-pipe-fitter-3-posts-kwale-county-government",
    "*Welder* at Brookhill Projects - https://www.myjobmag.co.ke/job/welder-brookhill-projects"



    
    #Hospitality
    "*Gym Instructor* at Enchula Resort - https://www.myjobmag.co.ke/job/gym-instructor-enchula-resort",
    "*Masseuse* at Enchula Resort - https://www.myjobmag.co.ke/job/masseuse-enchula-resort",
    "*Waiter/Waitress* at Sarova Hotels - https://www.myjobmag.co.ke/job/waiter-waitress-sarova-hotels",
    "*Housekeeping Supervisor* at Kempinski - https://www.myjobmag.co.ke/job/housekeeping-supervisor-kempinski",
    "*Front Office Assistant* at Marriott - https://www.myjobmag.co.ke/job/front-office-assistant-marriott",
    "*Waiter* at Zale Lounge - https://www.myjobmag.co.ke/job/waiter-3-zale-lounge",
    "*Food and Beverage Supervisor* at Emerge Egress Consulting - https://www.myjobmag.co.ke/job/food-and-beverage-supervisor-eastern-emerge-egress-consulting",
    "*Interior Design Specialist * Prestige Bluestar Holdings Ltd - https://www.myjobmag.co.ke/job/interior-design-specialist-prestige-bluestar-holdings-ltd",
    "*Interior Design Assistant* at Fast Choice - https://www.myjobmag.co.ke/job/interior-design-assistant-fast-choice-1",


    #Internship and attachements
    "*Intern - Practice and Policy Research* at UN-Habitat - https://www.fuzu.com/job?filters[term]=INTERN&filters[job_id]=747971&page=1",
    "*Intern - Logistics / Supply Chain Intern* at MSVL GROUP - https://www.fuzu.com/job?filters[term]=INTERN&filters[job_id]=743086&page=1",
    "*Intern - Better Migration Management (BMM) Programme* at GIZ KE - https://www.fuzu.com/job?filters[term]=INTERN&filters[job_id]=746825&page=2",
    "*Intern - Information Systems Auditor at d.light SOLAR- https://www.fuzu.com/job?filters[term]=INTERN&filters[job_id]=746800&page=2",
    "*Intern - Public Health, Social Sciences, Community Development, Project Management* at EcoBana - https://www.fuzu.com/job?filters[term]=INTERN&filters[job_id]=747969&page=2",

]

async def fetch_jobs(user_interest: str) -> list[str] | None:
    """
    Fetches job listings from the mock database using an intelligent keyword search.
    """
    logging.info(f"Fetching jobs for user interest: '{user_interest}'")
    user_interest = user_interest.lower()
    found_jobs = []
    
    # Determine the list of keywords to search for
    search_terms = INTEREST_KEYWORDS.get(user_interest, [user_interest])
    
    logging.info(f"Using smart search terms: {search_terms}")

    for job in MOCK_JOBS_LIST:
        for term in search_terms:
            if term in job.lower():
                found_jobs.append(job)
                break # Avoid adding the same job multiple times
                
    if not found_jobs:
        logging.warning(f"No jobs found for interest: '{user_interest}' with terms: {search_terms}")
        return None
        
    return found_jobs

