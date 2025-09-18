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
        },
        {
            "title": "Senior Software Architect",
            "keywords": ["architect", "software", "engineer", "senior"],
            "link": "https://egjd.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/747?utm_source=MyJobMag&utm_medium=jobboard"
        },
        {
            "title": "Senior Tax Advisor",
            "keywords": ["tax", "advisor", "senior", "finance"],
            "link": "https://careers.ey.com/ey/job/Nairobi-Senior-Tax-Advisor-International-Tax-&-Transaction-Services-00100/1248423901/?feedId=337401"
        },
        {
            "title": "Engineer - RAN",
            "keywords": ["engineer", "ran", "radio access network", "telecommunications"],
            "link": "https://egjd.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/911"
        },
        {
            "title": "HR Manager",
            "keywords": ["hr", "human resources", "manager", "people", "culture"],
            "link": "https://mwananchicredit.com/careers/hr-manager/?utm_source="
        },
        {
            "title": "Admin Assistant",
            "keywords": ["admin", "assistant", "office", "support"],
            "link": "https://www.corporatestaffing.co.ke/job/admin-assistant-ngo-job-global-methane-hub/"
        },
        {
            "title": "Senior Analyst",
            "keywords": ["senior", "analyst", "data", "analytics"],
            "link": "https://www.linkedin.com/jobs/view/4289572864/?alternateChannel=search&eBP=CwEAAAGZVfVem5mQyyeDsogcCamkW_WuDGk1ybErFVQ4ogoAXaqik-dN4Z44d7hetl7fFVNdi02XYMhOjsIaPqs8A_yWNv5ULX8C0eNSRVAoozHYuZmarrwZ1VmAQPXBtSp3anidN_hc7S0XGUOF8O1hg_PUa5EUmGqyG4yt0qe6RjBm0cDlVochBT3e1H2NqSY-7wIyIbawZWENLZWUkl_cwV0wuXxEdTPh06OTaqJsolEs69AGXTCbPM8QDy7HM_qscTi5H1BPDzCfK7dOBO4C3Sy_YWUm8TG4pAyXhFTJZvB40AvcZQKAhX2U6w-70MiRm-wQkDuiHJwcAjE-jLA90Q9JW1ZUXLZvRZzdw2m99SOTkfiJij-QESYyLCjUbETboTET2VgcozaR52Wh7q303nR9S1waoxP_KfAea937NwOrixUjDWsU_7moVWZ6EnSsiX_30TRgY8M1k9Ly86XyB50UmzWebE4VlhU40yc91r3knQ7wZDCVRg0gqVa2LaE_5-N8IBTanacUwvnulzJU&refId=Lf0MuoYEs+PxBu3i%2FqHCLA%3D%3D&trackingId=PFzZp+VYkDonGI2XQFKudQ%3D%3D"
        },
        {
            "title": "HR Recruiter",
            "keywords": ["hr", "recruiter", "human resources", "talent acquisition"],
            "link": "https://www.corporatestaffing.co.ke/job/recruiter-job-rls/"
        },
        {
            "title": "Video Producer",
            "keywords": ["video", "production", "filmmaking", "editing", "journalist"],
            "link": "https://careers.bbc.co.uk/job/Senior-Journalist-Video-Producer-Nairobi/28236-en_GB"
        },
        {
            "title": "Business Development Manager",
            "keywords": ["business", "development", "manager", "sales", "marketing", "business development"],
            "link": "https://www.linkedin.com/jobs/view/4299549794/?alternateChannel=search&eBP=CwEAAAGZVfVZWIGky1oeel4A-2Iq5akyRc_aZJwdeFzW5nRPu0claYaGsQMGVNNeS18XPNCY978-wGYiSyUgs80Iaw_G69eACSbh6nK0HA6wUIDEQ0f1K5Dfbma0YS_oocgagusmxcjXzRJr3Q98pciWXMaK4LHlm1KdRN38VEVTalczs2WYNcoOFUx1p3MsZ_L5_DHTePcyS04VyzRwBjTe-gThA5s-TbLXqHizHf_9ZzWFTKsF0FmV99Znbx56ZwfWFjc-E8WcIVy-zRdMO6oL2nOFirR-h1cu3Vhs7w80svn9dzyfimxaeAmbnUSwUR227XGgxZiED9k7zYpov2qdLpcensT5U5Y0r61mg3-8OCQzDKPqG_mEfwjwe-WVwDFTjqquzrR2zmTE2rL2CMQQme2xzQmR166zQ6PEYWjr65Dk4th-KFoeQp9DTpWcO17E34UqqeiQ7AdXkB5UE96tuiuwwFaViml2I9JYMsD3pTwY68mtR3M7b2s&refId=nFrXWPtXfQkk1fjN5Ilgug%3D%3D&trackingId=t%2FGQw5uZYkfH4QN4qp0l1Q%3D%3D"
        },
        {
            "title": "Customer Service Specialist",
            "keywords": ["customer service", "support", "client relations", "communication"],
            "link": "https://www.linkedin.com/jobs/view/4299929748/?alternateChannel=search&eBP=CwEAAAGZVe6ZeakeEAb_PS38k3Nvn3-ijNkDC_KfSn7zyplpkGPds_h9VlUaYcY5q_kE50shRRyH4_-Ag12pwciN2xLGXfiAWOrmomX12-wcX-TETnkjp7KN4mtB6D4M4BPEy7_fnJQJE5NR2l4g0Aqn-9nP-wzCtwMs243BzLeiFlEFO6fQw-x-hG3x1BnGlNRBSztHxc4ZQ-WLy7BhMyUUnYxuXFXLj-gjObrw9U4W4VZvR3WuXmXLTV5jBNMIBpJRwA-TIgCvgxu0JxVfYQ5-HPml1osVa8GX5Vuw9iTkUW2gUGn9yRxBgt3HN3oOUFJJNo5uWanCLfCKmD1cq_hwKRmk5ZfKMBHzOGN4Ey75W1himDOOyVzaBYfuhVmdr_fJ89ueaTQG5S94A10bXkhXvj1ULS_ZbcMoRG7399HiDKvOHVekLurZptSygEQz7SNQpmB_IK5lIZwEa3QiVFYc7Byu8e4sKYFt5pREwk1c4xIQKjgSOqgPZCzBnH-zRUFeho6yKOOgRC4sGVgleWvAYlWzHM5p0w&refId=z0N%2FU1XC02nhHbczsUw27g%3D%3D&trackingId=+qyA%2FBEXrtjjg7xnjxKw7A%3D%3D"
        },
        {
            "title": "Head of Finance",
            "keywords": ["finance", "financial management", "budgeting", "accounting"],
            "link": "https://www.corporatestaffing.co.ke/job/head-of-finance-job-rls/"
        },
        {
            "title": "Chief Manager – System Administration & Database Management",
            "keywords": ["database", "system administrator", "it", "infrastructure", "systems"],
            "link": "https://erecruitment.kra.go.ke/login"
        },
        {
            "title": "ICT Officer",
            "keywords": ["ict", "information technology", "it support", "technical"],
            "link": "https://www.fuzu.com/jobs/748792/application"
        },
        {
            "title": "Systems Administrator",
            "keywords": ["system administrator", "it", "ict"],
            "link": "https://www.fuzu.com/jobs/750931/application"
        },
        {
            "title": "Chef de Partie",
            "keywords": ["chef", "cook", "catering", "hospitality"],
            "link": "https://jobs.smartrecruiters.com/AccorHotel/744000082371335-chef-de-partie"
        },
        {
            "title": "Intern",
            "keywords": ["internship", "intern"],
            "link": "https://www.fuzu.com/kenya/jobs/intern-nairobi"
        },
        {
            "title": "Intern - Urban Energy",
            "keywords": ["internship", "intern", "energy", "urban"],
            "link": "https://careers.un.org/jobSearchDescription/264144?language=en"
        },
        {
            "title": "Intern - Project Management",
            "keywords": ["project management", "internship", "intern"],
            "link": "https://careers.un.org/jobSearchDescription/264148?language=en"
        },
        {
            "title": "Clinical Nurse",
            "keywords": ["nursing", "healthcare", "clinical", "nurse"],
            "link": "https://aku.taleo.net/careersection/ex/jobdetail.ftl?job=250002KU&lang=en"
        },
        {
            "title": "L1 IT Desktop Support ",
            "keywords": ["Desktop", "support", "it"],
            "link": "https://applybpo.com/view-job-posting/10669"
        },
        {
            "title": "Project Manager",
            "keywords": ["project management", "project", "manager"],
            "link": "https://bfaglobal.com/careers/project-manager-bfa-global/"
        },
        {
            "title": "Programme Officer",
            "keywords": ["programme management", "project", "officer"],
            "link": "https://www.web.civicus.org/Programme-Officer"
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

