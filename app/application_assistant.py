import asyncio
import logging
from typing import Tuple, Optional, Dict, Any
from . import models, ai_client, whatsapp_client
from .resume_builder import format_cv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_and_draft(session: models.UserSession, job: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Orchestrates the AI-powered analysis and drafting for a specific job application.

    This function acts as the "brain" of the Application Assistant Agent. It chains
    multiple AI calls to provide comprehensive feedback and a drafted cover letter.

    Args:
        session: The user's current session object, containing their CV data.
        job: The job dictionary object the user is interested in.

    Returns:
        A tuple containing the formatted report for the user and a success flag.
    """
    if not session.resume_data or not job.get("description"):
        return "Sorry, I'm missing some information (either your CV or the job description) to proceed.", False

    cv_text = format_cv(session.resume_data)
    job_description = job.get("description", "")
    company_name = job.get("title", "").split(" at ")[-1] # Simple way to guess company name
    job_title = job.get("title", "")

    await whatsapp_client.send_whatsapp_message(
        session.phone_number, 
        f"Got it! I'm now analyzing your CV against the '{job_title}' role. This might take a moment..."
    )

    # --- Perform AI tasks in parallel for efficiency ---
    try:
        feedback_task = ai_client.optimize_resume(cv_text, job_description)
        cover_letter_task = ai_client.generate_cover_letter(cv_text, company_name, job_title, job_description)

        # Await both AI calls to complete
        feedback, cover_letter = await asyncio.gather(feedback_task, cover_letter_task)

        if not feedback or not cover_letter:
            return "Sorry, I had trouble connecting with the AI to generate the full analysis. Please try again in a moment.", False

        # --- Format the final report for the user ---
        report = (
            f"✅ *Analysis Complete for '{job_title}'*\n\n"
            "Here is my professional advice on how to best position yourself for this role:\n\n"
            "*--- CV OPTIMIZATION TIPS ---*\n"
            f"{feedback}\n\n"
            "*--- DRAFT COVER LETTER ---*\n"
            f"{cover_letter}"
        )
        
        return report, True

    except Exception as e:
        logging.error(f"Error in application assistant agent: {e}", exc_info=True)
        return "Sorry, an unexpected error occurred while analyzing your application. Please try again later.", False
