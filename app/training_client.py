# app/training_client.py
import asyncio
from typing import List, Optional

# --- High-Quality Mock Database of Real, Relevant Courses ---
# This list is manually curated to provide real value to users in the pilot program.
MOCK_TRAINING_LIST = [
    # Digital Skills & Marketing
    "*Fundamentals of Digital Marketing* by Google - Learn the basics of digital marketing with this free, certified course. https://skillshop.exceedlms.com/student/path/6943-fundamentals-of-digital-marketing",
    "*Social Media Marketing Course* by HubSpot Academy - A free, comprehensive course on social media strategy. https://academy.hubspot.com/courses/social-media",
    "*Introduction to Graphic Design* by Great Learning - A free beginner's course to learn the fundamentals of graphic design. https://www.mygreatlearning.com/academy/learn-for-free/courses/graphic-design-basics",
    
    # Ajira Digital (Official Kenyan Government Program)
    "*Ajira Digital Training Program* - Get skills in content writing, transcription, and data entry for online work. https://ajiradigital.go.ke/#/training",

    # Soft Skills
    "*Introduction to Public Speaking* by University of Washington - A highly-rated free course on Coursera. https://www.coursera.org/learn/public-speaking",
    "*Sales and Negotiations Skills* - A free short course on Alison.com covering key business skills. https://alison.com/course/sales-and-negotiations-skills",
    
    # Financial Literacy
    "*Personal Finance & Credit* - A free introductory course on Alison.com. https://alison.com/course/an-introductory-course-on-personal-finance-and-credit",
    "*Managing Your M-Pesa Business* - A practical guide on using M-Pesa for business (YouTube Series). https://www.youtube.com/watch?v=examplelink1",
    
    # Tech Skills
    "*Introduction to Web Development* - A free course covering HTML, CSS, and JavaScript. https://www.freecodecamp.org/learn/responsive-web-design/",
    "*Python for Everybody* by University of Michigan - A very popular free course for learning Python. https://www.coursera.org/specializations/python",
]

async def fetch_trainings(keyword: str) -> Optional[List[str]]:
    """
    Simulates fetching training courses based on a keyword search.
    In the future, this could be an API call to a real course provider.
    """
    await asyncio.sleep(1) # Simulate network latency
    
    try:
        # A simple keyword search logic
        keyword = keyword.lower()
        results = [
            course for course in MOCK_TRAINING_LIST 
            if keyword in course.lower()
        ]
        return results if results else []
    except Exception as e:
        print(f"Error fetching training data: {e}")
        return None

