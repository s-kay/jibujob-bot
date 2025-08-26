# app/services.py
from sqlalchemy.orm import Session
from . import models, whatsapp_client

# --- Mock Datasets ---
JOBS = {
    "software developer": [
        "Junior Python Developer – https://jobs.example.com/dev1",
        "Frontend Engineer – https://jobs.example.com/dev2",
    ],
    "accountant": [
        "Accounts Assistant – https://jobs.example.com/acc1",
        "Finance Analyst – https://jobs.example.com/acc2",
    ],
}
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

def paginate_results(items, start_index, count=3):
    """Paginates a list of items."""
    end_index = start_index + count
    paginated_items = items[start_index:end_index]
    next_index = end_index if end_index < len(items) else 0
    return paginated_items, next_index

async def process_message(db: Session, session: models.UserSession, message_text: str):
    """
    Main business logic handler for processing user messages with persistence.
    """
    message_text = message_text.strip().lower()
    state = session.session_data

    # Helper to reset all temporary 'awaiting' flags
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

    # --- Job Search Flow (with Persistence) ---
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
                listings = JOBS.get(session.job_interest.lower(), []) if session.job_interest else []
                results, next_index = paginate_results(listings, 0)
                state["last_job_index"] = next_index
                reply = f"Here are the latest jobs for *{session.job_interest}*:\n\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
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
            # The user's input, message_text, is already lowercased and is a guaranteed string.
            listings = JOBS.get(message_text, [])
            
            if not listings:
                reply = f"Sorry, I couldn't find jobs for '{message_text}'. Please try another role."
                state["awaiting_job_role"] = True # Keep asking for a valid role
            else:
                # Only save the interest to the database if it's valid.
                session.job_interest = message_text 
                results, next_index = paginate_results(listings, 0)
                state["last_job_index"] = next_index
                reply = f"Great! I've saved your interest as *{session.job_interest}*.\n\nHere are the first results:\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags() # Clear the 'awaiting' flag
                
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return
            
        # Handle "more" command for pagination
        if message_text == "more" and session.job_interest:
            listings = JOBS.get(session.job_interest.lower(), []) if session.job_interest else []
            start_index = state.get("last_job_index", 0)
            if start_index == 0:
                reply = f"You've seen all the current listings for *{session.job_interest}*.\n\n{MAIN_MENU}"
                session.current_menu = "main"
            else:
                results, next_index = paginate_results(listings, start_index)
                state["last_job_index"] = next_index
                reply = "Here are more results:\n\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                else: reply += "\n\nThat's all for now!"
                reply += f"\n\nType 'menu' to return to the main menu."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

    # --- Training Flow (Placeholder) ---
    if message_text == "2" or session.current_menu == "training":
        session.current_menu = "training"

        # On first entry to this menu, check for saved interest
        if message_text == "2":
            reset_flags()
            if session.training_interest:
                state["awaiting_training_confirm"] = True
                reply = f"I remember you were interested in *{session.training_interest}* training. Shall I search for those again? (yes/no)"
            else:
                state["awaiting_training_role"] = True
                reply = "📚 Which training module are you interested in? (e.g., Digital Skills, Entrepreneurship)"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return
        
        # Handle user confirming their saved interest
        if state.get("awaiting_training_confirm"):
            if message_text in ["yes", "y"]:
                listings = JOBS.get(session.training_interest.lower(), []) if session.training_interest else []
                results, next_index = paginate_results(listings, 0)
                state["last_training_index"] = next_index
                reply = f"Here are the latest trainings for *{session.training_interest}*:\n\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif message_text in ["no", "n"]:
                state["awaiting_training_role"] = True
                reply = "No problem. What new training are you looking for?"
                reset_flags()
            else:
                reply = "Please answer with 'yes' or 'no'."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        # Handle user providing a new training
        if state.get("awaiting_training_role"):
            # The user's input, message_text, is already lowercased and is a guaranteed string.
            listings = TRAININGS.get(message_text, [])

            if not listings:
                reply = f"Sorry, I couldn't find trainings for '{message_text}'. Please try another training."
                state["awaiting_training_role"] = True # Keep asking for a valid training
            else:
                # Only save the interest to the database if it's valid.
                session.training_interest = message_text
                results, next_index = paginate_results(listings, 0)
                state["last_training_index"] = next_index
                reply = f"Perfect ✅ — I’ll guide you through *{session.training_interest}*.\n\nHere are the first results:\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags() # Clear the 'awaiting' flag
                
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return
            
        # Handle "more" command for pagination
        if message_text == "more" and session.training_interest:
            listings = TRAININGS.get(session.training_interest.lower(), []) if session.training_interest else []
            start_index = state.get("last_training_index", 0)
            if start_index == 0:
                reply = f"You've seen all the current listings for *{session.training_interest}*.\n\n{MAIN_MENU}"
                session.current_menu = "main"
            else:
                results, next_index = paginate_results(listings, start_index)
                state["last_training_index"] = next_index
                reply = "Here 👇 are more results:\n\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                else: reply += "\n\nThat's all for now!"
                reply += f"\n\nType 'menu' to return to the main menu."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

    # --- Mentorship Flow (Placeholder) ---
    if message_text == "3" or session.current_menu == "mentorship":
        session.current_menu = "mentorship"

        # On first entry to this menu, check for saved interest
        if message_text == "3":
            reset_flags()
            if session.mentorship_interest:
                state["awaiting_mentorship_confirm"] = True
                reply = f"🤝 Last time you were interested in *{session.mentorship_interest}* mentorship. Shall I bring those up again? (yes/no)"
            else:
                state["awaiting_mentorship_role"] = True
                reply = "🤝 What type of mentorship are you looking for? (e.g., Tech, Business)"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return
        
        # Handle user confirming their saved interest
        if state.get("awaiting_mentorship_confirm"):
            if message_text in ["yes", "y"]:
                listings = MENTORSHIPS.get(session.mentorship_interest.lower(), []) if session.mentorship_interest else []
                results, next_index = paginate_results(listings, 0)
                state["last_mentorship_index"] = next_index
                reply = f"Here 👇 are the latest mentors for *{session.mentorship_interest}*:\n\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif message_text in ["no", "n"]:
                state["awaiting_mentorship_role"] = True
                reply = "No problem. What new mentorship are you looking for?"
                reset_flags()
            else:
                reply = "Please answer with 'yes' or 'no'."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        # Handle user providing a new mentorship
        if state.get("awaiting_mentorship_role"):
            # The user's input, message_text, is already lowercased and is a guaranteed string.
            listings = MENTORSHIPS.get(message_text, [])

            if not listings:
                reply = f"Sorry, I couldn't find mentors for '{message_text}'. Please try another mentorship."
                state["awaiting_mentorship_role"] = True # Keep asking for a valid mentorship
            else:
                # Only save the interest to the database if it's valid.
                session.mentorship_interest = message_text
                results, next_index = paginate_results(listings, 0)
                state["last_mentorship_index"] = next_index
                reply = f"Nice ✅ — I’ll connect you with *{session.mentorship_interest}*.\n\nHere are the first results:\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags() # Clear the 'awaiting' flag                
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return
            
        # Handle "more" command for pagination
        if message_text == "more" and session.mentorship_interest:
            listings = MENTORSHIPS.get(session.mentorship_interest.lower(), []) if session.mentorship_interest else []
            start_index = state.get("last_mentorship_index", 0)
            if start_index == 0:
                reply = f"You've seen all the current listings for *{session.mentorship_interest}*.\n\n{MAIN_MENU}"
                session.current_menu = "main"
            else:
                results, next_index = paginate_results(listings, start_index)
                state["last_mentorship_index"] = next_index
                reply = "Here 👇 are more results:\n\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                else: reply += "\n\nThat's all for now!"
                reply += f"\n\nType 'menu' to return to the main menu."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

    # --- Entrepreneurship Flow (Placeholder) ---
    if message_text == "4" or session.current_menu == "entrepreneurship":
        session.current_menu = "entrepreneurship"

        # On first entry to this menu, check for saved interest
        if message_text == "4":
            reset_flags()
            if session.entrepreneurship_interest:
                state["awaiting_mentorship_confirm"] = True
                reply = f"💡 Last time you were exploring *{session.entrepreneurship_interest}* entrepreneurship. Are you still interested in it? (yes/no)"
            else:
                state["awaiting_mentorship_role"] = True
                reply = "💡 Which area interests you? (Freelancing, Agribusiness, E-commerce, Crafts, Digital Services)"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return
        
        # Handle user confirming their saved interest
        if state.get("awaiting_entrepreneurship_confirm"):
            if message_text in ["yes", "y"]:
                listings = ENTREPRENEURSHIPS.get(session.entrepreneurship_interest.lower(), []) if session.entrepreneurship_interest else []
                results, next_index = paginate_results(listings, 0)
                state["last_entrepreneurship_index"] = next_index
                reply = f"Here 👇 are the latest entrepreneurship resources for *{session.entrepreneurship_interest}*:\n\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif message_text in ["no", "n"]:
                state["awaiting_entrepreneurship_role"] = True
                reply = "Okay, what new area are you interested in?"
                reset_flags()
            else:
                reply = "Please answer with 'yes' or 'no'."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        # Handle user providing a new entrepreneurship role
        if state.get("awaiting_entrepreneurship_role"):
            # The user's input, message_text, is already lowercased and is a guaranteed string.
            listings = ENTREPRENEURSHIPS.get(message_text, [])

            if not listings:
                reply = f"Sorry, I couldn't find resources for '{message_text}'. Please try another entrepreneurship area."
                state["awaiting_entrepreneurship_role"] = True # Keep asking for a valid entrepreneurship area
            else:
                # Only save the interest to the database if it's valid.
                session.entrepreneurship_interest = message_text
                results, next_index = paginate_results(listings, 0)
                state["last_entrepreneurship_index"] = next_index
                reply = f"Awesome ✅ — I’ll show you resources for *{session.entrepreneurship_interest}*.\n\nHere are the results:\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags() # Clear the 'awaiting' flag                
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return
            
        # Handle "more" command for pagination
        if message_text == "more" and session.entrepreneurship_interest:
            listings = ENTREPRENEURSHIPS.get(session.entrepreneurship_interest.lower(), []) if session.entrepreneurship_interest else []
            start_index = state.get("last_entrepreneurship_index", 0)
            if start_index == 0:
                reply = f"You've seen all the current listings for *{session.entrepreneurship_interest}*.\n\n{MAIN_MENU}"
                session.current_menu = "main"
            else:
                results, next_index = paginate_results(listings, start_index)
                state["last_entrepreneurship_index"] = next_index
                reply = "Here 👇 are more results:\n\n" + "\n".join(results)
                if next_index > 0: reply += "\n\nType 'more' for the next set."
                else: reply += "\n\nThat's all for now!"
                reply += f"\n\nType 'menu' to return to the main menu."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

    # --- Fallback for unrecognized input ---
    reply = f"❓ I didn't understand that. Please choose a number from the menu or type 'menu' to start over.\n\n{MAIN_MENU}"
    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
