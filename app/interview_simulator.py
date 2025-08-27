# app/interview_simulator.py
from typing import Tuple, List, Optional
from . import models
import random

# --- Mock Interview Question Database ---
INTERVIEW_QUESTIONS = {
    "general": [
        "Tell me about yourself.",
        "What are your biggest strengths?",
        "What is your biggest weakness?",
        "Where do you see yourself in 5 years?",
        "Why do you want to work for this company?",
    ],
    "accountant": [
        "Can you describe your experience with financial reporting software like QuickBooks or SAP?",
        "How do you ensure accuracy and attention to detail in your work?",
        "Tell me about a time you identified a significant cost-saving opportunity.",
    ],
    "sales": [
        "How do you handle rejection from a potential customer?",
        "Describe your process for qualifying a new lead.",
        "Tell me about your most successful sale and what made it a success.",
    ],
    "software developer": [
        "Can you describe a challenging technical problem you solved on a recent project?",
        "How do you stay up-to-date with new technologies and programming languages?",
        "Explain a complex project you worked on in simple terms.",
    ],
}

def get_questions_for_role(role: str) -> List[str]:
    """Selects relevant questions for a given role, including general questions."""
    role_key = role.lower()
    questions = list(INTERVIEW_QUESTIONS.get("general", [])) # Start with a copy of general questions
    
    # Find the best matching role-specific questions
    best_match_key = None
    for key in INTERVIEW_QUESTIONS:
        if key in role_key:
            best_match_key = key
            break
    
    if best_match_key:
        questions.extend(INTERVIEW_QUESTIONS[best_match_key])
        
    random.shuffle(questions)
    return questions[:5] # Return a random set of 5 questions

def format_feedback(interview_data: dict) -> str:
    """Formats the collected answers into a summary for the user."""
    feedback = "*--- Your Interview Practice Summary ---*\n\n"
    answers = interview_data.get("answers", {})
    
    for question, answer in answers.items():
        feedback += f"*Question:* {question}\n"
        feedback += f"*Your Answer:* {answer}\n\n"
        
    feedback += "*--------------------*\n"
    feedback += "Well done! Reviewing your answers is a great way to prepare."
    return feedback.strip()

def handle_interview_conversation(session: models.UserSession, message_text: str) -> Tuple[str, bool]:
    """
    Manages the interview simulation conversation.
    Returns the reply message and a boolean indicating if the flow is complete.
    """
    interview_data = session.interview_data
    state = session.session_data

    # --- Start of the flow: Get the job role ---
    if not interview_data.get("questions"):
        role = message_text
        questions = get_questions_for_role(role)
        interview_data["role"] = role
        interview_data["questions"] = questions
        interview_data["answers"] = {}
        interview_data["current_question_index"] = 0
        
        first_question = questions[0]
        state["awaiting_interview_answer"] = True
        return f"Great! Let's practice for a *{role}* interview. We'll go through 5 questions.\n\nHere's your first one:\n\n_{first_question}_", False

    # --- During the flow: Process an answer and ask the next question ---
    if state.get("awaiting_interview_answer"):
        current_index = interview_data.get("current_question_index", 0)
        questions = interview_data.get("questions", [])
        
        # Save the user's answer to the previous question
        previous_question = questions[current_index]
        interview_data["answers"][previous_question] = message_text
        
        # Move to the next question
        next_index = current_index + 1
        interview_data["current_question_index"] = next_index
        
        if next_index < len(questions):
            next_question = questions[next_index]
            return f"Good answer. Here is question {next_index + 1} of {len(questions)}:\n\n_{next_question}_", False
        else:
            # All questions have been answered
            state.pop("awaiting_interview_answer", None)
            feedback = format_feedback(interview_data)
            return feedback, True
    
    # Fallback in case state is broken
    return "Something went wrong with the simulation. Let's start over.", True
