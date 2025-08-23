import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# ✅ Environment variables (set in Render dashboard)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ✅ Helper to send messages via WhatsApp API
def send_message(to: str, text: str):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    try:
        resp = httpx.post(url, headers=headers, json=payload)
        print("📤 WhatsApp API response:", resp.status_code, resp.text)
        resp.raise_for_status()
    except Exception as e:
        print("❌ Error sending message:", e)

# ✅ Root endpoint
@app.get("/")
async def root():
    return {"status": "JibuJob bot running ✅"}

# ✅ Webhook verification (Meta requires GET)
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == "my_verify_token":
        return JSONResponse(content=int(params.get("hub.challenge","0")))
    return JSONResponse(content="Invalid verification token", status_code=403)

# ✅ Webhook receiver (Meta sends POST here)
@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    print("📩 Incoming payload:", data)  # Debug log

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            print("⚠️ No messages found in payload.")
            return {"status": "no messages"}

        msg = messages[0]
        from_number = msg.get("from")
        text = ""

        # ✅ Extract text safely
        if msg.get("type") == "text":
            text = msg["text"].get("body", "").strip()

        print("📩 Extracted text:", text)

        # ✅ Menu logic
        if text == "1":
            reply = "Here are some sample job listings:\n- Software Engineer (Remote)\n- Marketing Intern (Nairobi)\n- Sales Associate (Mombasa)"
        elif text == "2":
            reply = "Here are some training resources:\n- https://www.coursera.org\n- https://www.udemy.com\n- https://www.linkedin.com/learning"
        elif text == "3":
            reply = "We can connect you with a mentor. Reply with your field of interest (e.g., Tech, Business, Design)."
        else:
            reply = (
                "👋 Welcome to JibuJob!\n"
                "Please choose an option:\n"
                "1️⃣ Sample Job Listings\n"
                "2️⃣ Training Links\n"
                "3️⃣ Mentor Introductions"
            )

        # ✅ Send reply
        if from_number:
            send_message(from_number, reply)

    except Exception as e:
        print("❌ Error in webhook_handler:", e)

    return {"status": "ok"}
