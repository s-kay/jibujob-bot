from app import models

def handle_feedback_conversation(session: models.UserSession, message: str) -> tuple[str, dict | None, bool]:
    """
    Manages the multi-step conversation for collecting user feedback.
    Returns the reply, the collected data (at the end), and a completion flag.
    """
    state = session.session_data
    step = state.get("feedback_step", 0)
    
    # Use the correct keys that match the database model and crud function
    feedback_data = state.get("feedback_data", {
        "likes": None,
        "dislikes": None,
        "suggestions": None,
        "rating": None
    })

    if step == 0:
        state["feedback_step"] = 1
        state["feedback_data"] = feedback_data
        return "Karibu! We value your feedback. To start, what do you like most about KaziLeo so far?", None, False
    
    elif step == 1:
        feedback_data["likes"] = message
        state["feedback_step"] = 2
        return "Got it. Now, what has been the most confusing or difficult part of using the bot?", None, False
        
    elif step == 2:
        feedback_data["dislikes"] = message
        state["feedback_step"] = 3
        return "Thanks for that. Do you have any suggestions for new features or improvements?", None, False
        
    elif step == 3:
        feedback_data["suggestions"] = message
        state["feedback_step"] = 4
        return "Almost done! Finally, on a scale of 1 to 5 (where 5 is best), how would you rate your experience?", None, False
        
    elif step == 4:
        rating = None
        try:
            rating_num = int(message.strip())
            if 1 <= rating_num <= 5:
                rating = rating_num
        except (ValueError, TypeError):
            pass # Keep rating as None if it's not a valid number
        
        feedback_data["rating"] = rating
        
        summary = format_feedback_summary(feedback_data)
        reply = f"{summary}\n\nThank you so much for your feedback! It will help us make KaziLeo better for everyone."
        
        # We don't clear the state here. We return the final data to be saved.
        return reply, feedback_data, True

    return "Sorry, something went wrong with the feedback process.", None, True

def format_feedback_summary(feedback_data: dict) -> str:
    """Formats the collected feedback into a user-friendly summary."""
    summary = " Asante! 🙏 Here's a summary of your feedback:\n\n"
    if feedback_data.get("likes"):
        summary += f"✅ *What you liked:*\n{feedback_data['likes']}\n\n"
    if feedback_data.get("dislikes"):
        summary += f"🤔 *What was confusing:*\n{feedback_data['dislikes']}\n\n"
    if feedback_data.get("suggestions"):
        summary += f"💡 *Your suggestions:*\n{feedback_data['suggestions']}\n\n"
    if feedback_data.get("rating"):
        summary += f"⭐ *Your rating:*\n{feedback_data['rating']} out of 5"
    return summary.strip()

