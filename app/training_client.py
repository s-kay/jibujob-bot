# app/training_client.py
import logging
from typing import List, Optional

# --- Uncategorized Mock Training Database ---
# This is now a single list, allowing for more flexible keyword searching.
MOCK_TRAININGS_LIST = [
    # Digital Skills
    "*Free Course: Intro to Digital Marketing* (Google)",
    "*Learn Advanced Excel for Business* (Coursera)",
    "*Social Media Management 101* (ALX)",
    "*Graphic Design Basics with Canva* (YouTube)",
    
    # AI
    "*Introduction to AI Prompt Engineering* (Free)",
    "*AI for Everyone* by Andrew Ng (Coursera)",
    "*Generative AI Fundamentals* (Google Cloud Skills)",
    "*Basics of Machine Learning* (Udacity)",
    
    # Agribusiness
    "*Modern Poultry Farming Techniques* (Local NGO)",
    "*Guide to Sustainable Farming* (Online Course)",
    "*Agribusiness Management Essentials* (Strathmore)",
    "*Introduction to Hydroponics* (YouTube)",
    
    # Crafts & Business
    "*Turning Your Craft into a Business* (YouTube Series)",
    "*Etsy for Beginners: Selling Handmade Goods*",
    "*Basic Bookkeeping for Creatives*",
    "*Photography for Your Handmade Products*",

    # Sales
    "*The Art of Sales: Mastering the Selling Process* (Coursera)",
    "*Customer Service Excellence* (Alison)",
    "*Negotiation Skills for Sales Professionals*",
]

async def fetch_trainings(skill_title: str) -> Optional[List[str]]:
    """
    Fetches training listings by performing a keyword search on the mock database.
    """
    logging.info(f"Fetching mock trainings for keyword: '{skill_title}'")
    
    search_term = skill_title.lower()
    
    # Find all trainings in the list that contain the search term
    found_trainings = [training for training in MOCK_TRAININGS_LIST if search_term in training.lower()]
    
    if not found_trainings:
        logging.warning(f"No mock trainings found for keyword '{skill_title}'")
        return []
        
    return found_trainings
