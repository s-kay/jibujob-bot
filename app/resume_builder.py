from typing import Tuple, Optional
from . import models
import asyncio
from app.file_handler import upload_text_as_file

CV_QUESTIONS = {
    1: {"key": "full_name", "prompt": "💪🏾 Great start! Let's build a CV that will get you noticed.\n\nFirst, what is your full name?"},
    2: {"key": "email", "prompt": "Got it. What's a professional email address for employers to contact you? (e.g., jane.doe@email.com)"},
    3: {"key": "phone", "prompt": "Perfect. And your phone number?"},
    4: {"key": "links", "prompt": "Great! Please share any professional links you'd like to include (e.g., LinkedIn, portfolio website, Github). (Type 'skip' if none)"},
    5: {"key": "summary", "prompt": "Next, let's write a powerful Professional Summary. Describe your main role and top achievement."},
    6: {"key": "experience", "prompt": "Now for your Work Experience. Please list your most recent job title, the company, and one key achievement with a number. "
        "For example: 'Accountant, XYZ Corp (2022-2024) - Reduced monthly reporting errors by 15%.'\n\n(Type 'skip' if you have no formal work experience)"},
    7: {"key": "education", "prompt": "What is your highest qualification and where did you get it? "
        "For example: 'Bachelor of Commerce in Finance, University of Nairobi, 2021-2025'"},
    8: {"key": "certifications", "prompt": "Do you have any relevant certifications? If so, please list them. (Type 'skip' if none)"},
    9: {"key": "projects", "prompt": "Have you worked on any notable projects? If so, please describe them briefly. (Type 'skip' if none)"},
    10: {"key": "skills", "prompt": "Great. Now, list your most important technical and soft skills, separated by commas. Think about keywords from job descriptions. "
        "For example: 'QuickBooks, Financial Reporting, Budgeting, Microsoft Excel, Communication, Problem-Solving'"},
    11: {"key": "referees", "prompt": "Finally, do you have any referees you'd like to include? If so, please provide their names and contact information. (Type 'skip' if none)"},
}

CV_EDITOR_MAP = {
    "1": {"key": "summary", "name": "Professional Summary"},
    "2": {"key": "experience", "name": "Work Experience"},
    "3": {"key": "education", "name": "Education"},
    "4": {"key": "skills", "name": "Skills"},
    "5": {"key": "profile", "name": "Profile Info"}, # Special case
}

def get_editor_menu():
    return (
        "Great! Which part of your CV would you like to update?\n\n"
        "1. Professional Summary\n"
        "2. Work Experience\n"
        "3. Education\n"
        "4. Skills\n"
        "5. Profile Info (Phone/Email/links)"
    )

def format_cv(cv_data: Optional[dict]) -> str:
    if not cv_data: return "*No CV data provided.*"
    name = cv_data.get('full_name', 'N/A').upper()
    email = cv_data.get('email', 'N/A')
    phone = cv_data.get('phone', 'N/A')
    links = cv_data.get('links', 'N/A')
    profile_line = f"{email} | {phone} | {links}"
    cv = f"""
*--- YOUR ATS-FRIENDLY CV ---*

*{name}*
{profile_line}

*--- Professional Summary ---*
{cv_data.get('summary', 'N/A')}

*--- Work Experience ---*
{cv_data.get('experience', 'N/A')}

*--- Education ---*
{cv_data.get('education', 'N/A')}

*--- Certifications ---*
{cv_data.get('certifications', 'N/A')}

*--- Projects ---*
{cv_data.get('projects', 'N/A')}

*--- Skills ---*
{cv_data.get('skills', 'N/A')}

*--- Referees ---*
{cv_data.get('referees', 'N/A')}
"""
    return cv.strip()

def has_existing_cv(resume_data: dict) -> bool:
    """
    A CV is considered 'existing' and 'complete' if:
    - The 'is_complete' flag is set
    - Core required fields are filled
    """
    if not resume_data or not resume_data.get("is_complete"):
        return False

    # Core fields only (optional ones are ignored)
    core_fields = ["full_name", "email", "phone", "summary", "experience", "education", "skills"]
    for field in core_fields:
        if not resume_data.get(field):
            return False
    return True


async def handle_resume_conversation(session: models.UserSession, message: str) -> tuple[str, str | None, bool]:
    state = session.resume_data or {}

    # --- Ongoing Creation ---
    if "creation_step" in state:
        current_step = state.get("creation_step", 1)
        
        # The message we just received is the answer to the *previous* question.
        step_that_was_answered = current_step - 1
        if message and step_that_was_answered in CV_QUESTIONS:
            answer_key = CV_QUESTIONS[step_that_was_answered]["key"]
            if message.lower().strip() != 'skip':
                state[answer_key] = message

        # Now, decide what to do next. Have we finished?
        if current_step > len(CV_QUESTIONS):
            state.pop("creation_step", None)
            state["is_complete"] = True
            session.resume_data = state
            final_message = "✅ Your CV is complete!"
            cv_text = format_cv(state)
            user_name_part = state.get("full_name", "user").split(" ")[0]
            filename = f"KaziLeo_CV_{user_name_part}.txt"
            download_link = await upload_text_as_file(cv_text, filename)
            return final_message, download_link, True

        # If not finished, ask the current question and update the state for the next turn.
        question_info = CV_QUESTIONS[current_step]
        state["creation_step"] = current_step + 1
        session.resume_data = state
        return question_info["prompt"], None, False


    # --- Ongoing Editing ---
    elif "editing_step" in state:
        if state["editing_step"] == "awaiting_section_choice":
            if message in CV_EDITOR_MAP:
                state.pop("editing_step")
                section_info = CV_EDITOR_MAP[message]
                state["awaiting_section_update"] = section_info["key"]
                state["editing_section_name"] = section_info["name"]
                if section_info["key"] == "profile":
                    current_data = f"{state.get('email', '')}, {state.get('phone', '')}, {state.get('links', '')}"
                    prompt = "Please provide the new Email, Phone Number, and Links, separated by commas."
                else:
                    current_data = state.get(section_info['key'], 'No data saved yet.')
                    prompt = f"Please provide the new content for your *{section_info['name']}*."
                return f"Okay, here's what I currently have for *{section_info['name']}*:\n_{current_data}_\n\n{prompt}", None, False
            else:
                return "Please select a valid number from the menu (1-5).", None, False

        elif "awaiting_section_update" in state:
            section_key = state.pop("awaiting_section_update")
            section_name = state.pop("editing_section_name", "Section")
            if section_key == "profile":
                parts = [p.strip() for p in message.split(',')]
                state["email"] = parts[0] if len(parts) > 0 else ""
                state["phone"] = parts[1] if len(parts) > 1 else ""
                state["links"] = parts[2] if len(parts) > 2 else ""
            else:
                state[section_key] = message
            state["editing_step"] = "awaiting_continue_choice"
            session.resume_data = state
            return f"✅ Perfect, I've updated your *{section_name}*.\n\nWould you like to edit another section? (yes/no)", None, False

        elif state["editing_step"] == "awaiting_continue_choice":
            state.pop("editing_step")
            if "yes" in message.lower():
                state["editing_step"] = "awaiting_section_choice"
                session.resume_data = state
                return get_editor_menu(), None, False
            else:
                final_message = "Great! Your CV has been updated."
                cv_text = format_cv(state)
                user_name_part = state.get("full_name", "user").split(" ")[0]
                filename = f"KaziLeo_CV_{user_name_part}.txt"
                download_link = await upload_text_as_file(cv_text, filename)
                return final_message, download_link, True

    # --- Entry Point: No active conversation ---
    else:
        if has_existing_cv(state):
            if "awaiting_edit_choice" not in state:
                state["awaiting_edit_choice"] = True
                session.resume_data = state
                return "It looks like you already have a CV with me. Would you like to edit it? (yes/no)", None, False
            else:
                state.pop("awaiting_edit_choice")
                if "yes" in message.lower():
                    state["editing_step"] = "awaiting_section_choice"
                    session.resume_data = state
                    return get_editor_menu(), None, False
                else:
                    # ✅ User said "no" → just return saved CV (no restart)
                    cv_text = format_cv(state)
                    user_name_part = state.get("full_name", "user").split(" ")[0]
                    filename = f"KaziLeo_CV_{user_name_part}.txt"
                    download_link = await upload_text_as_file(cv_text, filename)
                    return "Here’s your current CV 👇🏾", download_link, True
        else:
            session.resume_data = {"creation_step": 1}
            return CV_QUESTIONS[1]["prompt"], None, False

    return "Sorry, something went wrong in the CV builder. Let's return to the main menu.", None, True
