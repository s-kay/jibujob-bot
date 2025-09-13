# app/resume_builder.py
from typing import Tuple, Optional
from . import models, crud
import asyncio
from app.file_handler import generate_and_upload_pdf
from . import text_responses

# --- ATS-Friendly Questions ---
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

# This dictionary maps the user's choice in the editor to the key in the resume data.
CV_EDITOR_MAP = {
    "summary": {"key": "summary", "name": "Summary"},
    "experience": {"key": "experience", "name": "Work Experience"},
    "education": {"key": "education", "name": "Education"},
    "skills": {"key": "skills", "name": "Skills"},
    "profile": {"key": "profile", "name": "Profile Info"}, # Special case
    "certifications": {"key": "certifications", "name": "Certifications"},
    "projects": {"key": "projects", "name": "Projects"},
    "referees": {"key": "referees", "name": "Referees"}
}


def format_cv(cv_data: Optional[dict]) -> str:
    if not cv_data: return "*No CV data provided.*"
    name = cv_data.get('full_name', 'N/A').upper()
    email = cv_data.get('email', 'N/A')
    phone = cv_data.get('phone', 'N/A')
    links = cv_data.get('links', 'N/A')
    profile_line = f"{email} | {phone} | {links}"

    # Center the header using spaces (approximate centering for WhatsApp/text)
    header_width = 50  # Adjust based on your display needs
    name_spaces = ' ' * max(0, (header_width - len(name)) // 2)
    profile_spaces = ' ' * max(0, (header_width - len(profile_line)) // 2)

    cv = f"""


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
    """A CV is considered 'existing' and 'complete' if the 'is_complete' flag is set."""
    return bool(resume_data and resume_data.get("is_complete"))

async def handle_resume_conversation(session: models.UserSession, message: str) -> tuple[str, str | None, bool]:
    state = session.resume_data or {}

    # --- Ongoing Creation ---
    if "creation_step" in state:
        current_step = state.get("creation_step", 1)
        
        # Save answer for the question that was just asked
        if message:
            # current_step represents the question that was just asked
            if current_step in CV_QUESTIONS:
                step_key = CV_QUESTIONS[current_step]["key"]
                if message.lower().strip() != 'skip':
                    state[step_key] = message
        
        # Move to next step
        next_step = current_step + 1

        # Check if done
        if next_step > len(CV_QUESTIONS):
            state.pop("creation_step", None)
            state["is_complete"] = True
            session.resume_data = state
            final_message = "✅ Your CV is complete!"
            cv_text = format_cv(state)
            user_name_part = state.get("full_name", "user").split(" ")[0]
            filename = f"KaziLeo_CV_{user_name_part}.pdf"
            download_link = await generate_and_upload_pdf(state, filename)
            return final_message, download_link, True

        # Ask next question
        question_info = CV_QUESTIONS[next_step]
        state["creation_step"] = next_step  # Store the question we're about to ask
        session.resume_data = state
        return question_info["prompt"], None, False

    # Is the bot in the middle of EDITING an existing CV?
    elif "editing_step" in state:
        if state["editing_step"] == "awaiting_section_choice":
            if message in CV_EDITOR_MAP:
                state.pop("editing_step")
                section_info = CV_EDITOR_MAP[message]
                state["awaiting_section_update"] = section_info["key"]
                state["editing_section_name"] = section_info["name"]
                
                current_data = ""
                if section_info["key"] == "profile":
                    current_data = f"{state.get('email', '')}, {state.get('phone', '')}, {state.get('links', '')}"
                    prompt = "Please provide the new Email, Phone Number, and Links, separated by commas."
                else:
                    current_data = state.get(section_info['key'], 'No data saved yet.')
                    prompt = f"Please provide the new content for your *{section_info['name']}*."
                return f"Okay, here's what I currently have for *{section_info['name']}*:\n_{current_data}_\n\n{prompt}", None, False
            else:
                return text_responses.get_cv_editor_responses("start_editing_new"), None, False

    elif state.get("awaiting_section_update"):
        section_key = state.pop("awaiting_section_update")
        section_name = state.pop("editing_section_name", "Section")
        
        if section_key == "profile":
            parts = [p.strip() for p in message.split(',')]
            state["email"] = parts[0] if len(parts) > 0 else ""
            state["phone"] = parts[1] if len(parts) > 1 else ""
            state["links"] = parts[2] if len(parts) > 2 else ""
        else:
            state[section_key] = message
        
        state["awaiting_continue_choice"] = True
        return f"✅ Perfect, I've updated your *{section_name}*.\n\nWould you like to edit another section? (yes/no)", None, False

    elif state.get("awaiting_section_choice"):
        if message in CV_EDITOR_MAP:
            state.pop("awaiting_section_choice")
            section_info = CV_EDITOR_MAP[message]
            state["awaiting_section_update"] = section_info["key"]
            state["editing_section_name"] = section_info["name"]
            
            current_data = ""
            if section_info["key"] == "profile":
                current_data = f"{state.get('email', '')}, {state.get('phone', '')}, {state.get('links', '')}"
                prompt = "Please provide the new Email, Phone Number, and Links, separated by commas."
            else:
                current_data = state.get(section_info['key'], 'No data saved yet.')
                prompt = f"Please provide the new content for your *{section_info['name']}*."
            return f"Okay, here's what I currently have for *{section_info['name']}*:\n_{current_data}_\n\n{prompt}", None, False
        else:
            return text_responses.get_cv_editor_responses("start_editing_new"), None, False

    elif state.get("awaiting_continue_choice"):
        state.pop("awaiting_continue_choice")
        if "yes" in message.lower():
            state["awaiting_section_choice"] = True
            return text_responses.get_cv_editor_responses("start_editing_new"), None, False
        else:
            final_message = "Great! Your CV has been updated."
            cv_text = format_cv(state)
            user_name_part = state.get("full_name", "user").split(" ")[0]
            filename = f"KaziLeo_CV_{user_name_part}.pdf"
            download_link = await generate_and_upload_pdf(state, filename)
            return final_message, download_link, True

    # --- PRIORITY 2: Handle the initial entry point (if NO conversation is active) ---
    else:
        if has_existing_cv(state):
            if "awaiting_edit_choice" not in state:
                state["awaiting_edit_choice"] = True
                return "It looks like you already have a CV with me. Would you like to edit it? (yes/no)", None, False
            else:
                state.pop("awaiting_edit_choice")
                if "yes" in message.lower():
                    state["editing_step"] = "awaiting_section_choice"
                    return text_responses.get_cv_editor_responses("start_editing_new"), None, False
                else: # User wants to create a new one, erasing the old one
                    session.resume_data = {"creation_step": 1} 
                    return CV_QUESTIONS[1]["prompt"], None, False
        else: # No CV exists, so we must start the creation flow
            session.resume_data = {"creation_step": 1}
            return CV_QUESTIONS[1]["prompt"], None, False

    return "Sorry, something went wrong in the CV builder. Let's return to the main menu.", None, True