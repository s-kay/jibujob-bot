# app/entrepreneurship_client.py
import logging
from typing import List, Optional

# --- Uncategorized Mock Entrepreneurship Database ---
# This is now a single list, allowing for more flexible keyword searching.
MOCK_ENTREPRENEURSHIPS_LIST = [
    # Agribusiness
    "*Starter Guide: Modern Poultry Farming in Kenya*",
    "*Resource: Accessing Youth Enterprise Development Fund for Agribusiness*",
    "*Case Study: Successful Small-Scale Hydroponics*",

    # E-commerce
    "*How to Start a Dropshipping Business with Shopify*",
    "*Selling on Jumia & Jiji: A Beginner's Guide*",
    "*Using M-Pesa for Your Online Store*",

    # Freelancing
    "*Finding Your First Client on Upwork*",
    "*Guide to Pricing Your Freelance Services*",
    "*Managing Your Finances as a Freelancer in Kenya*",

    # Crafts
    "*Turning Your Craft into a Business* (YouTube Series)",
    "*Etsy for Beginners: Selling Handmade Goods*",
    "*Sourcing Materials for Crafts in Nairobi*",
]

async def fetch_entrepreneurship_guides(topic: str) -> Optional[List[str]]:
    """
    Fetches entrepreneurship guides by performing a keyword search on the mock database.
    """
    logging.info(f"Fetching mock entrepreneurship guides for keyword: '{topic}'")
    
    search_term = topic.lower()
    
    # Find all guides in the list that contain the search term
    found_guides = [guide for guide in MOCK_ENTREPRENEURSHIPS_LIST if search_term in guide.lower()]
    
    if not found_guides:
        logging.warning(f"No mock entrepreneurship guides found for keyword '{topic}'")
        return []
        
    return found_guides
