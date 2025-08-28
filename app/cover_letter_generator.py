# app/cover_letter_generator.py
from typing import Tuple
from . import models

# --- Cover Letter Questions ---
# These questions guide the user to provide the key components of a cover letter.
COVER_LETTER_QUESTIONS = [
    ("company_name", "Let's get started on your cover letter. What is the name of the company you are applying to?"),
    ("job_role", "And what is the exact job role you're applying for? (e.g., 'Junior Accountant')"),
    ("key_skill", "Great. Now, what is the #1 most important skill from the job description that you have? (e.g., 'Financial Reporting')"),
    ("experience_match", "Perfect. Briefly, how does your past experience match this key skill? (1-2 sentences). For example: 'In my previous role at XYZ, I was responsible for preparing monthly financial reports.'"),
    ("passion", "Finally, what excites you most about working for this specific company? (1 sentence). For example: 'I am inspired by your company's commitment to sustainable business practices.'"),
]

def format_cover_letter(cl_data: dict, user_data: dict) -> str:
    """Formats the collected data into a simple cover letter."""
    
    full_name = user_data.get('full_name', 'Your Name')
    email = user_data.get('email', 'your.email@example.com')
    phone = user_data.get('phone', '07XX XXX XXX')
    
    company_name = cl_data.get('company_name', '[Company Name]')
    job_role = cl_data.get('job_role', '[Job Role]')
    key_skill = cl_data.get('key_skill', '[Key Skill]')
    experience_match = cl_data.get('experience_match', '[Your relevant experience]')
    passion = cl_data.get('passion', '[Your reason for wanting to work there]')

    letter = f"""
*--- YOUR COVER LETTER DRAFT ---*

{full_name}
{phone}
{email}

Dear Hiring Manager,

I am writing to express my enthusiastic interest in the {job_role} position at {company_name}, which I discovered through [Platform where you saw the ad, e.g., BrighterMonday].

The job description highlights a need for proficiency in *{key_skill}*, a skill I have developed throughout my career. {experience_match} I am confident that my abilities align perfectly with the requirements of this role.

Furthermore, I have been following {company_name}'s work for some time. {passion} I am very eager to bring my dedication and skills to your team.

Thank you for considering my application. I have attached my CV for your review and look forward to discussing my qualifications further.

Sincerely,
{full_name}

*--------------------*
You can now copy and paste this text! While you're applying, would you like me to show you other *{job_role}* jobs? (yes/no)
"""
    return letter.strip()

def handle_cover_letter_conversation(session: models.UserSession, message_text: str) -> Tuple[str, bool]:
    """
    Manages the cover letter building conversation with a review-and-edit loop.
    """
    cl_data = session.cover_letter_data
    state = session.session_data
    
    # --- Handle the Review/Edit Step ---
    if state.get("awaiting_cl_confirmation"):
        field_to_confirm = state.get("field_to_confirm")
        if message_text in ["yes", "correct", "y"]:
            state.pop("awaiting_cl_confirmation", None)
            state.pop("field_to_confirm", None)
            # Fall through to ask the next question
        elif message_text in ["no", "change", "n"]:
            if field_to_confirm:
                cl_data.pop(field_to_confirm, None)
            state.pop("awaiting_cl_confirmation", None)
            state.pop("field_to_confirm", None)
            # Fall through to re-ask the same question
        else:
            return "Please reply with 'yes' or 'no'.", False

    # --- Handle a new answer from the user ---
    previous_question_key = state.get("awaiting_cl_answer_for")
    if previous_question_key and not state.get("awaiting_cl_confirmation"):
        cl_data[previous_question_key] = message_text
        
        state["awaiting_cl_confirmation"] = True
        state["field_to_confirm"] = previous_question_key
        state.pop("awaiting_cl_answer_for", None)
        confirmation_text = f"I have this down as:\n\n_{cl_data[previous_question_key]}_\n\nIs that correct? (yes/no)"
        return confirmation_text, False

    # --- Find and ask the next question ---
    next_question_key = None
    for key, _ in COVER_LETTER_QUESTIONS:
        if key not in cl_data:
            next_question_key = key
            break
            
    if next_question_key:
        _, question_text = next((q for q in COVER_LETTER_QUESTIONS if q[0] == next_question_key))
        state["awaiting_cl_answer_for"] = next_question_key
        return question_text, False
    else:
        # All questions are answered and confirmed
        state.pop("awaiting_cl_answer_for", None)
        state.pop("awaiting_cl_confirmation", None)
        state.pop("field_to_confirm", None)
        final_letter = format_cover_letter(cl_data, session.resume_data)
        state["awaiting_similar_jobs_confirm"] = True
        return final_letter, True
