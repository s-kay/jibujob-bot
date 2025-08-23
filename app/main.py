import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

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
    data = await request.json()

    # WhatsApp sends events in entry[0].changes[0].value
    try:
        messages = (
            data.get("entry", [])[0]
            .get("changes", [])[0]
            .get("value", {})
            .get("messages", [])
        )
    except Exception:
        messages = []

    for message in messages:
        if message.get("type") == "text":
            from_number = message["from"]
            user_text = message["text"]["body"]

            # For Day 1: simple static JSON-driven reply
            reply_text = get_first_flow_reply(user_text)

            send_whatsapp_message(from_number, reply_text)

    return {"status": "ok"}


# --- Send message to WhatsApp ---
def send_whatsapp_message(to: str, message: str):
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
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    if response.status_code >= 400:
        print("Error sending message:", response.text)


# --- First working flow (static JSON) ---
def get_first_flow_reply(user_text: str) -> str:
    """
    Very simple Day 1 flow:
    User says anything → reply with a canned response
    """
    flow = {
        "greeting": "👋 Welcome to JibuJob! Reply with:\n1️⃣ Jobs\n2️⃣ Training\n3️⃣ Mentor",
        "fallback": "I didn’t understand that. Please reply with 1, 2, or 3.",
        "options": {
            "1": "Here are some jobs near you 🚀",
            "2": "Here’s training content 📚",
            "3": "We’ll connect you with a mentor 🤝",
        },
    }

    normalized = user_text.strip().lower()
    return flow["options"].get(normalized, flow["greeting"])
