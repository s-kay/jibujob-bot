import os
import logging
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jibujob")

# Load environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# Validate env vars early
if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
    raise ValueError("Missing one or more required environment variables: WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID")

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 JibuJob Bot Day 4 started successfully with menu consistency!")

def send_whatsapp_message(to: str, message: str):
    """
    Send a WhatsApp message using the Meta WhatsApp Cloud API.
    """
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
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

    try:
        response = httpx.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"✅ Message sent to {to}")
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Error sending message: {e.response.text}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

@app.post("/webhook")
async def webhook(request: Request):
    """
    Handle incoming messages from WhatsApp webhook.
    """
    data = await request.json()
    logger.info(f"📩 Incoming webhook data: {data}")

    try:
        messages = data.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])
        if not messages:
            return JSONResponse(content={"status": "ignored"}, status_code=200)

        message = messages[0]
        from_number = message["from"]
        user_text = message.get("text", {}).get("body", "").strip()

        if user_text in ["hi", "hello", "menu", "start"]:
            send_whatsapp_message(
                from_number,
                "👋 Welcome to *JibuJob*! Please choose an option:\n\n"
                "1️⃣ Jobs\n"
                "2️⃣ Mentorship\n"
                "3️⃣ Skills Training\n"
                "4️⃣ Micro-entrepreneurship\n\n"
            )

        elif user_text == "1":
            send_whatsapp_message(
                from_number,
                "📌 Here are some sample job listings:\n\n"
                "1. Software Developer - Nairobi (Remote)\n"
                "2. Marketing Intern - Mombasa (Hybrid)\n"
                "3. Data Analyst - Kisumu (Onsite)\n\n"
                "Reply *menu* to go back."
            )

        elif user_text == "2":
            send_whatsapp_message(
                from_number,
                "🤝 Mentorship Options:\n\n"
                "1. Career Guidance with Industry Experts\n"
                "2. Peer-to-Peer Mentorship\n"
                "3. Professional Networking Events\n\n"
                "Reply *menu* to go back."
            )

        elif user_text == "3":
            send_whatsapp_message(
                from_number,
                "📚 Skills Training Resources:\n\n"
                "1. Digital Marketing Bootcamp\n"
                "2. Basic Coding (Python & Web Dev)\n"
                "3. Entrepreneurship 101\n\n"
                "Reply *menu* to go back."
            )

        elif user_text == "4":
            send_whatsapp_message(
                from_number,
                "💡 Micro-entrepreneurship Opportunities:\n\n"
                "1. Small Agribusiness Grants\n"
                "2. Local E-commerce Training\n"
                "3. Youth Savings & Loan Groups\n\n"
                "Reply *menu* to go back."
            )

        else:
            send_whatsapp_message(
                from_number,
                "❓ I didn't understand that. Please reply with a number (1-4) or *menu*."
            )

    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")

    return JSONResponse(content={"status": "received"}, status_code=200)
