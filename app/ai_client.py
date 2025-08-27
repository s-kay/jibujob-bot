# app/ai_client.py
import logging
import httpx
import re
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
    
    async with httpx.AsyncClient(timeout=60.0) as client:
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
        "Focus on keywords, action verbs, and quantifiable achievements. Keep the tone positive and encouraging."
    )
    user_prompt = (
        f"My CV:\n{cv_text}\n\nJob Description:\n{job_description}\n\nPlease give me 3-4 specific suggestions to improve my CV for this job."
    )
    
    feedback = await get_ai_response(system_prompt, user_prompt)
    if feedback:
        return f"*--- AI-Powered Feedback ---*\n\n{feedback}"
    return None # Return None if there was an error
