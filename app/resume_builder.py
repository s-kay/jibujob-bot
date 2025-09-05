# app/resume_builder.py
from typing import Tuple, Optional # 
from . import models
import asyncio
from app.file_handler import upload_text_as_file
from app import models

# --- ATS-Friendly Questions ---
# These questions are designed to prompt users for specific, keyword-rich, and quantifiable information.
CV_QUESTIONS = {
    1: {"key": "full_name", "prompt": "💪🏾 Great start! Let's build a CV that will get you noticed.\n\nFirst, what is your full name?"},
    2: {"key": "email", "prompt": "Got it. What's a professional email address for employers to contact you? (e.g., jane.doe@email.com)"},
    3: {"key": "phone", "prompt": "Perfect. And your phone number?"},
    4: {"key": "links", "prompt": "Great! Please share any professional links you'd like to include (e.g., LinkedIn, portfolio website, Github)."},
    5: {"key": "summary", "prompt": "Next, let's write a powerful Professional Summary. Describe your main role and top achievement."},
    6: {"key": "experience", "prompt": "Now for your Work Experience. Please list your most recent job title, the company, and one key achievement with a number. "
        "For example: 'Accountant, XYZ Corp (2022-2024) - Reduced monthly reporting errors by 15%.'\n\n(Type 'skip' if you have no formal work experience)"},
    7: {"key": "education", "prompt": "What is your highest qualification and where did you get it? "
        "For example: 'Bachelor of Commerce in Finance, University of Nairobi, 2021-2025'"},
    8: {"key": "certifications", "prompt": "Do you have any relevant certifications? If so, please list them. "
        "For example: 'Certified Public Accountant (CPA), Project Management Professional (PMP)'"},
    9: {"key": "projects", "prompt": "Have you worked on any notable projects? If so, please describe them briefly. "
        "For example: 'Led a team to develop a budgeting tool that reduced costs by 20%.'"},
    10: {"key": "skills", "prompt": "Great. Now, list your most important technical and soft skills, separated by commas. Think about keywords from job descriptions. "
        "For example: 'QuickBooks, Financial Reporting, Budgeting, Microsoft Excel, Communication, Problem-Solving'"},
    11: {"key": "referees", "prompt": "Finally, do you have any referees you'd like to include? If so, please provide their names and contact information."
        "For example: 'John Doe, johndoe@email.com, +254712345678'"},

}


# This dictionary maps the user's choice in the editor to the key in the resume data.
CV_EDITOR_MAP = {
    "1": {"key": "summary", "name": "Professional Summary"},
    "2": {"key": "experience", "name": "Work Experience"},
    "3": {"key": "education", "name": "Education"},
    "4": {"key": "skills", "name": "Skills"},
    "5": {"key": "profile", "name": "Profile Info"}, # Special case
}

def get_editor_menu():
    """Returns the formatted CV editor sub-menu."""
    return (
        "Great! Which part of your CV would you like to update?\n\n"
        "1. Professional Summary\n"
        "2. Work Experience\n"
        "3. Education\n"
        "4. Skills\n"
        "5. Profile Info (Phone/Email/links)"
    )
        


def format_cv(cv_data: Optional[dict]) -> str:
    """Formats the collected data into a clean, ATS-friendly text CV."""
    if not cv_data:
        return "*No CV data provided.*"

    # Centered profile info
    name = cv_data.get('full_name', 'N/A').upper()
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

def has_existing_cv(resume_data: dict) -> bool:
    """Return True if the user has a mostly complete CV."""
    required_fields = ["full_name", "email", "phone", "summary", "experience"]
    return all(resume_data.get(field) for field in required_fields)

async def handle_resume_conversation(session: models.UserSession, message: str) -> tuple[str, str | None, bool]:
    """
    Manages the multi-step conversation for building OR editing a CV.
    Returns the reply, a potential download link, and a completion flag.
    """
    state = session.session_data if session.session_data else {}
    resume_data = session.resume_data if session.resume_data else {}

    # --- Main Router for this flow ---
    # Are we in the middle of editing a specific section?
    if state.get("awaiting_cv_update_for"):
        section_key = state.pop("awaiting_cv_update_for")
        
        if section_key == "profile":
            resume_data["phone_number"] = message.split(",")[0].strip()
            resume_data["email"] = message.split(",")[1].strip() 
            resume_data["links"] = message.split(",")[2].strip() if "," in message else ""
        else:
            resume_data[section_key] = message
        
        state["awaiting_edit_another_section"] = True
        editing_section = state.get('editing_section')
        section_name = CV_EDITOR_MAP[editing_section]['name'] if editing_section in CV_EDITOR_MAP else "Section"
        return f"✅ Perfect, I've updated your *{section_name}*.\n\nWould you like to edit another section? (yes/no)", None, False

    # Are we waiting for the user to choose a section to edit?
    elif state.get("awaiting_editor_choice"):
        if message in CV_EDITOR_MAP:
            state.pop("awaiting_editor_choice", None)
            section_info = CV_EDITOR_MAP[message]
            state["editing_section"] = message # remember which number they chose
            state["awaiting_cv_update_for"] = section_info["key"]
            
            current_data = ""
            if section_info["key"] == "contact":
                current_data = f"{resume_data.get('phone_number', '')}, {resume_data.get('email', '')}"
                prompt = "Please provide the new Phone Number and Email, separated by a comma."
            else:
                current_data = resume_data.get(section_info['key'], 'No data saved yet.')
                prompt = f"Please provide the new content for your *{section_info['name']}*."

            return f"Okay, here's what I currently have for *{section_info['name']}*:\n_{current_data}_\n\n{prompt}", None, False
        else:
            return "Please select a valid number from the menu (1-5).", None, False
            
    # Are we waiting to see if they want to edit another section?
    elif state.get("awaiting_edit_another_section"):
        state.pop("awaiting_edit_another_section", None)
        if "yes" in message.lower():
            state["awaiting_editor_choice"] = True
            return get_editor_menu(), None, False
        else:
            # They are done editing, generate the final CV
            final_message = "Great! Your CV has been updated."
            cv_text = format_cv(resume_data)
            user_name_part = resume_data.get("full_name", "user").split(" ")[0]
            filename = f"KaziLeo_CV_{user_name_part}.txt"
            download_link = await upload_text_as_file(cv_text, filename)
            return final_message, download_link, True

    # --- Initial Entry Point ---
    # Does a CV already exist?
    elif has_existing_cv(resume_data):
        if not state.get("awaiting_edit_choice"):
            state["awaiting_edit_choice"] = True
            return "It looks like you already have a CV with me. Would you like to edit it? (yes/no)", None, False
        else:
            state.pop("awaiting_edit_choice", None)
            if "yes" in message.lower():
                state["awaiting_editor_choice"] = True
                return get_editor_menu(), None, False
            else:
                # User doesn't want to edit, so we assume they want to start a new one.
                session.resume_data = {}; resume_data = {}
                state["resume_step"] = 1
                return CV_QUESTIONS[1]["prompt"], None, False

    # --- Standard "Create New CV" Flow ---
    else:
        step = state.get("resume_step", 1)
        if step > 1:
            prev_step_key = CV_QUESTIONS[step - 1]["key"]
            resume_data[prev_step_key] = message

        # Always save the updated resume_data back to the session!
        session.resume_data = resume_data
        session.session_data = state

        if step > len(CV_QUESTIONS):
            final_message = "Your CV is complete!"
            cv_text = format_cv(resume_data)
            user_name_part = resume_data.get("full_name", "user").split(" ")[0]
            filename = f"KaziLeo_CV_{user_name_part}.txt"
            download_link = await upload_text_as_file(cv_text, filename)
            return final_message, download_link, True

        question_info = CV_QUESTIONS[step]
        state["resume_step"] = step + 1
        session.session_data = state
        return question_info["prompt"], None, False

