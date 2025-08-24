import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Load environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "jibujob_verify")

if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
    raise ValueError("Missing one or more required environment variables: WHATSAPP_TOKEN, WHATSAPP_PHONE_ID")

GRAPH_API_URL = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"

# --- Utils ---
async def send_whatsapp_message(to: str, message: str):
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

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GRAPH_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            logging.info(f"Message sent to {to}: {message}")
        except httpx.HTTPStatusError as e:
            logging.error(f"Error sending message: {e.response.text}")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")

# --- Handlers ---
async def handle_message(from_number: str, user_name: str, message_text: str):
    message_text = message_text.strip().lower()

    if message_text in ["hi", "hello", "start"]:
        reply = (
            f"Hi {user_name}! 👋\n\n"
            "👋 Welcome to JibuJob Career Bot!\n"
            "Please choose an option:\n\n"
            "1️⃣ Job Listings\n"
            "2️⃣ Training Modules\n"
            "3️⃣ Mentorship\n"
            "4️⃣ Micro-entrepreneurship\n"
            "0️⃣ Exit"
        )
        await send_whatsapp_message(from_number, reply)

    elif message_text == "1":
        reply = (
            "🔎 *Job Listings*\n\n"
            "Here are some opportunities you might like:\n\n"
            "• Software Developer (Remote) – Apply here: https://jobs.example.com/dev\n"
            "• Marketing Intern (Nairobi) – Apply here: https://jobs.example.com/marketing\n"
            "• Customer Support Agent – Apply here: https://jobs.example.com/support\n\n"
            "👉 Reply with 'hi' anytime to return to the main menu."
        )
        await send_whatsapp_message(from_number, reply)

    elif message_text == "2":
        reply = (
            "📚 *Training Modules*\n\n"
            "Upskill yourself with our training:\n\n"
            "• Digital Skills – https://training.example.com/digital\n"
            "• Entrepreneurship – https://training.example.com/entrepreneurship\n"
            "• Career Readiness – https://training.example.com/career\n\n"
            "👉 Reply with 'hi' anytime to return to the main menu."
        )
        await send_whatsapp_message(from_number, reply)

    elif message_text == "3":
        reply = (
            "🤝 *Mentorship*\n\n"
            "Connect with experienced mentors:\n\n"
            "• Tech Mentors – https://mentorship.example.com/tech\n"
            "• Business Mentors – https://mentorship.example.com/business\n"
            "• Career Coaches – https://mentorship.example.com/coaches\n\n"
            "👉 Reply with 'hi' anytime to return to the main menu."
        )
        await send_whatsapp_message(from_number, reply)

    elif message_text == "4":
        reply = (
            "💡 *Micro-entrepreneurship*\n\n"
            "Explore small business opportunities:\n\n"
            "• Online Freelancing – https://biz.example.com/freelance\n"
            "• Agribusiness – https://biz.example.com/agri\n"
            "• E-commerce – https://biz.example.com/ecommerce\n\n"
            "👉 Reply with 'hi' anytime to return to the main menu."
        )
        await send_whatsapp_message(from_number, reply)

    elif message_text == "0":
        reply = "👋 Goodbye! Thank you for using JibuJob Career Bot. We wish you success!"
        await send_whatsapp_message(from_number, reply)

    else:
        reply = (
            "❓ I didn’t understand that.\n\n"
            "Please choose an option:\n"
            "1️⃣ Job Listings\n"
            "2️⃣ Training Modules\n"
            "3️⃣ Mentorship\n"
            "4️⃣ Micro-entrepreneurship\n"
            "0️⃣ Exit"
        )
        await send_whatsapp_message(from_number, reply)

# --- Webhook ---
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        logging.info("Webhook verified successfully.")
        return JSONResponse(content=int(params.get("hub.challenge", 0)))
    logging.warning("Webhook verification failed.")
    return JSONResponse(content="Verification failed", status_code=403)

@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    logging.info(f"Incoming webhook data: {data}")

    try:
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])
                    if messages and contacts:
                        msg = messages[0]
                        contact = contacts[0]
                        from_number = msg["from"]
                        message_text = msg.get("text", {}).get("body", "")
                        user_name = contact.get("profile", {}).get("name", "there")

                        await handle_message(from_number, user_name, message_text)
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logging.error(f"Error handling webhook: {str(e)}")
        return JSONResponse(content={"status": "error"}, status_code=500)

@app.on_event("startup")
async def startup_event():
    logging.info("🚀 JibuJob WhatsApp bot started successfully and is ready to receive messages.")
