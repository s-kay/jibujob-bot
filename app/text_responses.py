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
        # For returning users, keep it short and direct.
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
    Returns the main menu in a more conversational format.
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
        # ... (rest of the responses remain the same)
    }
    
    listing_str = "\n\n" + "\n".join(listings) if listings else ""
    
    # Check if the context exists, otherwise return a default message
    if context in responses:
        return random.choice(responses[context]) + listing_str
    return "Here is the information I found for you:" + listing_str
