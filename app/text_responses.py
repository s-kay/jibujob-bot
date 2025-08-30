# app/text_responses.py
import random
from typing import List, Optional, Tuple

def get_greeting_parts(user_name: str, is_new_user: bool) -> Tuple[str, Optional[str]]:
    """
    Selects a random, friendly greeting based on whether the user is new or returning.
    Now includes Swahili/Sheng options.
    """
    if is_new_user:
        greetings = [
            f"Hi {user_name}, it's great to meet you! I'm KaziLeo, your new career companion.",
            f"Sasa {user_name}! It's great to meet you. My name is KaziLeo, and I'm here to help you on your career journey.",
            f"Karibu {user_name}! I'm KaziLeo, your personal guide to jobs and skills in Kenya.",
        ]
        introduction = "I can help you find jobs (kazi), learn new skills (mafunzo), connect with mentors (ushauri), or explore business ideas (biashara)."
        return (random.choice(greetings), introduction)
    else:
        greetings = [
            f"Hey {user_name}! Great to see you again.",
            f"Welcome back, {user_name}! Ready to pick up where we left off?",
            f"Karibu tena, {user_name}! Let's find some more opportunities for you.",
            f"Niaje {user_name}! Good to see you again.",
        ]
        return (random.choice(greetings), None)

def get_sheng_greeting_response() -> str:
    """Returns a random, friendly Sheng response to a greeting."""
    return random.choice(["Poa!", "Fiti sana!", "Poa poa."])

def get_main_menu() -> str:
    """
    Returns the main menu in a more conversational format with Swahili hints.
    """
    return (
        "What's our mission for today?\n\n"
        "1️⃣ **Find a new job** (Tafuta Kazi)\n"
        "2️⃣ **Learn a new skill** (Jifunze Ujuzi)\n"
        "3️⃣ **Connect with a mentor** (Pata Ushauri)\n"
        "4️⃣ **Explore a business idea** (Anzisha Biashara)\n"
        "5️⃣ **Build a simple CV**\n"
        "6️⃣ **AI Interview Practice**\n"
        "7️⃣ **Generate a Cover Letter**\n"
        "8️⃣ **Optimize My CV for a Job**\n"
        "9️⃣ **Analyze Job Skills**\n\n"
        "Just reply with the number of your choice, or type '0' to reset."
    )

def get_empathetic_response(context: str, listings: List[str] = [], interest: Optional[str] = None) -> str:
    """
    Provides context-aware, empathetic responses.
    """
    interest_text = f"*{interest}*" if interest else "your topic"

    responses = {
        "searching": [ f"Okay, let me check the latest opportunities for {interest_text}. One moment..." ],
        "api_error": [ "Apologies, I'm having a little trouble connecting to our services right now. Could you please try again in a few minutes?" ],
        "jobs_found": [ f"Alright, I found a few promising roles for {interest_text}! Here’s what I’ve got:" ],
        "no_jobs_found": [ f"Hmm, it looks like there aren't any open roles for {interest_text} right now. That's okay! I'll keep an eye out and can alert you when one is posted." ],
        "training_found": [ f"Perfect! I've found some great courses to help you build your skills in {interest_text}. Take a look:" ],
        "no_training_found": [ f"I couldn't find any specific courses for {interest_text} at the moment, but I'll keep searching and let you know if something comes up!" ],
        "guides_found": [ f"That's a great field! I've gathered some resources to get you started with {interest_text}:" ],
        "no_guides_found": [ f"I don't have specific guides for {interest_text} just yet, but that's a great topic. I'll research it and add it to my knowledge base!" ],
        "mentors_found": [ f"Connecting with a mentor is a brilliant idea! Here are some experienced professionals in {interest_text} who are available:" ],
        "no_mentors_found": [ f"It seems my list of mentors for {interest_text} is empty right now. I'll work on finding experts to add!" ],
        "interest_saved_and_jobs_found": [ f"Great! I've saved your interest in {interest_text}.\n\nHere are the first results I found for you:" ],
        "interest_saved_and_training_found": [ f"Great! I've saved your interest in {interest_text}.\n\nHere are the first courses:" ],
        "interest_saved_and_mentors_found": [ f"Perfect! I've saved your interest in {interest_text}.\n\nHere are some available mentors:" ],
        "interest_saved_and_guides_found": [ f"Excellent! I've saved your interest in {interest_text}.\n\nHere are the first guides:" ],
    }
    
    listing_str = "\n\n" + "\n".join(listings) if listings else ""
    
    return random.choice(responses.get(context, ["Here is the information I found for you:"])) + listing_str
