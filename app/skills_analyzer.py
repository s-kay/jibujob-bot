# app/skills_analyzer.py
import logging
import re
from typing import Tuple, List, Optional
from . import models, ai_client, resume_builder

logger = logging.getLogger(__name__)

def _parse_skills_from_response(ai_response: str) -> List[str]:
    """A simple parser to extract skills from a formatted AI response."""
    skills = []
    # Find lines that start with a number, asterisk, or dash, followed by a bolded skill
    pattern = r"[\d\*\-]+\.\s+\*\*(.*?)\*\*"
    matches = re.findall(pattern, ai_response)
    if matches:
        return [skill.strip() for skill in matches]
    return skills

async def analyze_skills_gap(session: models.UserSession, job_description: str) -> Tuple[str, Optional[List[str]]]:
    """
    Analyzes the user's CV against a job description to find skill gaps using a live AI call.
    """
    cv_text = resume_builder.format_cv(session.resume_data)

    system_prompt = (
        "You are KaziLeo, an expert AI career coach in Kenya. Your task is to perform a skills gap analysis. "
        "Analyze the user's CV and the provided job description. "
        "Your response MUST contain a friendly summary followed by a numbered list of the top 3-5 most important skills required by the job that are missing from the CV. "
        "Format the missing skills in the list like this: `1. **Skill Name**`. "
        "Conclude by encouraging them to learn these skills."
    )

    user_prompt = (
        f"Here is my CV:\n---CV START---\n{cv_text}\n---CV END---\n\n"
        f"Here is the job description I am targeting:\n---JOB START---\n{job_description}\n---JOB END---\n\n"
        "Please perform a skills gap analysis and tell me what key skills I am missing for this role."
    )

    ai_response = await ai_client.get_ai_response(system_prompt, user_prompt)

    if not ai_response:
        # Handle case where the AI client returned an error
        return "Sorry, I was unable to analyze the skills gap at this moment. Please try again later.", None

    missing_skills = _parse_skills_from_response(ai_response)
    
    return ai_response, missing_skills
