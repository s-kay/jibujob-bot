# app/resume_builder.py
from typing import Tuple
from . import models

# --- ATS-Friendly Questions ---
# These questions are designed to prompt users for specific, keyword-rich, and quantifiable information.
CV_QUESTIONS = [
    ("full_name", "Of course. Let's build a CV that gets noticed. First, what is your full name?"),
    ("email", "Got it. What's a professional email address for employers to contact you? (e.g., jane.doe@email.com)"),
    ("phone", "Perfect. And your phone number?"),
    ("summary", 
     "Next, let's write a powerful Professional Summary. Describe your main role and top achievement. "
     "For example: 'Detail-oriented Accountant with 3 years of experience who saved a company KES 500,000 by optimizing budgets.'"),
    ("experience", 
     "Now for your Work Experience. Please list your most recent job title, the company, and one key achievement with a number. "
     "For example: 'Accountant, XYZ Corp (2022-2024) - Reduced monthly reporting errors by 15%.'\n\n(Type 'skip' if you have no formal work experience)"),
    ("skills", 
     "Great. Now, list your most important technical and soft skills, separated by commas. Think about keywords from job descriptions. "
     "For example: 'QuickBooks, Financial Reporting, Budgeting, Microsoft Excel, Communication, Problem-Solving'"),
    ("education", 
     "Almost done! What is your highest qualification and where did you get it? "
     "For example: 'Bachelor of Commerce in Finance, University of Nairobi'"),
]

def format_cv(cv_data: dict) -> str:
    """Formats the collected data into a clean, ATS-friendly text CV."""
    
    cv = f"""
*--- YOUR ATS-FRIENDLY CV ---*

*Name:* {cv_data.get('full_name', 'N/A')}
*Email:* {cv_data.get('email', 'N/A')}
*Phone:* {cv_data.get('phone', 'N/A')}

*--- Professional Summary ---*
{cv_data.get('summary', 'N/A')}

*--- Work Experience ---*
{cv_data.get('experience', 'N/A')}

*--- Skills ---*
{cv_data.get('skills', 'N/A')}

*--- Education ---*
{cv_data.get('education', 'N/A')}

*--------------------*
This CV is optimized for automated systems. You can now copy this text and use it in your applications!
"""
    return cv.strip()

def handle_resume_conversation(session: models.UserSession, message_text: str) -> Tuple[str, bool]:
    """
    Manages the CV building conversation with a review-and-edit loop.
    Returns the reply message and a boolean indicating if the flow is complete.
    """
    cv_data = session.resume_data
    state = session.session_data
    
    # --- Handle the Review/Edit Step ---
    if state.get("awaiting_cv_confirmation"):
        field_to_confirm = state.get("field_to_confirm")
        if message_text in ["yes", "correct", "y"]:
            # User confirmed, clear flags and move on
            state.pop("awaiting_cv_confirmation", None)
            state.pop("field_to_confirm", None)
        elif message_text in ["no", "change", "n"]:
            # User wants to edit, remove the incorrect data and ask again
            if field_to_confirm:
                cv_data.pop(field_to_confirm, None)
            state.pop("awaiting_cv_confirmation", None)
            state.pop("field_to_confirm", None)
            # We'll fall through to the next logic which will re-ask the question
        else:
            return "Please reply with 'yes' or 'no'.", False

    # --- Handle a new answer from the user ---
    previous_question_key = state.get("awaiting_cv_answer_for")
    if previous_question_key and not state.get("awaiting_cv_confirmation"):
        # Save the answer
        if message_text.lower() == 'skip' and previous_question_key == 'experience':
            cv_data[previous_question_key] = "No formal work experience."
        else:
            cv_data[previous_question_key] = message_text
        
        # Ask for confirmation
        state["awaiting_cv_confirmation"] = True
        state["field_to_confirm"] = previous_question_key
        state.pop("awaiting_cv_answer_for", None)
        confirmation_text = f"I have this down as:\n\n_{message_text}_\n\nIs that correct? (yes/no)"
        return confirmation_text, False

    # --- Find and ask the next question ---
    next_question_key = None
    for key, _ in CV_QUESTIONS:
        if key not in cv_data:
            next_question_key = key
            break
            
    if next_question_key:
        _, question_text = next((q for q in CV_QUESTIONS if q[0] == next_question_key))
        state["awaiting_cv_answer_for"] = next_question_key
        return question_text, False
    else:
        # All questions are answered and confirmed, format and return the CV
        state.pop("awaiting_cv_answer_for", None)
        state.pop("awaiting_cv_confirmation", None)
        state.pop("field_to_confirm", None)
        final_cv = format_cv(cv_data)
        return final_cv, True
