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
    sheng_greetings = ["niaje", "sasa", "vipi", "habari"]
    if message_text in ["hi", "hello", "start", "menu"] or any(greeting in message_text for greeting in sheng_greetings):
        session.current_menu = "main"
        reset_flags()
        if any(greeting in message_text for greeting in sheng_greetings):
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_sheng_greeting_response())
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
        reply = "👋🏾 Your session has been reset. Type 'hi' to start again with a fresh menu."
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
        
    # --- Keyword-based Routing (Hybrid NLP Model) ---
    if session.current_menu == "main":
        if "kazi" in message_text or "ajira" in message_text or "wera" in message_text or "mboka" in message_text or "works" in message_text: message_text = "1"
        elif "mafunzo" in message_text or "jifunza" in message_text or "kusoma" in message_text: message_text = "2"
        elif "ushauri" in message_text: message_text = "3"
        elif "biashara" in message_text: message_text = "4"

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
        job_role = session.cover_letter_data.get("job_role") if session.cover_letter_data else None
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
                reply = "🔎 Which type of job are you interested in? (e.g., Software Developer, Accountant)"
            else:
                session.job_interest = message_text_original
                await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.job_interest))
                listings = await job_client.fetch_jobs(message_text)
                reply = text_responses.get_empathetic_response("interest_saved_and_jobs_found" if listings else "no_jobs_found", listings=listings or [], interest=session.job_interest)
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
        elif state.get("awaiting_job_confirm"):
            if message_text in ["yes", "y"]:
                if session.job_interest:
                    await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.job_interest))
                    listings = await job_client.fetch_jobs(session.job_interest)
                    reply = text_responses.get_empathetic_response("jobs_found" if listings else "no_jobs_found", listings=listings or [], interest=session.job_interest)
                else:
                    reply = "Hmm! 🤔 Something seems to have gone wrong. What job are you looking for?"; state["awaiting_job_role"] = True
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
            elif message_text in ["no", "n"]:
                state.pop("awaiting_job_confirm", None); state["awaiting_job_role"] = True
                reply = "👍🏾 No problem. What new job role are you looking for?"
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
                reply = "Please type in a skill (e.g., 'Digital Skills'), not a number."
            else:
                session.training_interest = message_text_original
                listings = await training_client.fetch_trainings(message_text)
                reply = text_responses.get_empathetic_response("interest_saved_and_training_found" if listings else "no_training_found", listings=listings or [], interest=session.training_interest)
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
        elif state.get("awaiting_training_confirm"):
            if message_text in ["yes", "y"]:
                if session.training_interest:
                    listings = await training_client.fetch_trainings(session.training_interest)
                    reply = text_responses.get_empathetic_response("training_found" if listings else "no_training_found", listings=listings or [], interest=session.training_interest)
                else: reply = "Ooh! I don't have a saved training interest for you 😕. What skill would you like to learn? 📚"; state["awaiting_training_role"] = True
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

    elif message_text == "3" or session.current_menu == "mentorship":
        session.current_menu = "mentorship"
        if state.get("awaiting_mentorship_role"):
            if message_text.isdigit():
                reply = "Please type a field (e.g., 'Tech'), not a number."
            else:
                session.mentorship_interest = message_text_original
                listings = await mentorship_client.fetch_mentors(message_text)
                reply = text_responses.get_empathetic_response("interest_saved_and_mentors_found" if listings else "no_mentors_found", listings=listings or [], interest=session.mentorship_interest)
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
        elif state.get("awaiting_mentorship_confirm"):
            if message_text in ["yes", "y"]:
                if session.mentorship_interest:
                    listings = await mentorship_client.fetch_mentors(session.mentorship_interest)
                    reply = text_responses.get_empathetic_response("mentors_found" if listings else "no_mentors_found", listings=listings or [], interest=session.mentorship_interest)
                else: reply = "I don't seem to have a saved mentorship interest for you. What field are you looking for? 🤔"; state["awaiting_mentorship_role"] = True
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
            elif message_text in ["no", "n"]:
                state.pop("awaiting_mentorship_confirm", None); state["awaiting_mentorship_role"] = True
                reply = "It's not a problem 😀. What new field are you interested in finding a mentor for?"
            else: reply = "Please answer with 'yes' or 'no'."
        else:
            reset_flags()
            if session.mentorship_interest: state["awaiting_mentorship_confirm"] = True; reply = f"I remember you were looking for a mentor in *{session.mentorship_interest}*. Shall we search for experts in that field again? (yes/no)"
            else: state["awaiting_mentorship_role"] = True; reply = "Connecting with a mentor is a great idea! What field are you looking for guidance in? (e.g., Tech, Business)"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
        
    elif message_text == "4" or session.current_menu == "entrepreneurship":
        session.current_menu = "entrepreneurship"
        if state.get("awaiting_entrepreneurship_role"):
            if message_text.isdigit():
                reply = "Please type a business area (e.g., 'Agribusiness'), not a number."
            else:
                session.entrepreneurship_interest = message_text_original
                listings = await entrepreneurship_client.fetch_entrepreneurship_guides(message_text)
                reply = text_responses.get_empathetic_response("interest_saved_and_guides_found" if listings else "no_guides_found", listings=listings or [], interest=session.entrepreneurship_interest)
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
        elif state.get("awaiting_entrepreneurship_confirm"):
            if message_text in ["yes", "y"]:
                if session.entrepreneurship_interest:
                    listings = await entrepreneurship_client.fetch_entrepreneurship_guides(session.entrepreneurship_interest)
                    reply = text_responses.get_empathetic_response("guides_found" if listings else "no_guides_found", listings=listings or [], interest=session.entrepreneurship_interest)
                else: reply = "Hmm! 🤔, I don't seem to have a saved business interest for you. What business idea are you exploring?"; state["awaiting_entrepreneurship_role"] = True
                session.current_menu = "main"; reset_flags()
                reply += f"\n\n{text_responses.get_main_menu()}"
            elif message_text in ["no", "n"]:
                state.pop("awaiting_entrepreneurship_confirm", None); state["awaiting_entrepreneurship_role"] = True
                reply = "No worries! What new business idea are you thinking about?"
            else: reply = "Please answer with 'yes' or 'no'."
        else:
            reset_flags()
            if session.entrepreneurship_interest: state["awaiting_entrepreneurship_confirm"] = True; reply = f"Last time we were looking at guides for *{session.entrepreneurship_interest}*. Want to explore that again? (yes/no)"
            else: state["awaiting_entrepreneurship_role"] = True; reply = "💡 Awesome! Exploring a business idea is a great step. What field are you interested in? (e.g., Agribusiness, E-commerce)"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    elif message_text == "5" or session.current_menu == "resume_builder":
        if message_text == "5" and session.current_menu == "main":
            session.current_menu = "resume_builder"; session.resume_data = {}; reset_flags(); message_text = "" 
        reply, is_complete = resume_builder.handle_resume_conversation(session, message_text)
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        if is_complete:
            session.current_menu = "main"; await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_main_menu())
        return

    elif message_text == "6" or session.current_menu == "interview_practice":
        if state.get("awaiting_interview_role_confirm"):
            if message_text in ["yes", "y"] and session.job_interest:
                message_text = session.job_interest; reset_flags()
            elif message_text in ["no", "n"]:
                state.pop("awaiting_interview_role_confirm", None); state["awaiting_interview_role"] = True
                reply = "Okay, what job role would you like to practice for instead?"
                await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                return
            else:
                reply = "Please answer with 'yes' or 'no'."; await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                return
        
        if (message_text == "6" and session.current_menu == "main") or state.get("awaiting_interview_role"):
            session.current_menu = "interview_practice"
            if not state.get("awaiting_interview_role"): # First time entry
                reset_flags()
                if session.job_interest: reply = f"Let's practice for an interview! I see your saved interest is *{session.job_interest}*. Would you like to practice for that role? (yes/no)"; state["awaiting_interview_role_confirm"] = True
                else: reply = "Let's practice for an interview! What job role are you preparing for? (e.g., Accountant, Sales)"; state["awaiting_interview_role"] = True
                await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                return

        reply, is_complete = interview_simulator.handle_interview_conversation(session, message_text)
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        if is_complete:
            session.current_menu = "main"; await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_main_menu())
        return

    elif message_text == "7" or session.current_menu == "cover_letter":
        if message_text == "7" and session.current_menu == "main":
            if not session.resume_data or not session.resume_data.get('full_name'):
                reply = "It's best to build a CV first so I have your details. Please choose option 5 from the menu to create your CV, then come back here!"
                await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                return
            session.current_menu = "cover_letter"; session.cover_letter_data = {}; reset_flags(); message_text = "" 
        reply, is_complete = cover_letter_generator.handle_cover_letter_conversation(session, message_text)
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        if is_complete: pass
        return
        
    elif message_text == "8" or session.current_menu == "cv_optimizer":
        if state.get("awaiting_rewrite_confirm"):
            if message_text in ["yes", "y"]:
                await whatsapp_client.send_whatsapp_message(session.phone_number, "Perfect! I'll get to work on rewriting those sections. This is an advanced AI task, so it might take up to a minute...")
                if session.resume_data:
                    cv_text = resume_builder.format_cv(session.resume_data)
                    job_description = state.get("last_jd_for_opt", ""); feedback = state.get("last_cv_feedback", "")
                    rewritten_sections = await ai_client.rewrite_cv_sections(cv_text, job_description, feedback)
                    if rewritten_sections: await whatsapp_client.send_whatsapp_message(session.phone_number, rewritten_sections)
                    else: await whatsapp_client.send_whatsapp_message(session.phone_number, "Sorry, I wasn't able to rewrite the sections at this time.")
            else: await whatsapp_client.send_whatsapp_message(session.phone_number, "No problem! You can apply the feedback manually. Let me know what you'd like to do next.")
            session.current_menu = "main"; reset_flags(); await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_main_menu())
        elif state.get("awaiting_job_description_for_opt"):
            job_description = message_text
            await whatsapp_client.send_whatsapp_message(session.phone_number, "Analyzing your CV against the job description... This might take a moment.")
            if session.resume_data:
                cv_text = resume_builder.format_cv(session.resume_data)
                feedback = await ai_client.optimize_resume(cv_text, job_description)
                if feedback:
                    await whatsapp_client.send_whatsapp_message(session.phone_number, feedback)
                    state["last_cv_feedback"] = feedback; state["last_jd_for_opt"] = job_description; state["awaiting_rewrite_confirm"] = True
                    reply = "Would you like me to try and rewrite your CV summary and experience sections based on this feedback for you? (yes/no)"
                    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                else:
                    await whatsapp_client.send_whatsapp_message(session.phone_number, "Sorry, I couldn't get feedback for you right now. Please try again later.")
                    session.current_menu = "main"; await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_main_menu())
            reset_flags()
        else:
            session.current_menu = "cv_optimizer"; reset_flags()
            if not session.resume_data or not session.resume_data.get('full_name'):
                reply = "To optimize your CV, I need your details first. Please use option 5 to build your CV, and then come right back!"; session.current_menu = "main"
            else:
                reply = "Excellent! To get started, please paste the full job description for the role you're applying for."; state["awaiting_job_description_for_opt"] = True
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    elif message_text == "9" or session.current_menu == "skills_analyzer":
        if state.get("awaiting_jd_for_analysis"):
            job_description = message_text
            await whatsapp_client.send_whatsapp_message(session.phone_number, "Analyzing your skills against the job description... This AI-powered step might take a moment.")
            if session.resume_data:
                analysis, missing_skills = await skills_analyzer.analyze_skills_gap(session, job_description)
                if analysis: await whatsapp_client.send_whatsapp_message(session.phone_number, analysis)
                if missing_skills:
                    skill_to_suggest = missing_skills[0]
                    reply = f"The good news is you can learn these! Would you like me to search for training courses on *{skill_to_suggest}* right now? (yes/no)"
                    state["awaiting_training_suggestion_confirm"] = True; state["skill_suggestion"] = skill_to_suggest; reset_flags()
                    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                else:
                    session.current_menu = "main"; reset_flags(); await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_main_menu())
        else:
            session.current_menu = "skills_analyzer"; reset_flags()
            if not session.resume_data or not session.resume_data.get('full_name'):
                reply = "To analyze your skills gap, I need your CV details first. Please use option 5 to build your CV, then come right back!"; session.current_menu = "main"
            else:
                reply = "This is a powerful tool! To start, please paste the full job description you are targeting."; state["awaiting_jd_for_analysis"] = True
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    # Fallback if no specific state was handled and not in a flow
    else:
        reply = f"❓ Sorry, I didn't quite get that. Here's the main menu again.\n\n{text_responses.get_main_menu()}"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

