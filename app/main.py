import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# In-memory user sessions
user_sessions = {}

# Mock dataset for job listings
mock_jobs = [
    {"title": "Software Engineer", "company": "Safaricom", "location": "Nairobi", "apply_link": "https://safaricom.co.ke/careers"},
    {"title": "Data Analyst", "company": "KCB Bank", "location": "Nairobi", "apply_link": "https://kcbgroup.com/careers"},
    {"title": "AI Research Intern", "company": "iHub Kenya", "location": "Remote", "apply_link": "https://ihub.co.ke/jobs"},
    {"title": "Cloud Engineer", "company": "Microsoft ADC", "location": "Lagos", "apply_link": "https://microsoft.com/careers"},
    {"title": "Frontend Developer", "company": "Andela", "location": "Remote", "apply_link": "https://andela.com/careers"},
]

# Helper function: Send message via WhatsApp API
async def send_message(to: str, text: str):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logging.info(f"✅ Message sent to {to}: {text}")
        except httpx.HTTPStatusError as e:
            logging.error(f"❌ Error sending message: {e.response.text}")
        except Exception as e:
            logging.error(f"❌ Unexpected error sending message: {str(e)}")

# Webhook verification
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return JSONResponse(content=int(params.get("hub.challenge", 0)), status_code=200)
    return JSONResponse(content="Invalid verification token", status_code=403)

# Webhook message receiver
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    logging.info(f"📩 Incoming webhook data: {data}")

    try:
        if "entry" in data:
            changes = data["entry"][0].get("changes", [])
            if changes:
                value = changes[0].get("value", {})
                messages = value.get("messages", [])
                contacts = value.get("contacts", [])

                if messages:
                    phone_number = messages[0]["from"]
                    user_text = messages[0]["text"]["body"].strip().lower()
                    user_name = contacts[0]["profile"]["name"] if contacts else "there"

                    # Initialize session if first time
                    if phone_number not in user_sessions:
                        user_sessions[phone_number] = {"step": "menu"}
                        await send_message(
                            phone_number,
                            f"👋 Hi {user_name}, welcome to JibuJob!\nReply 'Menu' to see your options."
                        )
                        return {"status": "new user greeted"}

                    # Retrieve last step
                    session = user_sessions[phone_number]

                    # Main menu
                    if user_text in ["hi", "menu", "hello"]:
                        menu = (
                            "📋 *Main Menu*\n\n"
                            "1️⃣ Job Listings\n"
                            "2️⃣ Training Resources\n"
                            "3️⃣ Mentorship Connections"
                        )
                        user_sessions[phone_number]["step"] = "menu"
                        await send_message(phone_number, menu)

                    # Job listings
                    elif user_text.startswith("1") or "job" in user_text:
                        job_list = "\n".join(
                            [f"{idx+1}. {job['title']} at {job['company']} ({job['location']})"
                             for idx, job in enumerate(mock_jobs)]
                        )
                        reply = f"💼 Available Jobs:\n\n{job_list}\n\n👉 Reply with a job number to see details."
                        user_sessions[phone_number]["step"] = "job_list"
                        await send_message(phone_number, reply)

                    # Handle job details if user previously asked for jobs
                    elif session.get("step") == "job_list" and user_text.isdigit():
                        idx = int(user_text) - 1
                        if 0 <= idx < len(mock_jobs):
                            job = mock_jobs[idx]
                            reply = (
                                f"💼 *{job['title']}*\n"
                                f"🏢 {job['company']}\n"
                                f"📍 {job['location']}\n"
                                f"🔗 Apply here: {job['apply_link']}"
                            )
                            await send_message(phone_number, reply)
                        else:
                            await send_message(phone_number, "⚠️ Invalid choice. Please select a valid job number.")

                    elif user_text.startswith("2") or "train" in user_text:
                        resources = (
                            "📚 Free Training Resources:\n"
                            "- Microsoft Learn: https://learn.microsoft.com/\n"
                            "- Coursera: https://coursera.org\n"
                            "- ALX Africa: https://www.alxafrica.com/"
                        )
                        await send_message(phone_number, resources)

                    elif user_text.startswith("3") or "mentor" in user_text:
                        mentorship = (
                            "🤝 Mentorship Program:\n"
                            "We can connect you with mentors in Tech, Business, and Design.\n"
                            "Reply with your area of interest."
                        )
                        await send_message(phone_number, mentorship)

                    else:
                        await send_message(phone_number, "❓ I didn’t understand. Please reply with 'Menu' to see options.")

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {str(e)}")

    return JSONResponse(content={"status": "ok"})

# --- Startup Log ---
@app.on_event("startup")
async def startup_event():
    logging.info("🚀 JibuJob WhatsApp Bot is up and running on Day 4 ✅")
