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
                if messages:
                    phone_number = messages[0]["from"]
                    user_text = messages[0]["text"]["body"].strip().lower()

                    # Menu responses
                    if user_text in ["hi", "menu", "hello"]:
                        menu = (
                            "👋 Welcome to JibuJob!\n\n"
                            "Please choose an option:\n"
                            "1️⃣ Job Listings\n"
                            "2️⃣ Training Resources\n"
                            "3️⃣ Mentorship Connections"
                        )
                        await send_message(phone_number, menu)

                    elif user_text.startswith("1") or "job" in user_text:
                        job_list = "\n\n".join([f"💼 {job['title']} at {job['company']} ({job['location']})\nApply: {job['apply_link']}" for job in mock_jobs])
                        await send_message(phone_number, f"Here are some opportunities:\n\n{job_list}")

                    elif user_text.startswith("2") or "train" in user_text:
                        resources = (
                            "📚 Free Training Resources:\n"
                            "- Microsoft Learn: https://learn.microsoft.com/\n"
                            "- Coursera (Free Courses): https://coursera.org\n"
                            "- ALX Africa: https://www.alxafrica.com/"
                        )
                        await send_message(phone_number, resources)

                    elif user_text.startswith("3") or "mentor" in user_text:
                        mentorship = (
                            "🤝 Mentorship Program:\n"
                            "We can connect you with industry mentors in Tech, Business, and Design.\n"
                            "Reply with your area of interest to get started."
                        )
                        await send_message(phone_number, mentorship)

                    else:
                        await send_message(phone_number, "❓ Sorry, I didn’t understand. Please reply with 'Menu' to see options.")

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {str(e)}")

    return JSONResponse(content={"status": "ok"})

# --- Startup Log ---
@app.on_event("startup")
async def startup_event():
    logging.info("🚀 JibuJob WhatsApp Bot is up and running on Day 3 ✅")
