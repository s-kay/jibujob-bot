# app/text_responses.py
import random
from typing import Optional

#  privacy policy URL 
PRIVACY_POLICY_URL = "https://gist.github.com/s-kay/1b779e2db46be1521dbb34251dd2fdf2/raw/74d52102aaf9528cf21176c1e2a5f2f4fecf0955/kazileo_privacy_policy.md"

def get_sheng_greeting_response() -> str:
    """Returns a random, friendly Sheng response to a greeting."""
    responses = ["Poa!", "Fiti sana!", "Sema Kazi!"]
    return random.choice(responses)

def get_greeting_parts(user_name: str, is_new_user: bool, greeting_word: str) -> tuple[str, str | None, str]:
    """
    Selects a random, friendly greeting based on whether the user is new or returning.
    Now includes Swahili/Sheng options.
    """
    if is_new_user:
        greetings = [
            f"Hi {user_name}, 👋🏾 Welcome to KaziLeo! I'm Riziki, ",
            f"Sasa {user_name}! 👋🏾 Welcome to KaziLeo! My name is Riziki, ",
            f"Karibu {user_name}! 👋🏾 Welcome to KaziLeo! I'm Riziki, ",
        ]
        introduction = ("I'm your AI companion, here to help you find jobs (kazi), learn new skills (mafunzo), connect with mentors (ushauri), or explore business ideas (biashara).\n\n" f"By using KaziLeo, you agree to our Privacy Policy: {PRIVACY_POLICY_URL}"
        )

        # A more detailed prompt for new users to help them discover features.
        prompt = "To get started, just tell me what you need. For example, you can say:\n\n• \"Tafuta kazi\"\n• \"Nionyeshe training\"\n• \"Tengeneza CV\""

        return random.choice(greetings), introduction, prompt
    else:
        # Returning user gets a shorter, more direct interaction.
        options = [
            f"Hey {user_name}! 👋🏾 Great to see you again.",
            f"😃 Welcome back,{user_name}! Ready to pick up where we left off?",
            f"👏🏾 Karibu tena, {user_name}! Let's find some more opportunities for you.",
            f"👋🏾 Niaje {user_name}! Nimefurahi tumekutana tena.",
        ]
        if greeting_word in ["niaje", "sasa", "vipi", "habari", "mambo"]:
            greeting = get_sheng_greeting_response()
        else:
            greeting = random.choice(options)

        # The conversational menu prompt for returning users.
        prompt = get_conversational_menu_prompt()
        
        return greeting, None, prompt

def get_conversational_menu_prompt() -> str:
    """Returns the open-ended conversational prompt for the menu."""
    return "What would you like to do, find a job, build a CV, or practice for an interview? Just let me know!"

# --- NEW FUNCTION FOR CV EDITOR DIALOGUE ---
def get_cv_editor_responses(key: str, **kwargs) -> str:
    """
    Returns all dialogue for the CV creation and editing flows.
    """
    section_name = kwargs.get("section_name", "that section")
    current_data = kwargs.get("current_data", "")
    prompt = kwargs.get("prompt", "")

    responses = {
        "confirm_edit_existing": "It looks like you already have a CV with me. Would you like to edit it? (yes/no)",
        "show_section_and_prompt": f"Okay, here's what I currently have for *{section_name}*:\n_{current_data}_\n\n{prompt}",
        "invalid_editor_choice": "Sorry, I didn't get that. What section of your CV would you like to edit? You can reply with a number (1-5) for summary, experience, etc.",
        "confirm_section_update": f"✅ Perfect, I've updated your *{section_name}*.\n\nWould you like to edit another section? (yes/no)",
        "final_update_confirmation": "Great! Your CV has been updated.",
        "cv_complete": "✅ Your CV is complete!",
    }
    return responses.get(key, "Sorry, an error occurred in the CV builder.")

def get_empathetic_response(key: str, **kwargs) -> str:
    """
    Returns a context-specific, empathetic response.
    """
    listings = kwargs.get("listings", [])
    interest = kwargs.get("interest", "that topic")
    
    # Format lists with bullet points for readability
    formatted_listings = "\n".join(f"• {item}" for item in listings) if listings else ""
    interest_text = f"*{interest}*" if interest else "your topic"

    responses = {
        "searching": [ f"Okay, let me check the latest opportunities for {interest_text}. One moment...", f"Searching for *{interest}* listings for you now. Hang tight!",
            f"Let's see what we can find for *{interest}*...\n{formatted_listings}" ],
        "api_error": [ "Apologies, I'm having a little trouble connecting to our services right now. Could you please try again in a few minutes?" ],
        "jobs_found": [ f"Alright, I found a few promising roles for {interest_text}! Here’s what I’ve got:\n{formatted_listings}" ],
        "no_jobs_found": [ f"Hmm, it looks like there aren't any open roles for {interest_text} right now. That's okay! I'll keep an eye out and can alert you when one is posted." ],
        "training_found": [ f"Perfect! I've found some great courses to help you build your skills in {interest_text}. Take a look:\n{formatted_listings}" ],
        "no_training_found": [ f"I couldn't find any specific courses for {interest_text} at the moment, but I'll keep searching and let you know if something comes up!" ],
        "guides_found": [ f"That's a great field! I've gathered some resources to get you started with {interest_text}:\n{formatted_listings}" ],
        "no_guides_found": [ f"I don't have specific guides for {interest_text} just yet, but that's a great topic. I'll research it and add it to my knowledge base!" ],
        "mentors_found": [ f"Connecting with a mentor is a brilliant idea! Here are some experienced professionals in {interest_text} who are available:\n{formatted_listings}" ],
        "no_mentors_found": [ f"It seems my list of mentors for {interest_text} is empty right now. I'll work on finding experts to add!" ],
        "interest_saved_and_jobs_found": [ f"Great! I've saved your interest in {interest_text}.\n\nGood news! A few opportunities just came up. Check these out:\n{formatted_listings}" ],
        "interest_saved_and_training_found": [ f"Great! I've saved your interest in {interest_text}.\n\nHere are the first courses:\n{formatted_listings}" ],
        "interest_saved_and_mentors_found": [ f"Perfect! I've saved your interest in {interest_text}.\n\nHere are some available mentors:\n{formatted_listings}" ],
        "interest_saved_and_guides_found": [ f"Excellent! I've saved your interest in {interest_text}.\n\nHere are the first guides:\n{formatted_listings}" ],
    }

    return random.choice(responses.get(key, ["Sorry, I'm not sure how to respond to that."]))