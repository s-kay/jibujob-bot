# app/services.py
from sqlalchemy.orm import Session
from . import models, whatsapp_client, job_client, training_client, entrepreneurship_client, mentorship_client, resume_builder, interview_simulator, cover_letter_generator, ai_client, skills_analyzer
from . import text_responses

async def process_message(db: Session, session: models.UserSession, message_text: str, is_new_user: bool):
    """
    Main business logic handler for processing user messages with persistence.
    """
    message_text_original = message_text # Keep original case for saving, but use lower for logic
    message_text = message_text.strip().lower()
    state = session.session_data

    def reset_flags():
        for key in list(state.keys()):
            if key.startswith("awaiting_"):
                state[key] = False

    # --- Universal Commands (Highest Priority) ---
    if message_text in ["hi", "hello", "start", "menu"]:
        session.current_menu = "main"
        reset_flags()
        greeting, introduction = text_responses.get_greeting_parts(session.user_name, is_new_user=is_new_user)
        await whatsapp_client.send_whatsapp_message(session.phone_number, greeting)
        if introduction:
            await whatsapp_client.send_whatsapp_message(session.phone_number, introduction)
        await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_main_menu())
        return

    if message_text == "0":
        session.current_menu = "main"
        reset_flags()
        session.session_data = {}
        reply = "👋 Your session has been reset. Type 'hi' to start again with a fresh menu."
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    # --- Specialized Handlers (Second Priority) ---
    if state.get("awaiting_training_suggestion_confirm"):
        skill_to_learn = state.get("skill_suggestion")
        if message_text in ["yes", "y"] and skill_to_learn:
            session.current_menu = "training"; session.training_interest = skill_to_learn; reset_flags()
            listings = await training_client.fetch_trainings(skill_to_learn)
            reply = text_responses.get_empathetic_response("training_found" if listings else "no_training_found", listings=listings or [], interest=skill_to_learn)
        else:
            reply = "No problem! You can always come back and search for training later."
        session.current_menu = "main"; reset_flags()
        reply += f"\n\n{text_responses.get_main_menu()}"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
        
    if state.get("awaiting_similar_jobs_confirm"):
        job_role = session.cover_letter_data.get("job_role")
        if message_text in ["yes", "y"] and job_role:
            session.job_interest = job_role
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=job_role))
            listings = await job_client.fetch_jobs(job_role)
            reply = text_responses.get_empathetic_response("jobs_found" if listings else "no_jobs_found", listings=listings or [], interest=job_role)
        else:
            reply = "No problem! Let me know what you'd like to do next."
        session.current_menu = "main"; reset_flags()
        reply += f"\n\n{text_responses.get_main_menu()}"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    # --- Sequential Conversation Flow Handlers ---
    if message_text == "1" or session.current_menu == "jobs":
        session.current_menu = "jobs"
        if state.get("awaiting_job_role"):
            if message_text.isdigit():
                reply = "Please type a job role (e.g., 'Accountant'), not a number."
            else:
                session.job_interest = message_text_original
                await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.job_interest))
                listings = await job_client.fetch_jobs(message_text)
                reply = f"Great! I've saved your interest in *{session.job_interest}*.\n" + text_responses.get_empathetic_response("jobs_found" if listings else "no_jobs_found", listings=listings or [], interest=session.job_interest)
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
        elif state.get("awaiting_job_confirm"):
            if message_text in ["yes", "y"]:
                if session.job_interest:
                    await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.job_interest))
                    listings = await job_client.fetch_jobs(session.job_interest)
                    reply = text_responses.get_empathetic_response("jobs_found" if listings else "no_jobs_found", listings=listings or [], interest=session.job_interest)
                else:
                    reply = "Something went wrong. What job are you looking for?"; state["awaiting_job_role"] = True
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
            elif message_text in ["no", "n"]:
                state.pop("awaiting_job_confirm", None); state["awaiting_job_role"] = True
                reply = "No problem. What new job role are you looking for?"
            else: reply = "Please answer with 'yes' or 'no'."
        else:
            reset_flags()
            if session.job_interest: state["awaiting_job_confirm"] = True; reply = f"I remember you were interested in *{session.job_interest}* jobs. Shall I search for those again? (yes/no)"
            else: state["awaiting_job_role"] = True; reply = "🔎 Sounds good! Which type of job are you interested in? (e.g., Software Developer, Accountant)"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    elif message_text == "2" or session.current_menu == "training":
        session.current_menu = "training"
        if state.get("awaiting_training_role"):
            if message_text.isdigit():
                reply = "Please type a skill (e.g., 'Digital Skills'), not a number."
            else:
                session.training_interest = message_text_original
                listings = await training_client.fetch_trainings(message_text)
                reply = f"Great! I've saved your interest in *{session.training_interest}*.\n" + text_responses.get_empathetic_response("training_found" if listings else "no_training_found", listings=listings or [], interest=session.training_interest)
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
        elif state.get("awaiting_training_confirm"):
            if message_text in ["yes", "y"]:
                if session.training_interest:
                    listings = await training_client.fetch_trainings(session.training_interest)
                    reply = text_responses.get_empathetic_response("training_found" if listings else "no_training_found", listings=listings or [], interest=session.training_interest)
                else: reply = "I don't have a saved training interest for you. What skill would you like to learn?"; state["awaiting_training_role"] = True
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
            elif message_text in ["no", "n"]:
                state.pop("awaiting_training_confirm", None); state["awaiting_training_role"] = True
                reply = "Sounds good. What new skill are you interested in learning today?"
            else: reply = "Please answer with 'yes' or 'no'."
        else:
            reset_flags()
            if session.training_interest: state["awaiting_training_confirm"] = True; reply = f"Last time you were looking into *{session.training_interest}* training. Should we look for more courses on that? (yes/no)"
            else: state["awaiting_training_role"] = True; reply = "📚 Happy to help! What new skill are you interested in learning? (e.g., AI, Digital Skills)"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    # ... (The rest of the flows would be updated with the same isdigit() check) ...

    else:
        reply = f"❓ Sorry, I didn't quite get that. Here's the main menu again.\n\n{text_responses.get_main_menu()}"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
