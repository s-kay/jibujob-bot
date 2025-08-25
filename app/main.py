import os
import logging
import time
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

# --- Mock Datasets ---
JOBS = {
    "software developer": [
        "Junior Python Developer – https://jobs.example.com/dev1",
        "Frontend Engineer – https://jobs.example.com/dev2",
        "Backend Engineer – https://jobs.example.com/dev3",
    ],
    "accountant": [
        "Accounts Assistant – https://jobs.example.com/acc1",
        "Finance Analyst – https://jobs.example.com/acc2",
        "Payroll Specialist – https://jobs.example.com/acc3",
    ],
}

TRAININGS = {
    "digital skills": [
        "Intro to Digital Literacy – https://training.example.com/ds1",
        "Advanced Excel – https://training.example.com/ds2",
    ],
    "entrepreneurship": [
        "How to Start a Small Business – https://training.example.com/ent1",
        "Marketing Basics – https://training.example.com/ent2",
    ],
}

MENTORSHIPS = {
    "tech": [
        "Meet Jane (Senior Developer) – https://mentorship.example.com/tech1",
        "Meet Alex (CTO Mentor) – https://mentorship.example.com/tech2",
    ],
    "business": [
        "Meet Mary (Startup Coach) – https://mentorship.example.com/biz1",
        "Meet Daniel (Finance Mentor) – https://mentorship.example.com/biz2",
    ],
}

ENTREPRENEURSHIPS = {
    "freelancing": [
        "Guide to Freelancing Platforms – https://biz.example.com/freelance1",
        "How to Price Your Services – https://biz.example.com/freelance2",
    ],
    "agribusiness": [
        "Starting a Poultry Farm – https://biz.example.com/agri1",
        "Modern Farming Techniques – https://biz.example.com/agri2",
    ],
    "e-commerce": [
        "Launch an Online Store – https://biz.example.com/ecom1",
        "Dropshipping Basics – https://biz.example.com/ecom2",
    ],
    "crafts": [
        "Turning Crafts into Business – https://biz.example.com/crafts1",
        "Selling Handmade Goods – https://biz.example.com/crafts2",
    ],
    "digital services": [
        "Offering Social Media Marketing – https://biz.example.com/ds1",
        "Freelance Graphic Design – https://biz.example.com/ds2",
    ],
}

# --- Constants ---
SESSION_TIMEOUT = 300  # 5 minutes
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

def is_session_expired(state: dict) -> bool:
    now = time.time()
    last_active = state.get("last_active", now)
    return (now - last_active) > SESSION_TIMEOUT

def paginate_results(items, start, count=2):
    end = start + count
    return items[start:end], end if end < len(items) else 0

# --- Handlers ---
async def handle_message(from_number: str, user_name: str, message_text: str):
    message_text = message_text.strip().lower()

    # Check or initialize user state
    if from_number not in user_state:
        user_state[from_number] = {"menu": "main"}
    state = user_state[from_number]

    if is_session_expired(state):
        logging.info(f"Session expired for {from_number}, resetting state.")
        user_state[from_number] = {"menu": "main"}
        state = user_state[from_number]

    state["last_active"] = time.time()

    defaults = {
        "job_interest": None, "training_interest": None, "mentorship_interest": None, "entrepreneurship_interest": None,
        "last_job_index": 0, "last_training_index": 0, "last_mentorship_index": 0, "last_entrepreneurship_index": 0,
        "awaiting_job_role": False, "awaiting_job_confirm": False,
        "awaiting_training_role": False, "awaiting_training_confirm": False,
        "awaiting_mentorship_role": False, "awaiting_mentorship_confirm": False,
        "awaiting_entrepreneurship_role": False, "awaiting_entrepreneurship_confirm": False,
    }
    for k, v in defaults.items():
        state.setdefault(k, v)

    def reset_flags():
        for key in list(state.keys()):
            if key.startswith("awaiting_"):
                state[key] = False

    # Greeting
    if message_text in ["hi", "hello", "start", "menu"]:
        state["menu"] = "main"
        reset_flags()
        reply = f"Hi {user_name}! 👋\n\n👋 Welcome to JibuJob Career Bot!\n{MAIN_MENU}"
        await send_whatsapp_message(from_number, reply)
        return

    # Exit
    if message_text == "0":
        user_state.pop(from_number, None)
        reply = "👋 Goodbye! Your session has been cleared. Type 'hi' to start again."
        await send_whatsapp_message(from_number, reply)
        return

    # ---------------- JOBS FLOW ----------------
    if message_text == "1":
        state["menu"] = "jobs"; reset_flags()
        if state["job_interest"]:
            state["awaiting_job_confirm"] = True
            reply = f"🔎 Last time you were interested in *{state['job_interest']}* jobs.\nDo you still want those listings? (yes/no)"
        else:
            state["awaiting_job_role"] = True
            reply = "🔎 Which type of job are you interested in? (e.g., Software Developer, Accountant)"
        await send_whatsapp_message(from_number, reply); return

    if state["awaiting_job_confirm"]:
        if message_text in ["yes", "y"]:
            listings = JOBS.get(state["job_interest"], [])
            results, nxt = paginate_results(listings, state["last_job_index"])
            reply = f"Here are *{state['job_interest']}* jobs 👇\n" + "\n".join(results) + "\n\n"
            if nxt: reply += "Type 'more' to see more results.\n\n"
            reply += MAIN_MENU
            state["last_job_index"] = nxt; state["menu"] = "jobs"; reset_flags()
        elif message_text in ["no", "n"]:
            state["job_interest"] = None; reset_flags(); state["awaiting_job_role"] = True
            reply = "Okay, what new type of job are you interested in?"
        else: reply = "Please reply with 'yes' or 'no'."
        await send_whatsapp_message(from_number, reply); return

    if state["awaiting_job_role"]:
        state["job_interest"] = message_text; reset_flags(); state["awaiting_job_confirm"] = True
        reply = f"Got it ✅ — I’ll track *{message_text}* jobs!\nWould you like to see *{message_text}* listings now? (yes/no)"
        await send_whatsapp_message(from_number, reply); return

    if message_text == "more" and state["menu"] == "jobs" and state["job_interest"]:
        listings = JOBS.get(state["job_interest"], [])
        results, nxt = paginate_results(listings, state["last_job_index"])
        reply = "More *{}* jobs 👇\n{}\n\n".format(state["job_interest"], "\n".join(results))
        if nxt: reply += "Type 'more' to see more results.\n\n"
        reply += MAIN_MENU; state["last_job_index"] = nxt
        await send_whatsapp_message(from_number, reply); return

    # ---------------- TRAINING FLOW ----------------
    if message_text == "2":
        state["menu"] = "training"; reset_flags()
        if state["training_interest"]:
            state["awaiting_training_confirm"] = True
            reply = f"📚 Last time you chose *{state['training_interest']}* training.\nDo you still want that? (yes/no)"
        else:
            state["awaiting_training_role"] = True
            reply = "📚 Which training module are you interested in? (e.g., Digital Skills, Entrepreneurship)"
        await send_whatsapp_message(from_number, reply); return

    if state["awaiting_training_confirm"]:
        if message_text in ["yes", "y"]:
            listings = TRAININGS.get(state["training_interest"], [])
            results, nxt = paginate_results(listings, state["last_training_index"])
            reply = f"Here’s your *{state['training_interest']}* training 👇\n" + "\n".join(results) + "\n\n"
            if nxt: reply += "Type 'more' to see more.\n\n"
            reply += MAIN_MENU
            state["last_training_index"] = nxt; state["menu"] = "training"; reset_flags()
        elif message_text in ["no", "n"]:
            state["training_interest"] = None; reset_flags(); state["awaiting_training_role"] = True
            reply = "Okay, what new training module are you interested in?"
        else: reply = "Please reply with 'yes' or 'no'."
        await send_whatsapp_message(from_number, reply); return

    if state["awaiting_training_role"]:
        state["training_interest"] = message_text; reset_flags(); state["awaiting_training_confirm"] = True
        reply = f"Perfect ✅ — I’ll guide you through *{message_text}* training!\nDo you want to access it now? (yes/no)"
        await send_whatsapp_message(from_number, reply); return

    if message_text == "more" and state["menu"] == "training" and state["training_interest"]:
        listings = TRAININGS.get(state["training_interest"], [])
        results, nxt = paginate_results(listings, state["last_training_index"])
        reply = f"More *{state['training_interest']}* training 👇\n" + "\n".join(results) + "\n\n"
        if nxt: reply += "Type 'more' to see more.\n\n"
        reply += MAIN_MENU; state["last_training_index"] = nxt
        await send_whatsapp_message(from_number, reply); return

    # ---------------- MENTORSHIP FLOW ----------------
    if message_text == "3":
        state["menu"] = "mentorship"; reset_flags()
        if state["mentorship_interest"]:
            state["awaiting_mentorship_confirm"] = True
            reply = f"🤝 Last time you wanted a *{state['mentorship_interest']}* mentor.\nDo you still want that? (yes/no)"
        else:
            state["awaiting_mentorship_role"] = True
            reply = "🤝 What type of mentorship are you looking for? (e.g., Tech, Business)"
        await send_whatsapp_message(from_number, reply); return

    if state["awaiting_mentorship_confirm"]:
        if message_text in ["yes", "y"]:
            listings = MENTORSHIPS.get(state["mentorship_interest"], [])
            results, nxt = paginate_results(listings, state["last_mentorship_index"])
            reply = f"Here’s your *{state['mentorship_interest']}* mentors 👇\n" + "\n".join(results) + "\n\n"
            if nxt: reply += "Type 'more' to see more.\n\n"
            reply += MAIN_MENU
            state["last_mentorship_index"] = nxt; state["menu"] = "mentorship"; reset_flags()
        elif message_text in ["no", "n"]:
            state["mentorship_interest"] = None; reset_flags(); state["awaiting_mentorship_role"] = True
            reply = "Okay, what type of mentor would you like now?"
        else: reply = "Please reply with 'yes' or 'no'."
        await send_whatsapp_message(from_number, reply); return

    if state["awaiting_mentorship_role"]:
        state["mentorship_interest"] = message_text; reset_flags(); state["awaiting_mentorship_confirm"] = True
        reply = f"Nice ✅ — I’ll connect you with *{message_text}* mentors!\nBrowse now? (yes/no)"
        await send_whatsapp_message(from_number, reply); return

    if message_text == "more" and state["menu"] == "mentorship" and state["mentorship_interest"]:
        listings = MENTORSHIPS.get(state["mentorship_interest"], [])
        results, nxt = paginate_results(listings, state["last_mentorship_index"])
        reply = f"More *{state['mentorship_interest']}* mentors 👇\n" + "\n".join(results) + "\n\n"
        if nxt: reply += "Type 'more' to see more.\n\n"
        reply += MAIN_MENU; state["last_mentorship_index"] = nxt
        await send_whatsapp_message(from_number, reply); return

    # ---------------- ENTREPRENEURSHIP FLOW ----------------
    if message_text == "4":
        state["menu"] = "entrepreneurship"; reset_flags()
        if state["entrepreneurship_interest"]:
            state["awaiting_entrepreneurship_confirm"] = True
            reply = f"💡 Last time you were exploring *{state['entrepreneurship_interest']}*.\nDo you still want that? (yes/no)"
        else:
            state["awaiting_entrepreneurship_role"] = True
            reply = "💡 Which area interests you? (Freelancing, Agribusiness, E-commerce, Crafts, Digital Services)"
        await send_whatsapp_message(from_number, reply); return

    if state["awaiting_entrepreneurship_confirm"]:
        if message_text in ["yes", "y"]:
            listings = ENTREPRENEURSHIPS.get(state["entrepreneurship_interest"], [])
            results, nxt = paginate_results(listings, state["last_entrepreneurship_index"])
            reply = f"Here’s *{state['entrepreneurship_interest']}* resources 👇\n" + "\n".join(results) + "\n\n"
            if nxt: reply += "Type 'more' to see more.\n\n"
            reply += MAIN_MENU
            state["last_entrepreneurship_index"] = nxt; state["menu"] = "entrepreneurship"; reset_flags()
        elif message_text in ["no", "n"]:
            state["entrepreneurship_interest"] = None; reset_flags(); state["awaiting_entrepreneurship_role"] = True
            reply = "Okay, what new area are you interested in?"
        else: reply = "Please reply with 'yes' or 'no'."
        await send_whatsapp_message(from_number, reply); return

    if state["awaiting_entrepreneurship_role"]:
        state["entrepreneurship_interest"] = message_text; reset_flags(); state["awaiting_entrepreneurship_confirm"] = True
        reply = f"Great ✅ — I’ll show you resources for *{message_text}*!\nFetch now? (yes/no)"
        await send_whatsapp_message(from_number, reply); return

    if message_text == "more" and state["menu"] == "entrepreneurship" and state["entrepreneurship_interest"]:
        listings = ENTREPRENEURSHIPS.get(state["entrepreneurship_interest"], [])
        results, nxt = paginate_results(listings, state["last_entrepreneurship_index"])
        reply = f"More *{state['entrepreneurship_interest']}* resources 👇\n" + "\n".join(results) + "\n\n"
        if nxt: reply += "Type 'more' to see more.\n\n"
        reply += MAIN_MENU; state["last_entrepreneurship_index"] = nxt
        await send_whatsapp_message(from_number, reply); return

    # ---------------- FALLBACK ----------------
    reply = f"❓ I didn’t understand that.\n\n{MAIN_MENU}"
    await send_whatsapp_message(from_number, reply)

# --- Webhook ---
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
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
