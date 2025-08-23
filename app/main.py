import os
import httpx
from fastapi import FastAPI, Request

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "testtoken")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
BASE_URL = "https://graph.facebook.com/v20.0"

@app.get("/")
async def root():
    return {"message": "JibuJob Bot API is running 🚀 (Day 3)"}

# ✅ Webhook verification (Meta calls this once)
@app.get("/webhook")
async def verify(request: Request):
    params = dict(request.query_params)
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge","0"))
    return {"error": "Verification failed"}

# ✅ Handle incoming messages
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        messages = changes["value"].get("messages")

        if messages:
            msg = messages[0]
            from_number = msg["from"]
            text = msg.get("text", {}).get("body", "").strip()

            # ✅ Menu logic
            if text == "1":
                reply = (
                    "📋 *Sample Job Listings:*\n"
                    "- Software Developer at Nairobi Tech\n"
                    "- Sales Associate at Mombasa Retail Ltd\n"
                    "- Data Analyst (Remote) at Africa DataHub\n\n"
                    "👉 Reply with the job title for more details."
                )
            elif text == "2":
                reply = (
                    "📚 *Training Opportunities:*\n"
                    "- Free Azure Fundamentals Course: https://learn.microsoft.com/en-us/training/azure\n"
                    "- Digital Marketing Basics: https://learndigital.withgoogle.com\n"
                    "- Data Science for Beginners: https://www.kaggle.com/learn\n\n"
                    "👉 Pick one to explore!"
                )
            elif text == "3":
                reply = (
                    "🤝 *Mentor Introductions:*\n"
                    "- Lucy (Tech Career Coach)\n"
                    "- Peter (Entrepreneurship Mentor)\n"
                    "- Amina (CV & Interview Prep)\n\n"
                    "👉 Reply with a mentor’s name to connect."
                )
            else:
                reply = (
                    "👋 Welcome to JibuJob! Reply with:\n"
                    "1️⃣ Jobs\n"
                    "2️⃣ Training\n"
                    "3️⃣ Mentor"
                )

            await send_message(from_number, reply)

    except Exception as e:
        print("❌ Error handling message:", e)

    return {"status": "ok"}

# ✅ Send a WhatsApp message via Cloud API
async def send_message(to: str, message: str):
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print("❌ Error sending message:", response.text)
        else:
            print("✅ Sent:", message)
