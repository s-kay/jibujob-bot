# app/training_client.py
import logging
from typing import List, Optional

# --- Enhanced Mock Training Database ---
# This acts as our stand-in for a live API for now.
MOCK_TRAININGS = {
    "digital skills": [
        "Free Course: Intro to Digital Marketing (Google)",
        "Learn Advanced Excel for Business (Coursera)",
        "Social Media Management 101 (ALX)",
    ],
    "ai": [
        "Introduction to AI Prompt Engineering (Free)",
        "AI for Everyone by Andrew Ng (Coursera)",
        "Generative AI Fundamentals (Google Cloud Skills)",
    ],
    "agribusiness": [
        "Modern Poultry Farming Techniques (Local NGO)",
        "Guide to Sustainable Farming (Online Course)",
        "Agribusiness Management Essentials (Strathmore)",
    ],
    "crafts": [
        "Turning Your Craft into a Business (YouTube Series)",
        "Etsy for Beginners: Selling Handmade Goods",
        "Basic Bookkeeping for Creatives",
    ],
}

async def fetch_trainings(skill_title: str) -> Optional[List[str]]:
    """
    Fetches training listings. 
    Currently uses an internal mock database.
    This function is ready to be swapped with a live API call in the future.
    """
    logging.info(f"Fetching mock trainings for query: '{skill_title}'")
    
    # Simple search logic: find the best matching key in our mock database
    best_match_key = None
    for key in MOCK_TRAININGS:
        if key in skill_title.lower():
            best_match_key = key
            break
            
    if best_match_key:
        return MOCK_TRAININGS[best_match_key]
    
    # If no direct match, return an empty list
    logging.warning(f"No mock training category found for '{skill_title}'")
    return []
