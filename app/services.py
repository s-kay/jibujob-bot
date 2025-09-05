# app/services.py
from sqlalchemy.orm import Session
from . import models, whatsapp_client, job_client, training_client, entrepreneurship_client, mentorship_client, resume_builder, interview_simulator, cover_letter_generator, ai_client, skills_analyzer, feedback_handler, crud, file_handler
from . import text_responses

async def process_message(db: Session, session: models.UserSession, message_text: str, is_new_user: bool):
    """
    Main business logic handler for processing user messages with persistence.
    """
    message_text_original = message_text.strip()
    message_text = message_text_original.lower()
    state = session.session_data

    # Helper to clear temporary conversational flags
    def clear_temp_state():
        for key in list(state.keys()):
            if key.startswith("awaiting_") or key.endswith("_step"):
                state.pop(key, None)

    # --- Universal Commands (Highest Priority) ---
    sheng_greetings = ["niaje", "sasa", "vipi", "habari", "mambo"]
    if message_text in ["hi", "hello", "start", "menu"] or any(greeting in message_text for greeting in sheng_greetings):
        session.current_menu = "main"
        state.clear()
        if session.resume_data:
            session.resume_data.clear() # Also clear feature-specific state
        greeting, introduction = text_responses.get_greeting_parts(session.user_name, is_new_user=is_new_user)
        await whatsapp_client.send_whatsapp_message(session.phone_number, greeting)
        if introduction:
            await whatsapp_client.send_whatsapp_message(session.phone_number, introduction)
        await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_main_menu())
        return

    if message_text == "0":
        session.current_menu = "main"
        state.clear()
        if session.resume_data:
            session.resume_data.clear()
        reply = "👋🏾 Your session has been reset. Type 'hi' to start again with a fresh menu."
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
        
    # --- Feedback Flow ---
    if message_text in ["feedback", "maoni"] or session.current_menu == "feedback":
        if message_text in ["feedback", "maoni"] and session.current_menu != "feedback":
            session.current_menu = "feedback"; state.clear(); message_text = "" 
        reply, feedback_data, is_complete = feedback_handler.handle_feedback_conversation(session, message_text_original)
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        if is_complete:
            if feedback_data:
                crud.save_feedback(db, user_phone_number=session.phone_number, feedback_data=feedback_data)
            session.current_menu = "main"; state.clear()
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_main_menu())
        return

    # --- Main Menu Router ---
    if session.current_menu == "main":
        if "kazi" in message_text or "ajira" in message_text: message_text = "1"
        elif "mafunzo" in message_text or "jifunze" in message_text or "kusoma" in message_text: message_text = "2"
        elif "ushauri" in message_text: message_text = "3"
        elif "biashara" in message_text: message_text = "4"
        
        if message_text == "1": session.current_menu = "jobs"
        elif message_text == "2": session.current_menu = "training"
        elif message_text == "3": session.current_menu = "mentorship"
        elif message_text == "4": session.current_menu = "entrepreneurship"
        elif message_text == "5": session.current_menu = "resume_builder"
        elif message_text == "6": session.current_menu = "interview_practice"
        elif message_text == "7": session.current_menu = "cover_letter"
        elif message_text == "8": session.current_menu = "cv_optimizer"
        elif message_text == "9": session.current_menu = "skills_analyzer"
        
        if session.current_menu != "main":
             message_text = "" # Clear message to signal start of a new flow

    # --- Sequential Conversation Flow Handlers ---

    if session.current_menu == "resume_builder":
        # This is the new, robust, and corrected logic for the CV builder.
        # It calls the handler and then processes the result.
        
        # Entry point for the flow
        if message_text == "" and not state and not (session.resume_data and session.resume_data.get('is_complete')):
             # This is a fresh start, clear any old data
             session.resume_data = {}

        reply, download_link, is_complete = await resume_builder.handle_resume_conversation(session, message_text_original)

        # If the handler says the conversation is over, we send the final messages.
        if is_complete:
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            if download_link:
                final_reply = f"Here is a link to your downloadable CV document:\n{download_link}\n\nThis link is private and will expire in 24 hours."
            else:
                final_reply = "Sorry, I had a little trouble creating the downloadable file. I've sent you the plain text version for now."
                cv_text = resume_builder.format_cv(session.resume_data or {})
                await whatsapp_client.send_whatsapp_message(session.phone_number, cv_text)

            session.current_menu = "main"
            if session.resume_data is not None:
                session.resume_data.clear() # Clean up the state after completion
            final_reply += f"\n\n{text_responses.get_main_menu()}"
            await whatsapp_client.send_whatsapp_message(session.phone_number, final_reply)
        
        # If the conversation is not over, we just send the next question.
        else:
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    # Fallback if no specific flow was handled
    else:
        # Check if we were in the middle of a flow but the input didn't match any state
        if session.current_menu != "main":
             reply = "Sorry, I was expecting a different kind of answer there. Let's go back to the main menu for now."
             session.current_menu = "main"
             state.clear()
        else:
             reply = f"❓ Sorry, I didn't quite get that."
        
        reply += f"\n\n{text_responses.get_main_menu()}"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

