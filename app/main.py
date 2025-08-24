import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v22.0")


if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID or not VERIFY_TOKEN:
    raise ValueError("Missing one or more required environment variables.")

app = FastAPI()

# -------------------------
# In-memory user state store
# -------------------------
user_states = {}

# -------------------------
# Mock job dataset
# -------------------------
mock_jobs = {
    "tech": [
        {"title": "Junior Software Developer", "company": "Nairobi Tech Hub"},
        {"title": "Cloud Engineer Intern", "company": "Safaricom"},
    ],
    "finance": [
        {"title": "Accounting Assistant", "company": "Equity Bank"},
        {"title": "Financial Analyst Trainee", "company": "KCB Group"},
    ],
    "general": [
        {"title": "Customer Service Representative", "company": "Kenya Airways"},
        {"title": "Logistics Assistant", "company": "DHL Nairobi"},
    ]
}

# -------------------------
# Helper: send message
# -------------------------
def send_message(to, text):
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text},
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Error sending message: {response.text}")
    return response.json()

# -------------------------
# Helper: main menu
# -------------------------
def get_main_menu():
    return (
        "👋 Welcome to *JibuJob*! Please choose an option:\n\n"
        "1️⃣ Jobs\n"
        "2️⃣ Mentorship\n"
        "3️⃣ Skills Training\n"
        "4️⃣ Micro-entrepreneurship\n\n"
        "Type the number of your choice."
    )

# -------------------------
# Webhook verification
# -------------------------
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return JSONResponse(content=int(params.get("hub.challenge", 0)), status_code=200)
    return JSONResponse(content="Invalid verification token", status_code=403)

# -------------------------
# Webhook message handling
# -------------------------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        messages = entry.get("messages")

        if messages:
            msg = messages[0]
            from_number = msg["from"]

            # Extract user name if available
            profile = entry.get("contacts", [{}])[0].get("profile", {})
            user_name = profile.get("name", "there")

            text = msg.get("text", {}).get("body", "").strip().lower()
            print(f"📩 Message from {from_number} ({user_name}): {text}")

            # Initialize user state if new
            if from_number not in user_states:
                user_states[from_number] = {"stage": "menu", "interest": None}
                send_message(from_number, f"Hi {user_name}! 👋")
                send_message(from_number, get_main_menu())
                return JSONResponse(content={"status": "new user greeted"})

            # Handle back-to-menu
            if text in ["menu", "back"]:
                user_states[from_number]["stage"] = "menu"
                send_message(from_number, get_main_menu())
                return JSONResponse(content={"status": "returned to menu"})

            stage = user_states[from_number]["stage"]

            # -------------------------
            # Stage: menu
            # -------------------------
            if stage == "menu":
                if text in ["1", "jobs"]:
                    user_states[from_number]["stage"] = "jobs"
                    send_message(
                        from_number,
                        "Great choice! Do you prefer *tech* jobs, *finance*, or *general* opportunities?"
                    )
                elif text in ["2", "mentorship"]:
                    user_states[from_number]["stage"] = "mentorship"
                    send_message(from_number, "🌱 Mentorship is coming soon! Type 'menu' to return.")
                elif text in ["3", "skills training"]:
                    user_states[from_number]["stage"] = "training"
                    send_message(from_number, "📘 Skills training modules will be available soon!")
                elif text in ["4", "micro-entrepreneurship"]:
                    user_states[from_number]["stage"] = "entrepreneurship"
                    send_message(from_number, "🚀 Micro-entrepreneurship resources are coming soon!")
                else:
                    send_message(from_number, "❌ Invalid choice. Please select again:\n\n" + get_main_menu())

            # -------------------------
            # Stage: jobs
            # -------------------------
            elif stage == "jobs":
                if text in mock_jobs:
                    user_states[from_number]["interest"] = text
                    jobs = mock_jobs[text]
                    job_list = "\n".join([f"- {j['title']} at {j['company']}" for j in jobs])
                    send_message(from_number, f"Here are some {text} jobs:\n\n{job_list}\n\nType 'menu' to go back.")
                else:
                    send_message(
                        from_number,
                        "❌ Please type 'tech', 'finance', or 'general' to see jobs. Or type 'menu' to return."
                    )

            else:
                send_message(from_number, "⚠️ I didn’t understand that. Type 'menu' to start again.")

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")

    return JSONResponse(content={"status": "received"})

# -------------------------
# Startup log
# -------------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 JibuJob WhatsApp bot (Day 4) is live and running.")
