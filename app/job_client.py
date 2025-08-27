# app/job_client.py
import httpx
import logging
from typing import List, Optional
from .config import settings

logger = logging.getLogger(__name__)

# The base URL for the job data aggregator API
JOB_API_URL = "https://jobdataapi.com/api/jobs/"

async def fetch_jobs(job_title: str, country_code: str = "KE") -> Optional[List[str]]:
    """
    Fetches job listings from the jobdataapi.com aggregator.

    Args:
        job_title: The job role to search for (e.g., "accountant").
        country_code: The ISO 3166-1 alpha-2 country code (e.g., "KE" for Kenya).

    Returns:
        A list of formatted job strings or None if an error occurs.
    """
    if not settings.JOB_API_KEY:
        logger.warning("JOB_API_KEY is not set. Skipping API call and returning mock data.")
        # Return a single mock result so the flow can be tested without a real key
        if "developer" in job_title.lower():
            return ["Mock: Senior Developer at KaziCorp - https://jobs.example.com/live1"]
        return None

    headers = {
        "Authorization": f"Api-Key {settings.JOB_API_KEY}"
    }
    params = {
        "query": job_title,
        "country_code": country_code,
        "page_size": 5 # Fetch 5 results at a time
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(JOB_API_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get("results"):
                logger.info(f"No jobs found for query: {job_title}")
                return []

            # Format the results into a user-friendly list of strings
            formatted_jobs = []
            for job in data["results"]:
                company = job.get("company", {}).get("name", "N/A")
                location = job.get("location", "N/A")
                title = job.get("title", "N/A")
                # We can't get a direct link, so we'll just present the info
                formatted_jobs.append(f"{title} at {company} ({location})")
            
            return formatted_jobs

        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching jobs from API: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching jobs: {e}")
            return None
