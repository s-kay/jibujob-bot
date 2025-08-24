import os
import logging
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ==============================
# Config & Setup
# ==============================
app = FastAPI()

# Configuration
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "jibujob-verify")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v22.0")

# Fail fast if critical ENV vars are missing
if not WHATSAPP_TOKEN:
    raise RuntimeError("❌ Missing WHATSAPP_TOKEN in environment.")
if not WHATSAPP_PHONE_ID:
    raise RuntimeError("❌ Missing WHATSAPP_PHONE_ID in environment.")



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def format_main_menu(user_name: str) -> str:
    """Return the main menu message with personalized greeting."""
    return (
        f"Hi {user_name}! 👋\n\n"
        "👋 Welcome to JibuJob Career Bot!\n"
        "Please choose an option:\n\n"
        "1️⃣ Job Listings\n"
        "2️⃣ Training Modules\n"
        "3️⃣ Mentorship\n"
        "4️⃣ Micro-entrepreneurship\n"
        "0️⃣ Exit"
    )

def handle_menu_choice(choice: str, user_name: str) -> str:
    """Handle user menu choice."""
    if choice == "1":
        return "💼 Here are the latest *Job Listings*:\n\n- Software Engineer\n- Data Analyst\n- Sales Associate\n\nReply 0️⃣ to return to the main menu."
    elif choice == "2":
        return "📚 Choose a *Training Module*:\n\n1. Beginner\n2. Intermediate\n3. Advanced\n\nReply 0️⃣ to return to the main menu."
    elif choice == "3":
        return "🤝 *Mentorship* options:\n\n- Tech Career Guidance\n- Business Startups\n- Leadership Coaching\n\nReply 0️⃣ to return to the main menu."
    elif choice == "4":
        return "🚀 *Micro-entrepreneurship* opportunities:\n\n- Digital Marketing\n- Agribusiness\n- E-commerce\n\nReply 0️⃣ to return to the main menu."
    elif choice == "0":
        return "👋 Thank you for using JibuJob Career Bot. Goodbye!"
    else:
        return "❌ Invalid option. Please try again.\n\n" + format_main_menu(user_name)

# -------------------------------------------------
# WhatsApp Webhook Verification
# -------------------------------------------------
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return JSONResponse(content=int(params.get("hub.challenge", 0)), status_code=200)
    return JSONResponse(content="Invalid verification token", status_code=403)

# -------------------------------------------------
# WhatsApp Message Receiver
# -------------------------------------------------
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    logger.info(f"Incoming webhook: {data}")

    try:
        # Extract user info
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            msg = messages[0]
            user_name = msg.get("profile", {}).get("name", "there")
            phone_number = msg["from"]
            user_text = msg.get("text", {}).get("body", "").strip()

            # Determine response
            if user_text.lower() in ["hi", "hello", "menu", "start"]:
                response_text = format_main_menu(user_name)
            else:
                response_text = handle_menu_choice(user_text, user_name)

            logger.info(f"Replying to {phone_number}: {response_text}")

            # Simulated response (replace with WhatsApp API call later)
            return {"reply": response_text}

    except Exception as e:
        logger.error(f"Error handling message: {e}")

    return {"status": "ok"}

# ------------------------- 
# # Startup log # ------------------------- 
@app.on_event("startup")
async def startup_event():
    print("🚀 JibuJob WhatsApp bot (Day 4) is live and running.")
