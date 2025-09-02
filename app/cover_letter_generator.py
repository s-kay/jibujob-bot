from app import models

def handle_cover_letter_conversation(session: models.UserSession, message: str) -> tuple[str, bool]:
    """
    Manages the multi-step conversation to gather information for the AI cover letter generator.
    Returns the reply to the user and a flag indicating if the conversation is complete.
    """
    state = session.session_data
    # Ensure cover_letter_data is initialized
    if 'cover_letter_data' not in session or not session.cover_letter_data:
        session.cover_letter_data = {}

    step = state.get("cover_letter_step", 0)

    if step == 0:  # Ask for company name
        state["cover_letter_step"] = 1
        return "Of course. I can help you write a strong cover letter. First, what is the name of the company you are applying to?", False

    elif step == 1:  # Ask for job role
        if session.cover_letter_data is not None:
            session.cover_letter_data["company_name"] = message
        state["cover_letter_step"] = 2
        return f"Got it, the company is *{message}*. Now, what is the exact job role you are applying for?", False

    elif step == 2:  # Ask for job description
        if session.cover_letter_data is not None:
            session.cover_letter_data["job_role"] = message
        state["cover_letter_step"] = 3
        return "Perfect. The final step is to paste the full job description. This will help me tailor the letter specifically for this role.", False
    
    # The final step (handling the job description) is managed in services.py
    # This function should not be called at that stage.
    return "Sorry, something went wrong with the cover letter process.", True

