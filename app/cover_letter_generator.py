from app import models

def handle_cover_letter_conversation(session: models.UserSession, message: str) -> tuple[str, bool]:
    """
    Manages the multi-step conversation for the AI cover letter generator.
    Returns the bot's reply and a flag indicating if the process is complete.
    """
    # THE FIX IS HERE: This defensive check ensures cover_letter_data is a dict,
    # satisfying the type checker and preventing potential runtime errors.
    if session.cover_letter_data is None:
        session.cover_letter_data = {}

    state = session.cover_letter_data
    step = state.get("step", 0)

    if step == 0:
        state["step"] = 1
        return "Let's get started on your cover letter. What is the name of the company you are applying to?", False
    
    elif step == 1:
        state["company_name"] = message
        state["step"] = 2
        return "Got it. And what is the exact job role you are applying for? (e.g., 'Junior Accountant')", False
        
    elif step == 2:
        state["job_role"] = message
        state["step"] = 3
        return "Perfect. Finally, please paste the full job description here. The more detail, the better the result!", False

    # The final step is handled in services.py, so this function is complete.
    # We return an empty reply and a "True" flag to signal completion.
    return "", True
