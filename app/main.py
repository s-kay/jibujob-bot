import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx   # ✅ make sure httpx is imported

app = FastAPI()

# Environment variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "testtoken")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ✅ BASE_URL definition
BASE_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"


@app.get("/")
async def root():
    return {"message": "JibuJob Bot API is running 🚀"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Webhook verification endpoint for WhatsApp Cloud API"""
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge","0"))
    return JSONResponse(content={"error": "Invalid verification"}, status_code=403)


@app.post("/webhook")
async def webhook(request: Request):
    """Handles incoming WhatsApp messages"""
    data = await request.json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            message = value["messages"][0]
            sender = message["from"]
            text = message.get("text", {}).get("body", "").strip()

            # ✅ Simple menu logic
            if text in ["1", "Jobs", "jobs"]:
                reply = "🔎 Great! Send me a job title (e.g., 'Accountant') and I’ll search for opportunities."
            elif text in ["2", "Training", "training"]:
                reply = "📚 Awesome! We’ll connect you to training resources. (Coming soon!)"
            elif text in ["3", "Mentor", "mentor"]:
                reply = "🤝 Wonderful! We’ll match you with mentors. (Coming soon!)"
            else:
                reply = (
                    "👋 Welcome to JibuJob! Reply with:\n"
                    "1️⃣ Jobs\n"
                    "2️⃣ Training\n"
                    "3️⃣ Mentor"
                )

            await send_message(sender, reply)

    except Exception as e:
        print("Webhook Error:", e)

    return {"status": "received"}


async def send_message(recipient: str, message: str):
    """Send WhatsApp message via Cloud API"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, headers=headers, json=payload)
        print("Send message response:", response.status_code, response.text)


@app.post("/send_message")
async def manual_send(request: Request):
    """Manual test endpoint to send messages"""
    data = await request.json()
    recipient = data.get("recipient")
    message = data.get("message", "Hello from JibuJob!")
    await send_message(recipient, message)
    return {"status": "sent", "to": recipient, "message": message}
