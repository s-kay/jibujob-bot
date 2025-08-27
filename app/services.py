# app/services.py
from sqlalchemy.orm import Session
from . import models, whatsapp_client, job_client

# --- Mock Datasets (JOBS dictionary is now removed) ---
TRAININGS = {
    "ai prompt": ["Intro to AI Prompting - https://training.example.com/ai1"],
    "digital skills": ["Advanced Excel - https://training.example.com/ds1"],
}
MENTORSHIPS = {
    "tech": ["Meet Jane (Senior Developer) – https://mentorship.example.com/tech1"],
    "business": ["Meet Mary (Startup Coach) – https://mentorship.example.com/biz1"],
}
ENTREPRENEURSHIPS = {
    "chicken keeping": ["Guide to Poultry Farming - https://biz.example.com/agri1"],
    "freelancing": ["How to Price Your Services – https://biz.example.com/freelance1"],
}

# --- Constants ---
MAIN_MENU = (
    "Please choose an option:\n\n"
    "1️⃣ Job Listings\n"
    "2️⃣ Training Modules\n"
    "3️⃣ Mentorship\n"
    "4️⃣ Entrepreneurship\n"
    "0️⃣ Reset Session"
)

# Note: The paginate_results function is no longer needed for the jobs flow
# as the API handles pagination. It can be kept for other mock data flows.

async def process_message(db: Session, session: models.UserSession, message_text: str):
    """
    Main business logic handler for processing user messages with persistence.
    """
    message_text = message_text.strip().lower()
    state = session.session_data

    def reset_flags():
        for key in list(state.keys()):
            if key.startswith("awaiting_"):
                state[key] = False

    # --- Universal Commands ---
    if message_text in ["hi", "hello", "start", "menu"]:
        session.current_menu = "main"
        reset_flags()
        reply = f"Hi {session.user_name}! 👋 Welcome back to KaziLeo.\n{MAIN_MENU}"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    if message_text == "0":
        session.current_menu = "main"
        session.session_data = {}
        reply = "👋 Your session has been reset. Type 'hi' to start again."
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    # --- Job Search Flow (with Live API) ---
    if message_text == "1" or session.current_menu == "jobs":
        session.current_menu = "jobs"

        # On first entry to this menu, check for saved interest 
        if message_text == "1":
            reset_flags()
            if session.job_interest:
                state["awaiting_job_confirm"] = True
                reply = f"I remember you were interested in *{session.job_interest}* jobs. Shall I search for those again? (yes/no)"
            else:
                state["awaiting_job_role"] = True
                reply = "🔎 Which type of job are you interested in? (e.g., Software Developer, Accountant)"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return
        
        # Handle user confirming their saved interest
        if state.get("awaiting_job_confirm"):
            if message_text in ["yes", "y"]:
                # FIX: Add a check to ensure job_interest is not None before using it.
                if session.job_interest:
                    reply = f"Searching for *{session.job_interest}* jobs..."
                    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                    
                    listings = await job_client.fetch_jobs(session.job_interest)
                    
                    if listings:
                        reply = f"Here are the latest jobs for *{session.job_interest}*:\n\n" + "\n".join(listings)
                    elif listings == []: # Empty list means no jobs found
                        reply = f"I couldn't find any current listings for *{session.job_interest}*. I'll keep an eye out for you!"
                    else: # None means an API error occurred
                        reply = "Sorry, I'm having trouble connecting to the job service right now. Please try again in a few minutes."
                else:
                    # This case should ideally not be hit, but it's a safe fallback.
                    reply = "Something went wrong, I don't have a saved job interest for you. What job are you looking for?"
                    state["awaiting_job_role"] = True
                
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif message_text in ["no", "n"]:
                state["awaiting_job_role"] = True
                reply = "No problem. What new job role are you looking for?"
                reset_flags()
            else:
                reply = "Please answer with 'yes' or 'no'."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        # Handle user providing a new job role
        if state.get("awaiting_job_role"):
            session.job_interest = message_text
            
            reply = f"Great! I've saved your interest as *{session.job_interest}*. Searching for jobs now..."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

            # Here, message_text is guaranteed to be a string from user input.
            listings = await job_client.fetch_jobs(message_text)

            if listings:
                reply = f"Here are the first results:\n\n" + "\n".join(listings)
            elif listings == []:
                reply = f"I couldn't find any current listings for *{session.job_interest}*. I'll keep an eye out and notify you if something comes up!"
            else:
                reply = "Sorry, I'm having trouble connecting to the job service right now. Please try again in a few minutes."

            reply += f"\n\nType 'menu' to return to the main menu."
            reset_flags()
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

    # --- Training Modules Flow ---
    # ... (Keep the placeholder logic for now) ...

    # --- Fallback ---
    reply = f"❓ I didn't understand that. Please choose a number from the menu.\n\n{MAIN_MENU}"
    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
