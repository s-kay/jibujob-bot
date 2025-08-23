import os
import requests
from fastapi import FastAPI, Request
import httpx 

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "JibuJob Bot API is running 🚀"}

# --- Environment variables ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "jibujob-verify")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v19.0")

WHATSAPP_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_ID}/messages"


# --- Verify webhook setup ---
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge", 0))
    return "Verification failed"


# --- Handle incoming messages ---
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

            # Basic menu logic
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
        response = await client.post(WHATSAPP_API_URL, headers=headers, json=payload)
        print("Send message response:", response.status_code, response.text)


@app.post("/send_message")
async def manual_send(request: Request):
    """Manual test endpoint to send messages"""
    data = await request.json()
    recipient = data.get("recipient")
    message = data.get("message", "Hello from JibuJob!")
    await send_message(recipient, message)
    return {"status": "sent", "to": recipient, "message": message}