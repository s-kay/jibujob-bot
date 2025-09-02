# app/ai_client.py
import logging
import httpx
from typing import Optional
from .config import settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
logger = logging.getLogger(__name__)

async def get_ai_response(system_prompt: str, user_prompt: str) -> Optional[str]:
    """
    A generic function to get a response from the Gemini AI model.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not set. Cannot call AI.")
        return None

    headers = {"Content-Type": "application/json"}
    params = {"key": settings.GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }
    
    async with httpx.AsyncClient(timeout=90.0) as client: # Increased timeout for potentially longer tasks
        try:
            response = await client.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            
            candidate = data.get("candidates", [{}])[0]
            content = candidate.get("content", {}).get("parts", [{}])[0]
            feedback = content.get("text")
            
            if not feedback:
                logger.error("AI response was empty or malformed.")
                return "Sorry, the AI couldn't generate a response at this moment."
            return feedback
        except httpx.HTTPStatusError as e:
            logger.error(f"Error from AI API: {e.response.text}")
            return "Sorry, I'm having trouble connecting to the AI service right now."
        except Exception as e:
            logger.error(f"An unexpected error occurred while calling AI API: {e}")
            return "An unexpected error occurred. Please try again."

async def optimize_resume(cv_text: str, job_description: str) -> Optional[str]:
    """
    Uses the generic AI client to provide resume optimization suggestions.
    """
    system_prompt = (
        "You are KaziLeo, a friendly AI career coach from Kenya. Your task is to help a user optimize their CV for a specific job. "
        "Analyze the CV and job description. Give 3-4 clear, actionable suggestions in a numbered list. "
        "Focus on keywords, action verbs, and quantifiable achievements. Keep the tone positive and encouraging. "
        "**Important: Your entire response must be under 3000 characters.**"
    )
    user_prompt = (
        f"My CV:\n{cv_text}\n\nJob Description:\n{job_description}\n\nPlease give me 3-4 specific suggestions to improve my CV for this job."
    )
    
    feedback = await get_ai_response(system_prompt, user_prompt)
    if feedback:
        return f"*--- AI-Powered Feedback ---*\n\n{feedback}"
    return None

async def rewrite_cv_sections(cv_text: str, job_description: str, feedback: str) -> Optional[str]:
    """
    Uses the AI to rewrite the 'Professional Summary' and 'Work Experience' sections of a CV
    based on the provided feedback.
    """
    system_prompt = (
        "You are an expert CV writer. Your task is to rewrite the 'Professional Summary' and 'Work Experience' sections of a user's CV. "
        "Use the original CV, the target job description, and the provided AI feedback to make the new sections more impactful and keyword-rich. "
        "Your response MUST ONLY contain the rewritten 'Professional Summary' and 'Work Experience' sections under their respective headings. Do not add any extra conversation or commentary."
    )
    user_prompt = (
        f"Original CV:\n{cv_text}\n\n"
        f"Target Job Description:\n{job_description}\n\n"
        f"AI Feedback to apply:\n{feedback}\n\n"
        "Please rewrite the 'Professional Summary' and 'Work Experience' sections based on all the information above."
    )
    
    rewritten_sections = await get_ai_response(system_prompt, user_prompt)
    if rewritten_sections:
        return f"*--- AI-Suggested Rewrite ---*\n\nHere are the updated sections for your CV:\n\n{rewritten_sections}"
    return None


async def generate_cover_letter(cv_data: str, company: str, role: str, job_description: str) -> str | None:
    """Uses a generative AI to create a tailored cover letter."""
    system_prompt = (
        "You are an expert Kenyan career coach named KaziLeo. Your task is to write a professional, concise, and impactful cover letter for a user applying for a job."
    )
    user_prompt = f"""
    **User's CV:**
    ---
    {cv_data}
    ---

    **Job Details:**
    - Company: {company}
    - Role: {role}
    - Job Description: {job_description}

    **Instructions:**
    1.  Start with a professional greeting addressing the hiring manager (or "Hiring Team" if no name is available).
    2.  In the first paragraph, clearly state the position being applied for and where it was seen (if applicable, otherwise omit).
    3.  In the body paragraphs, highlight 2-3 key skills or experiences from the user's CV that directly match the requirements in the job description. Use strong action verbs and quantify achievements.
    4.  Keep the tone professional but enthusiastic.
    5.  End with a strong closing statement expressing excitement for the opportunity and a call to action.
    6.  Use a professional sign-off with the user's full name from their CV.
    7.  The entire cover letter must be under 3000 characters.
    8.  Do not include placeholders like "[Your Contact Info]". The body of the letter is sufficient.
    """
    return await get_ai_response(system_prompt, user_prompt)
