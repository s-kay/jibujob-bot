# app/feedback_handler.py
from typing import Tuple, Dict, Any, Optional
from . import models

# --- The sequence of questions for the feedback flow ---
FEEDBACK_QUESTIONS = [
    {
        "key": "what_liked",
        "question": "Thank you for helping us improve KaziLeo! 🙏\n\nFirst, what do you like most about the bot so far?"
    },
    {
        "key": "what_confusing",
        "question": "Great, thanks! Now, what has been the most confusing or difficult part of using the bot?"
    },
    {
        "key": "feature_requests",
        "question": "That's very helpful. Is there anything you wish KaziLeo could do that it doesn't do yet?"
    },
    {
        "key": "rating",
        "question": "Finally, on a scale of 1 to 5 (where 5 is 'very helpful'), how would you rate your experience with KaziLeo so far?"
    }
]

def handle_feedback_conversation(
    session: models.UserSession, 
    message_text: str
) -> Tuple[str, Optional[Dict[str, Any]], bool]:
    """
    Manages the conversation flow for collecting user feedback.
    Returns the bot's reply, the collected feedback data, and a completion flag.
    """
    state = session.session_data
    feedback_data = state.get("feedback_data", {})

    current_step = state.get("feedback_step", 0)

    # If this is not the first step, save the user's previous answer
    if current_step > 0:
        prev_question_key = FEEDBACK_QUESTIONS[current_step - 1]["key"]
        
        # Validate rating input
        if prev_question_key == "rating":
            try:
                rating = int(message_text)
                if 1 <= rating <= 5:
                    feedback_data[prev_question_key] = rating
                else:
                    return ("Please enter a number between 1 and 5.", None, False)
            except ValueError:
                return ("That doesn't seem to be a valid number. Please enter a number from 1 to 5.", None, False)
        else:
            feedback_data[prev_question_key] = message_text

    # Check if we have more questions to ask
    if current_step < len(FEEDBACK_QUESTIONS):
        next_question = FEEDBACK_QUESTIONS[current_step]["question"]
        state["feedback_step"] = current_step + 1
        state["feedback_data"] = feedback_data
        return (next_question, None, False)
    else:
        # If we've asked all questions, the flow is complete
        final_reply = "Thank you so much! Your feedback is incredibly valuable and will help us make KaziLeo better for everyone. 🙏"
        state.pop("feedback_step", None)
        state.pop("feedback_data", None)
        return (final_reply, feedback_data, True)

def format_feedback_summary(feedback_data: Dict[str, Any]) -> str:
    """Formats the collected feedback into a clean, human-readable string for logging or review."""
    summary_parts = ["--- New User Feedback ---"]
    
    rating = feedback_data.get("rating")
    if rating:
        summary_parts.append(f"Rating: {rating}/5")
        
    liked = feedback_data.get("what_liked")
    if liked:
        summary_parts.append(f"\nWhat they liked:\n- {liked}")
        
    confusing = feedback_data.get("what_confusing")
    if confusing:
        summary_parts.append(f"\nWhat was confusing:\n- {confusing}")
        
    requests = feedback_data.get("feature_requests")
    if requests:
        summary_parts.append(f"\nFeature requests:\n- {requests}")
        
    summary_parts.append("\n-------------------------")
    
    return "\n".join(summary_parts)

