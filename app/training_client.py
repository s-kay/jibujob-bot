# app/training_client.py
import logging
from typing import List, Optional

# --- Uncategorized Mock Training Database ---
# This is now a single list, allowing for more flexible keyword searching.
MOCK_TRAININGS_LIST = [
    # Digital Skills
    "*FREE Digital Marketing & E-Commerce Training/Work Readiness/Mentorship* - https://ajiradigital.go.ke/#/activity/mombasa-kwashee-ayec-digital-marketing-e-commerce-training-mentorship-cohort-1-september-2025/TRAINING",
    "*FREE Digital Marketing and E-Commerce Training / Work Readiness / Mentorship* -  https://ajiradigital.go.ke/#/activity/nyandarua-destiny-sanctuary-digital-marketing-training-mentorship-29th-1st-september-2025/TRAINING",
    "*FREE online work readiness training and mentorship at Mukuru Slums Development Project*  - https://ajiradigital.go.ke/#/activity/nairobi-mukuru-slums-dev-project-digital-marketing-ecommerce-training-mentorship-9th-10th-s/TRAINING",
    "*FREE Data Analysis using Excel Training/Mentorship* - https://ajiradigital.go.ke/#/activity/monday-1st-september-zoom-data-analysis-using-excel-training-mentorship/TRAINING?t=U2FsdGVkX193A7kp8R5MeJ1W2l6pz1WVZGtniATW2s24Llnc2ikwW0iHmLoN4Nzd7YZc60vI4fhiqBbDKh4qnpntIMwNNt%2BbU07%2FKsemdej4De5QDlJ1TatxnpudFD04xt7BkukZqXa6L0zkbSWzSSWM3I%2FdKOXvNFcWCt2qbP7ymROjdGSeaWlTxvDYMgV0",
    "*FREE online work readiness training and mentorship at KIHBT Ngong*  - https://ajiradigital.go.ke/#/activity/kajiado-kihbt-ngong-digital-marketing-ecommerce-training-mentorship-4th-5th-sept-2025/TRAINING",


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
