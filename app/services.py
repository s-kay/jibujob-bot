# app/services.py
from sqlalchemy.orm import Session
from . import application_assistant, models, whatsapp_client, job_client, training_client, entrepreneurship_client, mentorship_client, resume_builder, interview_simulator, cover_letter_generator, ai_client, skills_analyzer, feedback_handler, crud, file_handler
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
        
        # --- THE NEW "INTELLIGENT RETURN" HANDLER ---
    if state.get("awaiting_post_cv_analysis_confirm"):
        state.clear()
        if "yes" in message_text:
            # Send the user back to the start of the job search flow
            session.current_menu = "jobs"
            if session.job_interest:
                state["awaiting_job_confirm"] = True
                reply = f"Great! I remember you were interested in *{session.job_interest}* jobs. Shall I search for those again? (yes/no)"
            else:
                state["awaiting_job_role"] = True
                reply = "Excellent! Which type of job are you interested in?"
        else:
            session.current_menu = "main"
            reply = f"No problem! Let me know what you'd like to do next.\n\n{text_responses.get_conversational_menu_prompt()}"
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

    
    
        # --- Job Search Flow ---   
    if session.current_menu == "jobs":
        session.current_menu = "jobs"

        # Step 5: Handle the follow-up after an agent run or job view
        if state.get("awaiting_another_search"):
            state.clear()
            if "yes" in message_text:
                if session.job_interest:
                    state["awaiting_job_confirm"] = True
                    reply = f"I remember you were interested in *{session.job_interest}* jobs. Shall I search for those again? (yes/no)"
                else:
                    state["awaiting_job_role"] = True
                    reply = "Great! What other job role are you interested in?"
            else:
                session.current_menu = "main"
                reply = "No problem! Let me know what you'd like to do next.\n\nWhat would you like to do, find a job, build a CV, or practice for an interview? Just let me know!"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

        # Step 4: Handle the user's decision to run the AI analysis
        elif state.get("awaiting_analysis_confirmation"):
            selected_job = state.get("selected_job_for_analysis")
            if "yes" in message_text and selected_job:
                state.clear()
                report, success = await application_assistant.analyze_and_draft(session, selected_job)
                await whatsapp_client.send_whatsapp_message(session.phone_number, report)
                state["awaiting_another_search"] = True
                await whatsapp_client.send_whatsapp_message(session.phone_number, "Would you like to search for another job? (yes/no)")
            else:
                state.clear()
                state["awaiting_another_search"] = True
                reply = "Okay, no problem. Would you like to select a different job from the list, or would you prefer to search for a new role?"
                await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

        # Step 3: Handle the user's selection of a specific job
        elif state.get("awaiting_job_selection"):
            
            # Check if the user wants to analyze the job they just viewed
            if "analyze" in message_text:
                if not resume_builder.has_existing_cv(session.resume_data or {}):
                    # THE FIX: Set hook and redirect to CV builder
                    state["post_cv_creation_hook"] = "analyze_job"
                    state["selected_job_for_post_cv"] = state.get("last_viewed_job")
                    session.current_menu = "resume_builder"
                    await whatsapp_client.send_whatsapp_message(session.phone_number, "You'll need a CV first. Just type `CV` to build one now.")
                    crud.update_session(db, session)
                    return
                else:
                    selected_job = state.get("last_viewed_job")
                    if selected_job:
                        state.clear()
                        report, success = await application_assistant.analyze_and_draft(session, selected_job)
                        await whatsapp_client.send_whatsapp_message(session.phone_number, report)
                        state["awaiting_another_search"] = True
                        await whatsapp_client.send_whatsapp_message(session.phone_number, "Would you like to search for another job? (yes/no)")
                    else:
                        await whatsapp_client.send_whatsapp_message(session.phone_number, "Sorry, I seem to have lost track of the job you were viewing. Please select a number from the list again.")

            elif message_text.lower() in ['cv', 'resume']:
                # THE FIX: Set hook and redirect to CV builder
                state["post_cv_creation_hook"] = "analyze_job"
                state["selected_job_for_post_cv"] = state.get("last_viewed_job")
                session.current_menu = "resume_builder"
                crud.update_session(db, session)
                # Call resume builder flow immediately
                await process_message(db, session, "", is_new_user)
                return
            
            else: # Assume they sent a number to select a job
                try:
                    choice_index = int(message_text_original) - 1
                    job_list = state.get("last_job_search_results", [])
                    
                    if 0 <= choice_index < len(job_list):
                        selected_job = job_list[choice_index]
                        state["last_viewed_job"] = selected_job
                        key_skills = await ai_client.extract_key_skills(selected_job.get("description", ""))
                        job_card = f"Here are the details for that role:\n\n*{selected_job['title']}*\n\n*Key Requirements:*\n{key_skills or 'Not specified'}\n\n*Full Details & Apply:*\n{selected_job['link']}"
                        await whatsapp_client.send_whatsapp_message(session.phone_number, job_card)

                        # THE FIX: Always show this message regardless of CV status
                        await whatsapp_client.send_whatsapp_message(session.phone_number, "I can match this job to your CV to boost your application. Reply analyze or pick another listing.")
                    else:
                        await whatsapp_client.send_whatsapp_message(session.phone_number, "That's not a valid number from the list. Please try again.")

                except (ValueError, TypeError):
                    await whatsapp_client.send_whatsapp_message(session.phone_number, "Please reply with a number from the list, or ask me to `analyze this job`.")
        
        # Step 2.5: Handle the confirmation of a saved interest
        elif state.get("awaiting_job_confirm"):
            state.clear()
            if "yes" in message_text and session.job_interest:
                await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.job_interest))
                listings_data = await job_client.fetch_jobs(db, session.job_interest)
                if listings_data:
                    formatted_listings = [f"{i}. {job['title']}" for i, job in enumerate(listings_data, 1)]
                    reply = f"Okay, here are the latest opportunities for *{session.job_interest}*:\n\n" + "\n".join(formatted_listings)
                    reply += "\n\nReply with the number of the job you'd like to view."
                    state["awaiting_job_selection"] = True
                    state["last_job_search_results"] = listings_data
                else:
                    reply = text_responses.get_empathetic_response("no_jobs_found", interest=session.job_interest)
                    session.current_menu = "main"
                    reply += "\n\nWhat would you like to do, find a job, build a CV, or practice for an interview? Just let me know!"
                await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            else:
                state["awaiting_job_role"] = True
                reply = "No problem. What new job role are you looking for?"
                await whatsapp_client.send_whatsapp_message(session.phone_number, reply)

        # Step 2: Handle the user providing a job role to search for
        elif state.get("awaiting_job_role"):
            session.job_interest = message_text_original
            await whatsapp_client.send_whatsapp_message(session.phone_number, text_responses.get_empathetic_response("searching", interest=session.job_interest))
            listings_data = await job_client.fetch_jobs(db, message_text)
            
            if listings_data:
                formatted_listings = [f"{i}. {job['title']}" for i, job in enumerate(listings_data, 1)]
                reply = f"Good news! I found these opportunities for *{session.job_interest}*:\n\n" + "\n".join(formatted_listings)
                reply += "\n\nReply with the number of the job you'd like to view."
                state.clear()
                state["awaiting_job_selection"] = True
                state["last_job_search_results"] = listings_data
            else:
                reply = text_responses.get_empathetic_response("no_jobs_found", interest=session.job_interest)
                session.current_menu = "main"
                state.clear()
                reply += "\n\nWhat would you like to do, find a job, build a CV, or practice for an interview? Just let me know!"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
            
        # Step 1: Handle the initial entry into the "jobs" flow
        else: 
            state.clear()
            if session.job_interest:
                state["awaiting_job_confirm"] = True
                reply = f"I remember you were interested in *{session.job_interest}* jobs. Shall I search for those again? (yes/no)"
            else:
                state["awaiting_job_role"] = True
                reply = "Sounds good! Which type of job are you interested in?"
            await whatsapp_client.send_whatsapp_message(session.phone_number, reply)
        
        crud.update_session(db, session)
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
                final_reply = f"Here is a link to your downloadable CV document:\n{download_link}\n\nThis link is private and will expire in 24 hours."
            else:
                final_reply = "Sorry, I had a little trouble creating the downloadable file. I've sent you the plain text version for now."
                if session.resume_data:
                    cv_text = resume_builder.format_cv(session.resume_data)
                    await whatsapp_client.send_whatsapp_message(session.phone_number, cv_text)
            
            await whatsapp_client.send_whatsapp_message(session.phone_number, final_reply)
            
            # THE FIX: Handle post-CV creation hooks
            if state.get("post_cv_creation_hook") == "analyze_job":
                # User came from job search wanting to analyze a job
                selected_job = state.get("selected_job_for_post_cv")
                state.clear()  # Clear the hook
                
                if selected_job:
                    # Ask if they want to analyze the specific job they were viewing
                    session.current_menu = "jobs"
                    state["awaiting_analysis_confirmation"] = True
                    state["selected_job_for_analysis"] = selected_job
                    await whatsapp_client.send_whatsapp_message(session.phone_number, f"Great! Now that you have a CV, would you like me to analyze it against the *{selected_job['title']}* role you were viewing? (yes/no)")
                elif session.job_interest:
                    # Ask if they want to search for jobs in their saved interest
                    session.current_menu = "jobs"
                    state["awaiting_job_confirm"] = True
                    await whatsapp_client.send_whatsapp_message(session.phone_number, f"Would you like to analyze a job as per your CV? I remember you were interested in *{session.job_interest}* jobs. Shall I search for those again? (yes/no)")
                else:
                    # No specific job or interest, ask what they want to do
                    session.current_menu = "main"
                    await whatsapp_client.send_whatsapp_message(session.phone_number, "Would you like to analyze a job as per your CV?\n\nWhat would you like to do, find a job, build a CV, or practice for an interview? Just let me know!")
            else:
                # Normal CV completion flow
                session.current_menu = "main"
                final_reply += f"\n\n{text_responses.get_conversational_menu_prompt()}"
                await whatsapp_client.send_whatsapp_message(session.phone_number, final_reply)
        else:
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

