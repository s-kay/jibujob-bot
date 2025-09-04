# app/resume_builder.py
from typing import Tuple, Optional # 
from . import models
import asyncio
from app.file_handler import upload_text_as_file

# --- ATS-Friendly Questions ---
# These questions are designed to prompt users for specific, keyword-rich, and quantifiable information.
CV_QUESTIONS = [
    ("full_name", "Of course. Let's build a CV that gets noticed. First, what is your full name?"),
    ("email", "Got it. What's a professional email address for employers to contact you? (e.g., jane.doe@email.com)"),
    ("phone", "Perfect. And your phone number?"),
    ("links", "Great! Please share any professional links you'd like to include (e.g., LinkedIn, portfolio website, Github)."),
    ("summary", 
     "Next, let's write a powerful Professional Summary. Describe your main role and top achievement. "
     "For example: 'Detail-oriented Accountant with 3 years of experience who saved a company KES 500,000 by optimizing budgets.'"),
    ("experience", 
     "Now for your Work Experience. Please list your most recent job title, the company, and one key achievement with a number. "
     "For example: 'Accountant, XYZ Corp (2022-2024) - Reduced monthly reporting errors by 15%.'\n\n(Type 'skip' if you have no formal work experience)"),
    ("education", 
     "Almost done! What is your highest qualification and where did you get it? "
     "For example: 'Bachelor of Commerce in Finance, University of Nairobi, 2021-2025'"),
    ("certifications",
     "Do you have any relevant certifications? If so, please list them. "
     "For example: 'Certified Public Accountant (CPA), Project Management Professional (PMP)'"),
    ("Projects",
     "Have you worked on any notable projects? If so, please describe them briefly. "
     "For example: 'Led a team to develop a budgeting tool that reduced costs by 20%.'"),
    ("skills", 
     "Great. Now, list your most important technical and soft skills, separated by commas. Think about keywords from job descriptions. "
     "For example: 'QuickBooks, Financial Reporting, Budgeting, Microsoft Excel, Communication, Problem-Solving'"),
    ("referees",
     "Finally, do you have any referees you'd like to include? If so, please provide their names and contact information."
     "For example: 'John Doe, johndoe@email.com, +254712345678'"),

]


def format_cv(cv_data: Optional[dict]) -> str:
    """Formats the collected data into a clean, ATS-friendly text CV."""
    if not cv_data:
        return "*No CV data provided.*"

    # Centered profile info
    name = cv_data.get('full_name', 'N/A')
    email = cv_data.get('email', 'N/A')
    phone = cv_data.get('phone', 'N/A')
    links = cv_data.get('links', 'N/A')

    profile_line = f"{email} | {phone} | {links}"

    cv = f"""
*--- YOUR ATS-FRIENDLY CV ---*

<center>
*{name}*
{profile_line}
</center>

*--- Professional Summary ---*
{cv_data.get('summary', 'N/A')}

*--- Work Experience ---*
{cv_data.get('experience', 'N/A')}

*--- Education ---*
{cv_data.get('education', 'N/A')}

*--- Certifications ---*
{cv_data.get('certifications', 'N/A')}

*--- Projects ---*
{cv_data.get('Projects', 'N/A')}

*--- Skills ---*
{cv_data.get('skills', 'N/A')}

*--- Referees ---*
{cv_data.get('referees', 'N/A')}

*--------------------*
This CV is optimized for automated systems. You can now copy this text and use it in your applications!
"""
    return cv.strip()

async def handle_resume_conversation(session: models.UserSession, message: str) -> tuple[str, str | None, bool]:
    """
    Manages the multi-step conversation for building a CV.
    Now returns the reply, a potential download link, and a completion flag.
    """
    state = session.session_data if session.session_data else {}
    resume_data = session.resume_data if session.resume_data else {}
    step = state.get("resume_step", 1)
    
    # --- Review and Edit Logic ---
    field_to_confirm = state.get("field_to_confirm")
    if field_to_confirm:
        if "yes" in message.lower():
            state.pop("field_to_confirm", None) # Clear the confirmation state
            step += 1 # Move to the next question
            state["resume_step"] = step
        elif "no" in message.lower():
            state.pop("field_to_confirm", None)
            if field_to_confirm in resume_data:
                resume_data.pop(field_to_confirm, None) # Clear the specific answer
            # Don't increment step, just ask the question again
            return CV_QUESTIONS[step]["prompt"], None, False
        else:
            return "Please answer with 'yes' or 'no'.", None, False

    # --- Standard Question Flow ---
    if step > 1: # Save the answer from the previous step
        prev_step_key = CV_QUESTIONS[step - 1]["key"]
        resume_data[prev_step_key] = message
        
        # Ask for confirmation
        state["field_to_confirm"] = prev_step_key
        confirmation_prompt = (
            f"I have your *{prev_step_key.replace('_', ' ').title()}* as:\n"
            f"_{message}_\n\n"
            "Is this correct? (yes/no)"
        )
        return confirmation_prompt, None, False

    # Check if the conversation is complete
    if step > len(CV_QUESTIONS):
        # Format the final CV
        cv_text = format_cv(resume_data)
        
        # Generate a unique filename for the user
        user_name_part = resume_data.get("full_name", "user").split(" ")[0]
        filename = f"{user_name_part}_CV.txt"

        # Call the file handler to upload the file
        await asyncio.sleep(1) # Small delay to feel more natural
        download_link = await upload_text_as_file(cv_text, filename)

        final_message = "Your CV is complete!"
        return final_message, download_link, True

    # Ask the current question
    question_info = CV_QUESTIONS[step]
    state["resume_step"] = step
    return question_info["prompt"], None, False

