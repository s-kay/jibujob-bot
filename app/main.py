import os
import logging
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==============================
# Config & Setup
# ==============================
app = FastAPI()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
API_VERSION = "v22.0"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "jibujob-verify")

if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
    logging.error("❌ Missing required environment variables: WHATSAPP_ACCESS_TOKEN / WHATSAPP_PHONE_NUMBER_ID")

GRAPH_API_URL = f"https://graph.facebook.com/{API_VERSION}/{WHATSAPP_PHONE_ID}/messages"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("🚀 Day 4 WhatsApp bot starting...")

# ==============================
# Mock Data
# ==============================
job_listings = [
    {"title": "Solar Technician", "location": "Nairobi", "type": "Full-time"},
    {"title": "Agribusiness Officer", "location": "Kisumu", "type": "Contract"},
    {"title": "Digital Marketing Intern", "location": "Remote", "type": "Internship"},
    {"title": "Community Health Worker", "location": "Mombasa", "type": "Part-time"},
]

training_modules = {
    "1": ["Basic ICT Skills", "Introduction to Solar Installation", "Agribusiness 101"],
    "2": ["Intermediate Web Development", "Mobile Money Operations", "Community Healthcare Basics"],
    "3": ["Advanced AI Skills", "Entrepreneurship & Startups", "Renewable Energy Systems"],
}

mentors = [
    {"name": "Alice", "expertise": "Agribusiness"},
    {"name": "Brian", "expertise": "Software Development"},
    {"name": "Cynthia", "expertise": "Renewable Energy"},
]

# Session state memory (user_id → state)
user_sessions = {}

# ==============================
# Helper Functions
# ==============================
def send_whatsapp_message(to: str, message: str):
    """Send a text message via WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logging.error("❌ Missing token or phone number ID")
        return

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(GRAPH_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        logging.error(f"❌ Error sending message: {response.text}")
    else:
        logging.info(f"✅ Sent message to {to}: {message}")


def get_main_menu():
    return (
        "👋 Welcome to JibuJob Career Bot!\n"
        "Please choose an option:\n\n"
        "1️⃣ Job Listings\n"
        "2️⃣ Training Modules\n"
        "3️⃣ Mentorship\n"
        "0️⃣ Exit"
    )

# ==============================
# Webhook Endpoints
# ==============================
@app.get("/webhook")
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return JSONResponse(content=int(params.get("hub.challenge", 0)), status_code=200)
    return JSONResponse(content="Invalid verification token", status_code=403)


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Handle incoming messages."""
    data = await request.json()
    logging.info(f"📩 Incoming: {data}")

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            message = messages[0]
            sender = message["from"]
            text = message["text"]["body"].strip()

            # Check user session state
            state = user_sessions.get(sender, {"step": "menu"})

            if text == "0":
                send_whatsapp_message(sender, "👋 Goodbye! Type 'hi' to start again anytime.")
                user_sessions.pop(sender, None)
                return {"status": "ok"}

            if state["step"] == "menu":
                if text == "1":
                    # Job listings
                    job_text = "📋 Job Listings:\n"
                    for job in job_listings:
                        job_text += f"- {job['title']} ({job['location']}, {job['type']})\n"
                    job_text += "\nType 'menu' to go back."
                    user_sessions[sender] = {"step": "menu"}
                    send_whatsapp_message(sender, job_text)

                elif text == "2":
                    # Training categories
                    module_text = "📚 Choose a training level:\n"
                    module_text += "1. Beginner\n2. Intermediate\n3. Advanced"
                    user_sessions[sender] = {"step": "training"}
                    send_whatsapp_message(sender, module_text)

                elif text == "3":
                    # Mentorship
                    mentor_text = "🤝 Available Mentors:\n"
                    for m in mentors:
                        mentor_text += f"- {m['name']} ({m['expertise']})\n"
                    mentor_text += "\nType 'menu' to go back."
                    user_sessions[sender] = {"step": "menu"}
                    send_whatsapp_message(sender, mentor_text)

                else:
                    send_whatsapp_message(sender, get_main_menu())

            elif state["step"] == "training":
                if text in training_modules:
                    selected = training_modules[text]
                    course_text = f"📚 {['Beginner','Intermediate','Advanced'][int(text)-1]} Modules:\n"
                    for c in selected:
                        course_text += f"- {c}\n"
                    course_text += "\nType 'menu' to return."
                    user_sessions[sender] = {"step": "menu"}
                    send_whatsapp_message(sender, course_text)
                else:
                    send_whatsapp_message(sender, "❌ Invalid choice. Type 1, 2, or 3.")

            elif text.lower() == "menu" or text.lower() == "hi":
                send_whatsapp_message(sender, get_main_menu())
                user_sessions[sender] = {"step": "menu"}

    except Exception as e:
        logging.error(f"❌ Error handling webhook: {e}")

    return {"status": "ok"}

# -------------------------
# Startup log
# -------------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 JibuJob WhatsApp bot (Day 4) is live and runningz.")
