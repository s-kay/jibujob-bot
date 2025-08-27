# app/entrepreneurship_client.py
import logging
from typing import List, Optional

# --- Enhanced Mock Entrepreneurship Database ---
MOCK_ENTREPRENEURSHIPS = {
    "agribusiness": [
        "Starter Guide: Modern Poultry Farming in Kenya",
        "Resource: Accessing Youth Enterprise Development Fund for Agribusiness",
        "Case Study: Successful Small-Scale Hydroponics",
    ],
    "e-commerce": [
        "How to Start a Dropshipping Business with Shopify",
        "Selling on Jumia & Jiji: A Beginner's Guide",
        "Using M-Pesa for Your Online Store",
    ],
    "freelancing": [
        "Finding Your First Client on Upwork",
        "Guide to Pricing Your Freelance Services",
        "Managing Your Finances as a Freelancer in Kenya",
    ],
    "crafts": [
        "Turning Your Craft into a Business (YouTube Series)",
        "Etsy for Beginners: Selling Handmade Goods",
        "Sourcing Materials for Crafts in Nairobi",
    ],
}

async def fetch_entrepreneurship_guides(topic: str) -> Optional[List[str]]:
    """
    Fetches entrepreneurship guides.
    Currently uses an internal mock database.
    """
    logging.info(f"Fetching mock entrepreneurship guides for query: '{topic}'")
    
    best_match_key = None
    for key in MOCK_ENTREPRENEURSHIPS:
        if key in topic.lower():
            best_match_key = key
            break
            
    if best_match_key:
        return MOCK_ENTREPRENEURSHIPS[best_match_key]
    
    logging.warning(f"No mock entrepreneurship category found for '{topic}'")
    return []
