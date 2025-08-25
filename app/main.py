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

# --- Simple in-memory state store ---
user_state = {}  # { phone_number: {...} }

# --- Constants ---
MAIN_MENU = (
    "Please choose an option:\n\n"
    "1️⃣ Job Listings\n"
    "2️⃣ Training Modules\n"
    "3️⃣ Mentorship\n"
    "4️⃣ Micro-entrepreneurship\n"
    "0️⃣ Exit"
)

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

    # Initialize state for new user
    if from_number not in user_state:
        user_state[from_number] = {
            "menu": "main",
            "job_interest": None,
            "training_interest": None,
            "mentorship_interest": None,
            "entrepreneurship_interest": None,
            "pending_flow": None,  # track if user is being re-asked
        }

    state = user_state[from_number]

    # Main Menu Greeting
    if message_text in ["hi", "hello", "start", "menu"]:
        state["menu"] = "main"
        state["pending_flow"] = None
        reply = (
            f"Hi {user_name}! 👋\n\n"
            "👋 Welcome to JibuJob Career Bot!\n"
            f"{MAIN_MENU}"
        )
        await send_whatsapp_message(from_number, reply)
        return

    # Exit clears state
    if message_text == "0":
        user_state.pop(from_number, None)
        reply = "👋 Goodbye! Your session has been cleared. Type 'hi' to start again."
        await send_whatsapp_message(from_number, reply)
        return

    # --- Jobs flow ---
    if message_text == "1":
        state["menu"] = "jobs"
        if state["job_interest"]:
            state["pending_flow"] = "jobs"
            reply = (
                f"🔎 Last time you were interested in *{state['job_interest']}* jobs.\n"
                "Do you still want those listings? (yes/no)"
            )
        else:
            reply = "🔎 Which type of job are you interested in? (e.g., Software Developer, Accountant)"
        await send_whatsapp_message(from_number, reply)
        return

    if state["menu"] == "jobs" and message_text not in ["1", "2", "3", "4", "0"]:
        if state.get("pending_flow") == "jobs":
            if message_text in ["yes", "y"]:
                reply = (
                    f"Here are the latest *{state['job_interest']}* jobs 👇\n"
                    f"https://jobs.example.com/{state['job_interest'].replace(' ', '-')}\n\n"
                    f"{MAIN_MENU}"
                )
                state["menu"] = "main"
                state["pending_flow"] = None
            elif message_text in ["no", "n"]:
                state["job_interest"] = None
                state["pending_flow"] = None
                reply = "Okay, what new type of job are you interested in?"
            else:
                reply = "❓ Please reply with *yes* or *no*."
        else:
            state["job_interest"] = message_text
            reply = (
                f"Got it ✅ — I’ll track *{message_text}* jobs for you!\n"
                f"Would you like to see some *{message_text}* listings now? (yes/no)"
            )
        await send_whatsapp_message(from_number, reply)
        return

    # --- Training flow ---
    if message_text == "2":
        state["menu"] = "training"
        if state["training_interest"]:
            state["pending_flow"] = "training"
            reply = (
                f"📚 Last time you chose *{state['training_interest']}* training.\n"
                "Do you still want that? (yes/no)"
            )
        else:
            reply = "📚 Which training module are you interested in? (e.g., Digital Skills, Entrepreneurship)"
        await send_whatsapp_message(from_number, reply)
        return

    if state["menu"] == "training" and message_text not in ["1", "2", "3", "4", "0"]:
        if state.get("pending_flow") == "training":
            if message_text in ["yes", "y"]:
                reply = (
                    f"Here’s your *{state['training_interest']}* training module 👇\n"
                    f"https://training.example.com/{state['training_interest'].replace(' ', '-')}\n\n"
                    f"{MAIN_MENU}"
                )
                state["menu"] = "main"
                state["pending_flow"] = None
            elif message_text in ["no", "n"]:
                state["training_interest"] = None
                state["pending_flow"] = None
                reply = "Okay, what new training module are you interested in?"
            else:
                reply = "❓ Please reply with *yes* or *no*."
        else:
            state["training_interest"] = message_text
            reply = (
                f"Perfect ✅ — I’ll guide you through *{message_text}* training!\n"
                f"Do you want to access the *{message_text}* course now? (yes/no)"
            )
        await send_whatsapp_message(from_number, reply)
        return

    # --- Mentorship flow ---
    if message_text == "3":
        state["menu"] = "mentorship"
        if state["mentorship_interest"]:
            state["pending_flow"] = "mentorship"
            reply = (
                f"🤝 Last time you wanted a *{state['mentorship_interest']}* mentor.\n"
                "Do you still want that? (yes/no)"
            )
        else:
            reply = "🤝 What type of mentorship are you looking for? (e.g., Tech, Business, Career)"
        await send_whatsapp_message(from_number, reply)
        return

    if state["menu"] == "mentorship" and message_text not in ["1", "2", "3", "4", "0"]:
        if state.get("pending_flow") == "mentorship":
            if message_text in ["yes", "y"]:
                reply = (
                    f"Here’s your *{state['mentorship_interest']}* mentorship resources 👇\n"
                    f"https://mentorship.example.com/{state['mentorship_interest'].replace(' ', '-')}\n\n"
                    f"{MAIN_MENU}"
                )
                state["menu"] = "main"
                state["pending_flow"] = None
            elif message_text in ["no", "n"]:
                state["mentorship_interest"] = None
                state["pending_flow"] = None
                reply = "Okay, what type of mentor would you like now?"
            else:
                reply = "❓ Please reply with *yes* or *no*."
        else:
            state["mentorship_interest"] = message_text
            reply = (
                f"Nice ✅ — I’ll connect you with *{message_text}* mentors!\n"
                f"Would you like to browse *{message_text}* mentor profiles now? (yes/no)"
            )
        await send_whatsapp_message(from_number, reply)
        return

    # --- Micro-entrepreneurship flow ---
    if message_text == "4":
        state["menu"] = "entrepreneurship"
        if state["entrepreneurship_interest"]:
            state["pending_flow"] = "entrepreneurship"
            reply = (
                f"💡 Last time you were exploring *{state['entrepreneurship_interest']}* opportunities.\n"
                "Do you still want that? (yes/no)"
            )
        else:
            reply = (
                "💡 Which micro-entrepreneurship area interests you?\n"
                "Options: Freelancing, Agribusiness, E-commerce, Crafts, Digital Services"
            )
        await send_whatsapp_message(from_number, reply)
        return

    if state["menu"] == "entrepreneurship" and message_text not in ["1", "2", "3", "4", "0"]:
        if state.get("pending_flow") == "entrepreneurship":
            if message_text in ["yes", "y"]:
                reply = (
                    f"Here’s more info on *{state['entrepreneurship_interest']}* 👇\n"
                    f"https://biz.example.com/{state['entrepreneurship_interest'].replace(' ', '-')}\n\n"
                    "📖 Startup Guide: https://biz.example.com/guides\n"
                    "💰 Funding Opportunities: https://biz.example.com/funding\n"
                    "📂 Business Templates: https://biz.example.com/templates\n\n"
                    f"{MAIN_MENU}"
                )
                state["menu"] = "main"
                state["pending_flow"] = None
            elif message_text in ["no", "n"]:
                state["entrepreneurship_interest"] = None
                state["pending_flow"] = None
                reply = "Okay, what new business area are you interested in?"
            else:
                reply = "❓ Please reply with *yes* or *no*."
        else:
            state["entrepreneurship_interest"] = message_text
            reply = (
                f"Great ✅ — I’ll show you resources for *{message_text}*!\n"
                f"Do you want me to fetch *{message_text}* resources now? (yes/no)"
            )
        await send_whatsapp_message(from_number, reply)
        return

    # --- Fallback ---
    reply = (
        "❓ I didn’t understand that.\n\n"
        f"{MAIN_MENU}"
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
        return JSONResponse(content=int(params.get("hub.challenge", "0")), status_code=200)
    logging.warning("Webhook verification failed.")
    return JSONResponse(content="Verification failed", status_code=403)

@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        data = await request.json()
        logging.info(f"Incoming webhook data: {data}")

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
