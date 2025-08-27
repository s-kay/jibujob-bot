# app/text_responses.py
import random
from typing import List, Optional, Tuple

def get_greeting_parts(user_name: str, is_new_user: bool) -> Tuple[str, Optional[str]]:
    """
    Selects a random, friendly greeting.
    Returns a tuple: (greeting_line, optional_introduction_line).
    The introduction is None for returning users.
    """
    if is_new_user:
        greetings = [
            f"Hi {user_name}, it's great to meet you! I'm KaziLeo, your new career companion.",
            f"Welcome, {user_name}! My name is KaziLeo, and I'm here to help you on your career journey.",
            f"Karibu {user_name}! I'm KaziLeo, your personal guide to jobs and skills in Kenya.",
        ]
        introduction = "I can help you find jobs, learn new skills, connect with mentors, or explore business ideas."
        return (random.choice(greetings), introduction)
    else:
        # For returning users, keep it short and direct.
        greetings = [
            f"Hey {user_name}! Great to see you again.",
            f"Welcome back, {user_name}! Ready to pick up where we left off?",
            f"Karibu tena, {user_name}! Let's find some more opportunities for you.",
        ]
        return (random.choice(greetings), None)

def get_main_menu() -> str:
    """
    Returns the main menu in a more conversational format.
    """
    return (
        "What's our mission for today?\n\n"
        "1️⃣ **Find a new job**\n"
        "2️⃣ **Learn a new skill**\n"
        "3️⃣ **Connect with a mentor**\n"
        "4️⃣ **Explore a business idea**\n"
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
        # --- Generic ---
        "searching": [
            f"Okay, let me check the latest opportunities for {interest_text}. One moment...",
            f"Searching for {interest_text} listings for you now. Hang tight!",
        ],
        "api_error": [
            "Apologies, I'm having a little trouble connecting to our services right now. Could you please try again in a few minutes?",
            "It seems my connection is a bit slow at the moment. Let's give it another try in a bit.",
        ],
        # --- Jobs Specific ---
        "jobs_found": [
            f"Alright, I found a few promising roles for {interest_text}! Here’s what I’ve got:",
            f"Good news! A few opportunities for {interest_text} just came up. Check these out:",
        ],
        "no_jobs_found": [
            f"Hmm, it looks like there aren't any open roles for {interest_text} right now. That's okay! I'll keep an eye out and can alert you when one is posted.",
            f"I couldn't find any current listings for {interest_text}. Don't worry, new roles are added all the time.",
        ],
        # --- Training Specific ---
        "training_found": [
            f"Perfect! I've found some great courses to help you build your skills in {interest_text}. Take a look:",
            f"Excellent choice! Here are some training resources for {interest_text} that could be really helpful:",
        ],
        "no_training_found": [
            f"I couldn't find any specific courses for {interest_text} at the moment, but I'll keep searching and let you know if something comes up!",
            f"It seems my course list for {interest_text} is empty right now. How about we try a broader topic, like 'digital skills'?",
        ],
        # --- Entrepreneurship Specific ---
        "guides_found": [
            f"That's a great field! I've gathered some resources to get you started with {interest_text}:",
            f"Awesome! Exploring {interest_text} is a solid move. Here are some guides that might help:",
        ],
        "no_guides_found": [
            f"I don't have specific guides for {interest_text} just yet, but that's a great topic. I'll research it and add it to my knowledge base!",
            f"My resources on {interest_text} are still growing. Could we explore a related area like 'freelancing' or 'e-commerce'?",
        ],
        # --- Mentorship Specific ---
        "mentors_found": [
            f"Connecting with a mentor is a brilliant idea! Here are some experienced professionals in {interest_text} who are available:",
            f"Great choice! I've found some mentors in {interest_text} who could offer valuable guidance:",
        ],
        "no_mentors_found": [
            f"It seems my list of mentors for {interest_text} is empty right now. This is a new area for me, and I'll work on finding experts to add!",
            f"I couldn't find a mentor for {interest_text} at the moment. Would you be interested in a related field like 'business' or 'tech'?",
        ],
    }
    
    listing_str = "\n\n" + "\n".join(listings) if listings else ""
    
    return random.choice(responses[context]) + listing_str
