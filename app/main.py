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



logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("🚀 Day 4 WhatsApp bot starting...")

# ==============================
# Mock Data
# ==============================
job_listings = [
    {"title": "Software Engineer", "company": "Safaricom", "location": "Nairobi", "apply_link": "https://safaricom.co.ke/careers"},
    {"title": "Data Analyst", "company": "KCB Bank", "location": "Nairobi", "apply_link": "https://kcbgroup.com/careers"},
    {"title": "AI Research Intern", "company": "iHub Kenya", "location": "Remote", "apply_link": "https://ihub.co.ke/jobs"},
    {"title": "Cloud Engineer", "company": "Microsoft ADC", "location": "Lagos", "apply_link": "https://microsoft.com/careers"},
    {"title": "Frontend Developer", "company": "Andela", "location": "Remote", "apply_link": "https://andela.com/careers"},
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

# -------------------------
# Helper: send message
# -------------------------
def send_message(to, text):
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"
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
# Webhook verification
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

            # ✅ Extract user name properly
            contacts = value.get("contacts", [])
            user_name = contacts[0].get("profile", {}).get("name", "there") if contacts else "there"

            text = message.get("text", {}).get("body", "").strip().lower()
            print(f"📩 Message from {sender} ({user_name}): {text}")

            # Check user session state
            state = user_sessions.get(sender, {"step": "menu"})

            # Exit command
            if text == "0":
                send_message(sender, "👋 Goodbye! Type 'hi' to start again anytime.")
                user_sessions.pop(sender, None)
                return {"status": "ok"}

            # Initialize user state if new
            if sender not in user_sessions:
                user_sessions[sender] = {"step": "menu", "interest": None}
                send_message(sender, f"Hi {user_name}! 👋")
                send_message(sender, get_main_menu())
                return JSONResponse(content={"status": "new user greeted"})

            # Handle menu selections
            if state["step"] == "menu":
                if text == "1":
                    # Job listings
                    job_list = "\n".join(
                        [f"{idx+1}. {job['title']} at {job['company']} ({job['location']})"
                        for idx, job in enumerate(job_listings)]
                    )
                    reply = f"💼 Available Jobs:\n\n{job_list}\n\n👉 Reply with a job number to see details."
                    user_sessions[sender]["step"] = "job_list"
                    send_message(sender, reply)

                elif text == "2":
                    # Training categories
                    module_text = "📚 Choose a training level:\n"
                    module_text += "1. Beginner\n2. Intermediate\n3. Advanced"
                    user_sessions[sender] = {"step": "training"}
                    send_message(sender, module_text)

                elif text == "3":
                    # Mentorship
                    mentor_text = "🤝 Available Mentors:\n"
                    for m in mentors:
                        mentor_text += f"- {m['name']} ({m['expertise']})\n"
                    mentor_text += "\nType 'menu' to go back."
                    user_sessions[sender] = {"step": "menu"}
                    send_message(sender, mentor_text)

                else:
                    send_message(sender, get_main_menu())

            # Handle job details
            elif state.get("step") == "job_list" and text.isdigit():
                idx = int(text) - 1
                if 0 <= idx < len(job_listings):
                    job = job_listings[idx]
                    reply = (
                        f"💼 *{job['title']}*\n"
                        f"🏢 {job['company']}\n"
                        f"📍 {job['location']}\n"
                        f"🔗 Apply here: {job['apply_link']}"
                    )
                    send_message(sender, reply)
                else:
                    send_message(sender, "⚠️ Invalid choice. Please select a valid job number.")

            # Handle training selection
            elif state["step"] == "training":
                if text in training_modules:
                    selected = training_modules[text]
                    course_text = f"📚 {['Beginner','Intermediate','Advanced'][int(text)-1]} Modules:\n"
                    for c in selected:
                        course_text += f"- {c}\n"
                    course_text += "\nType 'menu' to return."
                    user_sessions[sender] = {"step": "menu"}
                    send_message(sender, course_text)
                else:
                    send_message(sender, "❌ Invalid choice. Type 1, 2, or 3.")

            # Reset to menu
            elif text in ["menu", "hi"]:
                send_message(sender, get_main_menu())
                user_sessions[sender] = {"step": "menu"}

    except Exception as e:
        logging.error(f"❌ Error handling webhook: {e}")

    return {"status": "ok"}

# ------------------------- 
# # Startup log # ------------------------- 
@app.on_event("startup")
async def startup_event():
    print("🚀 JibuJob WhatsApp bot (Day 4) is live and running.")
