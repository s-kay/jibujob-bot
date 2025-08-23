import os
from fastapi import FastAPI, Request
import httpx
from typing import Dict

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "JibuJob Bot API is running 🚀"}

# Load sensitive values from environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "jibujob-verify")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v22.0")

# WhatsApp Graph API base
def get_whatsapp_url() -> str:
    if not WHATSAPP_PHONE_ID:
        raise ValueError("❌ WHATSAPP_PHONE_ID is not set in environment variables.")
    return f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"

# Mock datasets
jobs_dataset = [
    {"title": "Software Engineer", "company": "Andela", "location": "Nairobi", "link": "https://andela.com/careers"},
    {"title": "Cloud Engineer", "company": "Microsoft", "location": "Remote", "link": "https://careers.microsoft.com"},
    {"title": "Data Analyst", "company": "Safaricom", "location": "Nairobi", "link": "https://safaricom.co.ke/careers"},
]

training_links = [
    "👉 Digital Skills: https://learndigital.withgoogle.com/digitalskills",
    "👉 Microsoft Learn: https://learn.microsoft.com/training",
    "👉 Coursera Africa: https://www.coursera.org",
]

mentors = [
    "🌟 Lucy — Tech Career Coach",
    "🌟 Brian — Cloud Architect Mentor",
    "🌟 Anita — Data Science Guide",
]

# Function to send messages
async def send_whatsapp_message(to: str, message: str) -> None:
    if not WHATSAPP_TOKEN:
        print("❌ WHATSAPP_TOKEN is missing. Set WHATSAPP_TOKEN in environment.")
        return

    try:
        url = get_whatsapp_url()
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload: Dict = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"❌ Error sending message: {response.text}")
            else:
                print(f"✅ Message sent: {response.text}")
    except Exception as e:
        print(f"🔥 Exception while sending message: {e}")

# Webhook verification
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge", 0))
    return {"error": "Invalid verification token"}

# Webhook receiver
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            msg = messages[0]
            sender = msg["from"]
            text = msg.get("text", {}).get("body", "").strip()

            if text == "1":
                jobs_text = "📌 Sample Job Listings:\n"
                for job in jobs_dataset:
                    jobs_text += f"- {job['title']} at {job['company']} ({job['location']})\nApply: {job['link']}\n\n"
                await send_whatsapp_message(sender, jobs_text.strip())

            elif text == "2":
                training_text = "📚 Training Resources:\n" + "\n".join(training_links)
                await send_whatsapp_message(sender, training_text)

            elif text == "3":
                mentors_text = "🤝 Meet our Mentors:\n" + "\n".join(mentors)
                await send_whatsapp_message(sender, mentors_text)

            else:
                welcome = (
                    "👋 Welcome to JibuJob!\nReply with:\n"
                    "1️⃣ Jobs\n2️⃣ Training\n3️⃣ Mentor"
                )
                await send_whatsapp_message(sender, welcome)
    except Exception as e:
        print(f"⚠️ Webhook handling error: {e}")

    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "JibuJob Bot API is running 🚀"}
