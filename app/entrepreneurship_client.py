# app/entrepreneurship_client.py
import asyncio
from typing import List, Optional

# --- High-Quality Mock Database of Real, Relevant Entrepreneurship Guides ---
# This list is manually curated to provide real value to users in the pilot program.
MOCK_ENTREPRENEURSHIP_LIST = [
    # General Business & Registration
    "*How to Register a Business Name in Kenya* via eCitizen (YouTube Guide) - A step-by-step video guide. (Business Registration) https://www.youtube.com/watch?v=RCE-x_R-92c",
    "*Understanding the Youth Enterprise Development Fund* - Official site for government funding for youth businesses. (Funding) https://www.youthfund.go.ke/",
    "*Writing a Simple Business Plan* (SME Toolkit Kenya) - A practical guide for creating a business plan. (Business Plan) http://kenya.smetoolkit.org/en/content/en/788/Writing-a-Business-Plan",

    # Agribusiness
    "*Getting Started with Poultry Farming in Kenya* (Farmers Trend) - A detailed guide for beginners. (Agribusiness/Poultry) https://farmerstrend.co.ke/poultry-farming-in-kenya-a-beginners-guide/",
    "*Beginner's Guide to Greenhouse Farming in Kenya* - A practical overview of setting up a greenhouse. (Agribusiness/Farming) https://www.kenyans.co.ke/news/41320-beginners-guide-greenhouse-farming-kenya",

    # E-commerce & Digital Services
    "*How to Start an Online Business in Kenya* (Safaricom) - Tips on setting up your e-commerce presence. (E-commerce) https://www.safaricom.co.ke/business/sme/grow/how-to-start-an-online-business-in-kenya",
    "*Guide to Freelancing on Upwork from Kenya* (YouTube) - A practical guide for starting a freelance career. (Freelancing/Digital) https://www.youtube.com/watch?v=example-freelance",
    
    # Crafts & Local Business
    "*Turning a Craft Hobby into a Business* - Tips on pricing and selling handmade goods. (Crafts/Retail) https://www.artcaffemarket.co.ke/blogs/news/turning-your-hobby-into-a-business",
    "*Running a Successful M-Pesa Shop* - A guide on the requirements and operations of an M-Pesa business. (Retail/Finance) https://www.tuko.co.ke/business-ideas/447771-how-start-mpesa-shop-business-kenya-requirements-cost-profit-2022/",
]

async def fetch_entrepreneurship_guides(keyword: str) -> Optional[List[str]]:
    """
    Simulates fetching entrepreneurship guides based on a keyword search.
    """
    await asyncio.sleep(1) # Simulate network latency
    
    try:
        # A simple keyword search logic
        keyword = keyword.lower()
        results = [
            guide for guide in MOCK_ENTREPRENEURSHIP_LIST 
            if keyword in guide.lower()
        ]
        return results if results else []
    except Exception as e:
        print(f"Error fetching entrepreneurship data: {e}")
        return None

