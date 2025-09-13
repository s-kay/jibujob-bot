# app/services.py
from sqlalchemy.orm import Session
from . import models, whatsapp_client, job_client, training_client, entrepreneurship_client, mentorship_client, resume_builder, interview_simulator, cover_letter_generator, ai_client, skills_analyzer, feedback_handler, crud, file_handler
from . import text_responses



async def process_message(db: Session, session: models.UserSession, message_text: str, is_new_user: bool):
    """
    Main business logic handler for processing user messages with a conversational, keyword-driven flow.
    """
    message_text_original = message_text.strip()
    message_text = message_text_original.lower()
    state = session.session_data

    def clear_temp_state():
        for key in list(state.keys()):
            if key.startswith("awaiting_"):
                state.pop(key, None)
                

    # --- Universal Commands (Highest Priority) ---
    sheng_greetings = ["niaje", "sasa", "vipi", "habari", "mambo"]
    if message_text in ["hi", "hello", "start", "menu", "0"] or any(greeting in message_text for greeting in sheng_greetings):
        session.current_menu = "main"
        state.clear()
        if session.resume_data: session.resume_data.clear()
        
        greeting, introduction, prompt = text_responses.get_greeting_parts(session.user_name, is_new_user=is_new_user, greeting_word=message_text)
        
        await whatsapp_client.send_whatsapp_message(session.phone_number, greeting)
        if introduction:
            await whatsapp_client.send_whatsapp_message(session.phone_number, introduction)
        await whatsapp_client.send_whatsapp_message(session.phone_number, prompt)
        return
    
    # --- On-Demand Data Privacy Policy ---
    if message_text in ["privacy", "sera"]:
        reply = f"Here is our full Privacy Policy:\n{text_responses.PRIVACY_POLICY_URL}"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
        
    # --- Feedback Flow ---
    if message_text in ["feedback", "maoni"] or session.current_menu == "feedback":
        if message_text in ["feedback", "maoni"] and session.current_menu != "feedback":
            session.current_menu = "feedback"; state.clear(); message_text_original = ""
        
        reply, feedback_data, is_complete = feedback_handler.handle_feedback_conversation(session, message_text_original)
        
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        if is_complete:
            if feedback_data:
                crud.save_feedback(db, user_phone_number=session.phone_number, feedback_data=feedback_data)
            session.current_menu = "main"; state.clear()
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_conversational_menu_prompt())
        return
    
    # --- Specialized Post-Flow Handlers ---
    if state.get("awaiting_training_suggestion_confirm"):
        skill_to_learn = state.get("skill_suggestion")

        # Check for empty message first - and handle it properly
        if not message_text_original or not message_text_original.strip():
            print("DEBUG: Empty message received - ignoring completely")
            # Don't send any response, don't update session, just return
            return
        
        if "yes" in message_text and skill_to_learn:
            clear_temp_state()
            session.current_menu = "training"; session.training_interest = skill_to_learn
            listings = await training_client.fetch_trainings(skill_to_learn)
            reply = text_responses.get_empathetic_response("training_found", listings=listings or [], interest=skill_to_learn)
            state["awaiting_another_search"] = True
            reply += "\n\nWould you like to search for another skill?"
        elif "no" in message_text:
            clear_temp_state()
            reply = f"No problem! You can always ask me to find training later.\n\n{text_responses.get_conversational_menu_prompt()}"
            session.current_menu = "main"
        else:
            # Only ask for clarification if there was actual content
            reply = "Please answer with 'yes' or 'no'."
            
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        crud.update_session(db, session)
        return
        
            
    
    
    # --- Keyword-based Intent Routing (Only if at the main menu) ---
    if session.current_menu == "main":
        if any(kw in message_text for kw in ["kazi", "ajira", "job", "mboka", "jobs", "job opportunities", "employment", "career", "works"]): session.current_menu = "jobs"
        elif any(kw in message_text for kw in ["mafunzo", "jifunze", "kusoma", "skill", "training", "education", "learning", "development", "upskill", "learn"]): session.current_menu = "training"
        elif any(kw in message_text for kw in ["ushauri", "mentor", "mentorship", "coaching", "guidance"]): session.current_menu = "mentorship"
        elif any(kw in message_text for kw in ["biashara", "hustle", "business", "entrepreneurship", "startups", "innovation"]): session.current_menu = "entrepreneurship"
        elif any(kw in message_text for kw in ["cv", "resume", "curriculum vitae"]): session.current_menu = "resume_builder"
        elif any(kw in message_text for kw in ["interview", "practice"]): session.current_menu = "interview_practice"
        elif any(kw in message_text for kw in ["cover letter", "barua", "barua ya kazi", "application", "job application"]): session.current_menu = "cover_letter"
        elif any(kw in message_text for kw in ["optimize", "improve cv", "cv enhancement", "cv improvement"]): session.current_menu = "cv_optimizer"
        elif any(kw in message_text for kw in ["analyze", "skill gap", "skills assessment", "skills analysis", "skills audit"]): session.current_menu = "skills_analyzer"

        if session.current_menu != "main":
            message_text_original = "" # Clear message to signal the start of a new flow

    
    
    # --- In-Flow Conversation Logic ---
    # --- Job Search Flow ---   
    if session.current_menu == "jobs":
        if state.get("awaiting_another_search"):
            clear_temp_state()
            if "yes" in message_text:
                state["awaiting_job_role"] = True
                reply = "Great! What other job role are you interested in?"
            else:
                session.current_menu = "main"
                reply = f"No problem! Let me know what you'd like to do next.\n\n{text_responses.get_conversational_menu_prompt()}"
        elif state.get("awaiting_job_role"):
            clear_temp_state()
            session.job_interest = message_text_original
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.job_interest))
            listings = await job_client.fetch_jobs(message_text)
            reply = text_responses.get_empathetic_response("interest_saved_and_jobs_found" if listings else "no_jobs_found", listings=listings or [], interest=session.job_interest)
            state["awaiting_another_search"] = True
            reply += "\n\nWould you like to search for another role? (yes/no)"
        elif state.get("awaiting_job_confirm"):
            clear_temp_state()
            if "yes" in message_text and session.job_interest:
                await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.job_interest))
                listings = await job_client.fetch_jobs(session.job_interest)
                reply = text_responses.get_empathetic_response("jobs_found" if listings else "no_jobs_found", listings=listings or [], interest=session.job_interest)
                state["awaiting_another_search"] = True
                reply += "\n\nWould you like to search for another role? (yes/no)"
            else:
                state["awaiting_job_role"] = True
                reply = "No problem. What new job role are you looking for?"
        else: # Start of flow
            clear_temp_state()
            if session.job_interest:
                state["awaiting_job_confirm"] = True
                reply = f"I remember you were interested in *{session.job_interest}* jobs. Shall I search for those again? (yes/no)"
            else:
                state["awaiting_job_role"] = True
                reply = "🔎 Sounds good! Which type of job are you interested in?"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    # --- CV Builder Flow ---
    elif session.current_menu == "resume_builder":
        session.current_menu = "resume_builder"
        
        # Pass the first message to the handler to kick off the flow
        if any(kw in message_text for kw in ["cv", "resume"]):
            message_text_original = ""

        reply, download_link, is_complete = await resume_builder.handle_resume_conversation(session, message_text_original)
        
        # Persist any changes made to the session.resume_data
        crud.update_session(db, session)
        
        if is_complete:
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            if download_link:
                final_reply = f"Here is a link to your downloadable CV document 👇🏾:\n{download_link}\n\nThis link is private and will expire in 24 hours."
            else:
                final_reply = "Sorry 😕, I had a little trouble creating the downloadable file. I've sent you the plain text version for now."
                if session.resume_data:
                    cv_text = resume_builder.format_cv(session.resume_data)
                    await whatsapp_client.send_whatsapp_message(session.phone_number, cv_text)
            
            session.current_menu = "main"
            final_reply += f"\n\n{text_responses.get_conversational_menu_prompt()}"
            await whatsapp_client.send_whatsapp_message(session.phone_number, final_reply)
        else:
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
    
    # ---Cover letter flow ---
    if session.current_menu == "cover_letter":
        # This flow is now entirely self-contained and robust.
        if state.get("awaiting_similar_jobs_confirm"):
            job_role = state.get("last_cover_letter_role")
            
            if "yes" in message_text and job_role:
                clear_temp_state()
                session.current_menu = "jobs"; session.job_interest = job_role
                await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=job_role))
                listings = await job_client.fetch_jobs(job_role)
                reply = text_responses.get_empathetic_response("jobs_found", listings=listings or [], interest=job_role)
                state["awaiting_another_search"] = True
                reply += "\n\nWould you like to search for another role? (yes/no)"
            elif "no" in message_text:
                clear_temp_state()
                reply = f"No problem! 👊🏾 Best of luck with your application.\n\n{text_responses.get_conversational_menu_prompt()}"
                session.current_menu = "main"
            else:
                if not message_text_original: # Ignore empty/cascading messages
                    crud.update_session(db, session)
                    return 
                reply = "Please answer with 'yes' or 'no'."
        
        elif state.get("awaiting_cl_jd"):
            job_description = message_text_original
            clear_temp_state()
            await whatsapp_client.send_whatsapp_message(session.phone_number, "Excellent 🎉 ! Let me craft a professional cover letter for you...")
            
            if session.resume_data and session.cover_letter_data:
                cv_text = resume_builder.format_cv(session.resume_data)
                company = session.cover_letter_data.get("company_name", "the company")
                role = session.cover_letter_data.get("job_role", "the role")
                
                letter_text = await ai_client.generate_cover_letter(cv_text, company, role, job_description)
                
                if letter_text:
                    filename = f"{session.resume_data.get('full_name', 'user').split(' ')[0]}_{company}.pdf"
                    download_link = await file_handler.generate_and_upload_letter_pdf(letter_text, filename)

                    if download_link:
                        await whatsapp_client.send_whatsapp_message(session.phone_number, f"Your professional cover letter is ready! You can download the PDF here 👇🏾:\n{download_link}")
                    else:
                        await whatsapp_client.send_whatsapp_message(session.phone_number, "😕 I had trouble creating the PDF, but here is the text version:")
                        await whatsapp_client.send_whatsapp_message(session.phone_number, letter_text)

                    state["awaiting_similar_jobs_confirm"] = True
                    state["last_cover_letter_role"] = role
                    reply = f"I can also search for other jobs similar to '{role}'. Would you like me to do that now? (yes/no)"
                else:
                    reply = "😕 Sorry, I had a little trouble generating the letter right now. Please try again in a moment."; session.current_menu = "main"
            else:
                reply = "😕 Sorry, some data was missing. Let's restart."; session.current_menu = "main"

        elif state.get("awaiting_cl_role"):
            if session.cover_letter_data is None: session.cover_letter_data = {}
            session.cover_letter_data["job_role"] = message_text_original
            state.pop("awaiting_cl_role"); state["awaiting_cl_jd"] = True
            reply = "💯 Perfect. Finally, please paste the full job description here."

        elif state.get("awaiting_cl_company"):
            if session.cover_letter_data is None: session.cover_letter_data = {}
            session.cover_letter_data["company_name"] = message_text_original
            state.pop("awaiting_cl_company"); state["awaiting_cl_role"] = True
            reply = "👍🏾 Got it. And what is the exact job role you are applying for?"

        else: # Start of flow
            clear_temp_state()
            if not resume_builder.has_existing_cv(session.resume_data or {}):
                reply = "It's best to build a CV first so I have your details. Just ask `build a CV`"
                session.current_menu = "main"
            else:
                session.cover_letter_data = {}
                state["awaiting_cl_company"] = True
                reply = "👍🏾 Let's get started on your cover letter. What is the name of the company you are applying to?"

        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return


    # --- Training Flow ---
    elif session.current_menu == "training":
        if state.get("awaiting_another_search"):
            clear_temp_state()
            if "yes" in message_text:
                state["awaiting_training_role"] = True; 
                reply = "Great! What other skill are you interested in?"
            else:
                session.current_menu = "main"; 
                reply = f"💯 You got it! Let me know what you'd like to do next.\n\n{text_responses.get_conversational_menu_prompt()}"
        elif state.get("awaiting_training_role"):
            clear_temp_state(); 
            session.training_interest = message_text_original
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.training_interest))
            listings = await training_client.fetch_trainings(message_text)
            reply = text_responses.get_empathetic_response("interest_saved_and_training_found" if listings else "no_training_found", listings=listings or [], interest=session.training_interest)
            state["awaiting_another_search"] = True; 
            reply += "\n\nWould you like to search for another skill? (yes/no)"
        elif state.get("awaiting_training_confirm"):
            clear_temp_state()
            if "yes" in message_text and session.training_interest:
                await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.training_interest))
                listings = await training_client.fetch_trainings(session.training_interest)
                reply = text_responses.get_empathetic_response("training_found" if listings else "no_training_found", listings=listings or [], interest=session.training_interest)
                state["awaiting_another_search"] = True; 
                reply += "\n\nWould you like to search for another skill? (yes/no)"
            else:
                state["awaiting_training_role"] = True; 
                reply = "No problem. What new skill are you interested in?"
        else: # Start of flow
            clear_temp_state()
            if session.training_interest:
                state["awaiting_training_confirm"] = True; 
                reply = f"Last time you were looking into *{session.training_interest}* training. Should we look for more courses on that? (yes/no)"
            else:
                state["awaiting_training_role"] = True; 
                reply = "📚 Happy to help! What new skill are you interested in learning?"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return

    # --- Interview Entrepreneurship Flow ---
    elif session.current_menu == "entrepreneurship":
        if state.get("awaiting_another_search"):
            clear_temp_state()
            if "yes" in message_text:
                state["awaiting_business_topic"] = True
                reply = "Great! What other entrepreneurship topic are you interested in?"
            else:
                session.current_menu = "main"
                reply = f"No problem! Let me know what you'd like to do next.\n\n{text_responses.get_conversational_menu_prompt()}"
        elif state.get("awaiting_business_topic"):
            clear_temp_state()
            session.entrepreneurship_interest = message_text_original
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.entrepreneurship_interest))
            listings = await entrepreneurship_client.fetch_entrepreneurship_guides(message_text)
            reply = text_responses.get_empathetic_response("interest_saved_and_guides_found" if listings else "no_guides_found", listings=listings or [], interest=session.entrepreneurship_interest)
            state["awaiting_another_search"] = True
            reply += "\n\nWould you like to search for another topic? (yes/no)"
        elif state.get("awaiting_business_confirm"):
            clear_temp_state()
            if "yes" in message_text and session.entrepreneurship_interest:
                await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.entrepreneurship_interest))
                listings = await entrepreneurship_client.fetch_entrepreneurship_guides(session.entrepreneurship_interest)
                reply = text_responses.get_empathetic_response("guides_found" if listings else "no_guides_found", listings=listings or [], interest=session.entrepreneurship_interest)
                state["awaiting_another_search"] = True
                reply += "\n\nWould you like to search for another topic? (yes/no)"
            else:
                state["awaiting_business_topic"] = True
                reply = "No problem. What new entrepreneurship topic are you looking for?"
        else: # Start of flow
            clear_temp_state()
            if session.entrepreneurship_interest:
                state["awaiting_business_confirm"] = True
                reply = f"I remember you were interested in *{session.entrepreneurship_interest}* entrepreneurship topics. Shall I search for those again? (yes/no)"
            else:
                state["awaiting_business_topic"] = True
                reply = "🚀 Fantastic! What entrepreneurship topic are you interested in?"  

        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
    
    # --- Mentorship Flow ---
    if session.current_menu == "mentorship":
        if state.get("awaiting_another_search"):
            clear_temp_state()
            if "yes" in message_text:
                state["awaiting_mentor_topic"] = True
                reply = "Great! What other mentorship topic are you interested in?"
            else:
                session.current_menu = "main"
                reply = f"No problem! Let me know what you'd like to do next.\n\n{text_responses.get_conversational_menu_prompt()}"
        elif state.get("awaiting_mentor_topic"):
            clear_temp_state()
            session.mentorship_interest = message_text_original
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.mentorship_interest))
            listings = await mentorship_client.fetch_mentors(message_text)
            reply = text_responses.get_empathetic_response("interest_saved_and_mentors_found" if listings else "no_mentors_found", listings=listings or [], interest=session.mentorship_interest)
            state["awaiting_another_search"] = True
            reply += "\n\nWould you like to search for another topic? (yes/no)"
        elif state.get("awaiting_mentor_confirm"):
            clear_temp_state()
            if "yes" in message_text and session.mentorship_interest:
                await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.mentorship_interest))
                listings = await mentorship_client.fetch_mentors(session.mentorship_interest)
                reply = text_responses.get_empathetic_response("mentors_found" if listings else "no_mentors_found", listings=listings or [], interest=session.mentorship_interest)
                state["awaiting_another_search"] = True
                reply += "\n\nWould you like to search for another topic? (yes/no)"
            else:
                state["awaiting_mentor_topic"] = True
                reply = "No problem. What new mentorship topic are you looking for?"
        else: # Start of flow
            clear_temp_state()
            if session.mentorship_interest:
                state["awaiting_mentor_confirm"] = True
                reply = f"I remember you were interested in *{session.mentorship_interest}* mentorship topics. Shall I search for those again? (yes/no)"
            else:
                state["awaiting_mentor_topic"] = True
                reply = "🗣️ Wonderful! What mentorship topic are you interested in?"
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
    
    
    # --- CV Optimizer Flow ---
    elif session.current_menu == "cv_optimizer":
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
            session.current_menu = "main"; 
            clear_temp_state(); 
            reply = f"\n\n{text_responses.get_conversational_menu_prompt()}"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

        elif state.get("awaiting_job_description_for_opt"):
            job_description = message_text_original
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
                    session.current_menu = "main"; 
            clear_temp_state()
        else:
            session.current_menu = "cv_optimizer"; clear_temp_state()
            if not session.resume_data or not session.resume_data.get('full_name'):
                reply = "To optimize your CV, I need your details first. Please use option 5 to build your CV, and then come right back!"; session.current_menu = "main"
            else:
                reply = "Excellent! To get started, please paste the full job description for the role you're applying for."; state["awaiting_job_description_for_opt"] = True
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return


    
    # --- Interview Practice Flow ---
    elif session.current_menu == "interview_practice":
        if state.get("awaiting_interview_role_confirm"):
            if message_text in ["yes", "y"] and session.job_interest:
                message_text = session.job_interest; clear_temp_state()
            elif message_text in ["no", "n"]:
                state.pop("awaiting_interview_role_confirm", None); state["awaiting_interview_role"] = True
                reply = "Okay, what job role would you like to practice for instead?"
                await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                return
            else:
                reply = "Please answer with 'yes' or 'no'."; await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                return

        if (message_text == "interview_practice" and session.current_menu == "main") or state.get("awaiting_interview_role"):
            session.current_menu = "interview_practice"
            if not state.get("awaiting_interview_role"): # First time entry
                clear_temp_state()
                if session.job_interest: reply = f"Let's practice for an interview! I see your saved interest is *{session.job_interest}*. Would you like to practice for that role? (yes/no)"; state["awaiting_interview_role_confirm"] = True
                else: reply = "Let's practice for an interview! What job role are you preparing for? (e.g., Accountant, Sales)"; state["awaiting_interview_role"] = True
                await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                return

        reply, is_complete = interview_simulator.handle_interview_conversation(session, message_text_original)
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        if is_complete:
            session.current_menu = "main"; await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
    

        # --- Skills Analyzer Flow ---
    elif session.current_menu == "skills_analyzer":
        if state.get("awaiting_jd_for_analysis"):
            job_description = message_text_original
            await whatsapp_client.send_whatsapp_message(session.phone_number, "Analyzing your skills against the job description... This AI-powered step might take a moment.")
            if session.resume_data:
                analysis, missing_skills = await skills_analyzer.analyze_skills_gap(session, job_description)
                if analysis: await whatsapp_client.send_whatsapp_message(session.phone_number, analysis)
                if missing_skills:
                    skill_to_suggest = missing_skills[0]
                    reply = f"The good news is you can learn these! Would you like me to search for training courses on *{skill_to_suggest}* right now? (yes/no)"
                    state["awaiting_training_suggestion_confirm"] = True; state["skill_suggestion"] = skill_to_suggest; clear_temp_state()
                    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
                else:
                    session.current_menu = "main"; 
                    clear_temp_state(); 
                    reply = f"Great news! You seem to have all the key skills for this role.\n\n{text_responses.get_conversational_menu_prompt()}"
                    await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        else:
            session.current_menu = "skills_analyzer"; clear_temp_state()
            if not session.resume_data or not session.resume_data.get('full_name'):
                reply = "To analyze your skills gap, I need your CV details first. Please use option 5 to build your CV, then come right back!"; session.current_menu = "main"
            else:
                reply = "This is a powerful tool! To start, please paste the full job description you are targeting."; state["awaiting_jd_for_analysis"] = True
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        return
    
    

    # --- Fallback (If no intent was detected and not in a flow) ---
    else:
        reply = f"❓ Sorry, I didn't quite get that. What would you like to do? `find a job`, `build a CV`, and more."
        await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

