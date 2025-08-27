# app/services.py
from sqlalchemy.orm import Session
from . import models, whatsapp_client, job_client, training_client, entrepreneurship_client, mentorship_client

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

        if state.get("awaiting_job_confirm"):
            if message_text in ["yes", "y"]:
                if session.job_interest:
                    reply = f"Searching for *{session.job_interest}* jobs..."
                    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                    
                    listings = await job_client.fetch_jobs(session.job_interest)
                    
                    if listings:
                        reply = f"Here are the latest jobs for *{session.job_interest}*:\n\n" + "\n".join(listings)
                    elif listings == []:
                        reply = f"I couldn't find any current listings for *{session.job_interest}*. I'll keep an eye out for you!"
                    else:
                        reply = "Sorry, I'm having trouble connecting to the job service right now. Please try again in a few minutes."
                else:
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

        if state.get("awaiting_job_role"):
            session.job_interest = message_text
            
            reply = f"Great! I've saved your interest as *{session.job_interest}*. Searching for jobs now..."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

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

    # --- Training Flow (with Persistence) ---
    if message_text == "2" or session.current_menu == "training":
        session.current_menu = "training"
        
        if message_text == "2":
            reset_flags()
            if session.training_interest:
                state["awaiting_training_confirm"] = True
                reply = f"I remember you were interested in *{session.training_interest}* training. Shall I show you those courses again? (yes/no)"
            else:
                state["awaiting_training_role"] = True
                reply = "📚 What skill would you like to learn? (e.g., AI, Digital Skills, Agribusiness)"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        if state.get("awaiting_training_confirm"):
            if message_text in ["yes", "y"]:
                if session.training_interest:
                    listings = await training_client.fetch_trainings(session.training_interest)
                    if listings is not None:
                        reply = f"Here are courses for *{session.training_interest}*:\n\n" + "\n".join(listings)
                    else:
                        reply = "Sorry, I couldn't fetch training info right now. Please try again later."
                else:
                    reply = "I don't have a saved training interest for you. What skill would you like to learn?"
                    state["awaiting_training_role"] = True
                
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif message_text in ["no", "n"]:
                state["awaiting_training_role"] = True
                reply = "No problem. What new skill are you interested in learning?"
                reset_flags()
            else:
                reply = "Please answer with 'yes' or 'no'."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        if state.get("awaiting_training_role"):
            session.training_interest = message_text
            listings = await training_client.fetch_trainings(message_text)
            if listings:
                reply = f"Great! I've saved your interest in *{session.training_interest}*.\n\nHere are the first courses:\n" + "\n".join(listings)
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif listings == []:
                reply = f"Sorry, I couldn't find any training for '{message_text}'. Please try another topic."
                state["awaiting_training_role"] = True
            else: # Handles None case
                reply = "Sorry, I'm having trouble connecting to the training service. Please try again later."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

    # --- Mentorship Flow (with Persistence) ---
    if message_text == "3" or session.current_menu == "mentorship":
        session.current_menu = "mentorship"
        
        if message_text == "3":
            reset_flags()
            if session.mentorship_interest:
                state["awaiting_mentorship_confirm"] = True
                reply = f"I remember you were looking for a mentor in *{session.mentorship_interest}*. Shall I search again? (yes/no)"
            else:
                state["awaiting_mentorship_role"] = True
                reply = "🤝 What field are you looking for a mentor in? (e.g., Tech, Business, Agribusiness)"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        if state.get("awaiting_mentorship_confirm"):
            if message_text in ["yes", "y"]:
                if session.mentorship_interest:
                    listings = await mentorship_client.fetch_mentors(session.mentorship_interest)
                    if listings is not None:
                        reply = f"Here are some mentors in *{session.mentorship_interest}*:\n\n" + "\n".join(listings)
                    else:
                        reply = "Sorry, I couldn't fetch mentor info right now. Please try again later."
                else:
                    reply = "I don't have a saved mentorship interest for you. What field are you looking for?"
                    state["awaiting_mentorship_role"] = True
                
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif message_text in ["no", "n"]:
                state["awaiting_mentorship_role"] = True
                reply = "No problem. What new field are you interested in?"
                reset_flags()
            else:
                reply = "Please answer with 'yes' or 'no'."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        if state.get("awaiting_mentorship_role"):
            session.mentorship_interest = message_text
            listings = await mentorship_client.fetch_mentors(message_text)
            if listings:
                reply = f"Great! I've saved your interest in *{session.mentorship_interest}*.\n\nHere are some available mentors:\n" + "\n".join(listings)
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif listings == []:
                reply = f"Sorry, I couldn't find any mentors for '{message_text}'. Please try another field."
                state["awaiting_mentorship_role"] = True
            else: # Handles None case
                reply = "Sorry, I'm having trouble connecting to the mentorship service. Please try again later."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

    # --- Entrepreneurship Flow (with Persistence) ---
    if message_text == "4" or session.current_menu == "entrepreneurship":
        session.current_menu = "entrepreneurship"
        
        if message_text == "4":
            reset_flags()
            if session.entrepreneurship_interest:
                state["awaiting_entrepreneurship_confirm"] = True
                reply = f"I remember you were interested in *{session.entrepreneurship_interest}*. Shall I show you those guides again? (yes/no)"
            else:
                state["awaiting_entrepreneurship_role"] = True
                reply = "💡 What business idea are you exploring? (e.g., Agribusiness, E-commerce, Freelancing)"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        if state.get("awaiting_entrepreneurship_confirm"):
            if message_text in ["yes", "y"]:
                if session.entrepreneurship_interest:
                    listings = await entrepreneurship_client.fetch_entrepreneurship_guides(session.entrepreneurship_interest)
                    if listings is not None:
                        reply = f"Here are some guides for *{session.entrepreneurship_interest}*:\n\n" + "\n".join(listings)
                    else:
                        reply = "Sorry, I couldn't fetch the guides right now. Please try again later."
                else:
                    reply = "I don't have a saved business interest for you. What idea are you exploring?"
                    state["awaiting_entrepreneurship_role"] = True
                
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif message_text in ["no", "n"]:
                state["awaiting_entrepreneurship_role"] = True
                reply = "No problem. What new business idea are you interested in?"
                reset_flags()
            else:
                reply = "Please answer with 'yes' or 'no'."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

        if state.get("awaiting_entrepreneurship_role"):
            session.entrepreneurship_interest = message_text
            listings = await entrepreneurship_client.fetch_entrepreneurship_guides(message_text)
            if listings:
                reply = f"Great! I've saved your interest in *{session.entrepreneurship_interest}*.\n\nHere are the first guides:\n" + "\n".join(listings)
                reply += f"\n\nType 'menu' to return to the main menu."
                reset_flags()
            elif listings == []:
                reply = f"Sorry, I couldn't find any guides for '{message_text}'. Please try another topic."
                state["awaiting_entrepreneurship_role"] = True
            else: # Handles None case
                reply = "Sorry, I'm having trouble connecting to the entrepreneurship service. Please try again later."
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            return

    # --- Fallback ---
    reply = f"❓ I didn't understand that. Please select a number from the menu.\n\n{MAIN_MENU}"
    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
