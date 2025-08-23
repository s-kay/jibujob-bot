import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "testtoken")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
BASE_URL = "https://graph.facebook.com/v22.0"

# ✅ Mock job dataset
JOB_LISTINGS = {
    "Tech": [
        "Software Engineer (Remote, Kenya) – Ksh 150k/month",
        "Junior Data Analyst (Nairobi, Hybrid) – Ksh 80k/month",
        "Cloud Support Associate (Remote, Africa-wide) – Ksh 100k/month",
    ],
    "Business & Sales": [
        "Sales Associate (Mombasa, In-office) – Commission-based",
        "Marketing Intern (Nairobi, Hybrid) – Stipend + allowance",
        "Customer Success Officer (Kisumu, Remote possible) – Ksh 60k/month",
    ],
    "Skilled Trades": [
        "Electrician Apprentice (Nakuru, In-office) – Ksh 40k/month",
        "Plumbing Technician (Eldoret, In-office) – Ksh 45k/month",
    ],
    "Creative & Media": [
        "Graphic Designer (Remote) – Freelance, project-based",
        "Content Creator (Nairobi, Hybrid) – Ksh 70k/month",
    ],
}

# ✅ Helper to format jobs
def format_jobs() -> str:
    text = "📋 *Sample Job Listings* 📋\n\n"
    for category, jobs in JOB_LISTINGS.items():
        text += f"🔹 *{category}*\n"
        for job in jobs:
            text += f"- {job}\n"
        text += "\n"
    text += "👉 Reply with the job title you're interested in to learn more."
    return text.strip()

# ✅ Helper to send WhatsApp message
def send_message(to: str, text: str):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
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

# ✅ Webhook verification
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == "my_verify_token":
        return JSONResponse(content=int(params.get("hub.challenge","0")))
    return JSONResponse(content="Invalid verification token", status_code=403)

# ✅ Webhook receiver
@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    print("📩 Incoming payload:", data)  # Debug

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

        if msg.get("type") == "text":
            text = msg["text"].get("body", "").strip()

        print("📩 Extracted text:", text)

        # ✅ Menu logic
        if text == "1":
            reply = format_jobs()
        elif text == "2":
            reply = (
                "📚 *Training Resources*\n\n"
                "- Coursera: https://www.coursera.org\n"
                "- Udemy: https://www.udemy.com\n"
                "- LinkedIn Learning: https://www.linkedin.com/learning\n"
            )
        elif text == "3":
            reply = (
                "🤝 *Mentorship Matching*\n\n"
                "Please reply with your field of interest:\n"
                "- Tech\n"
                "- Business\n"
                "- Creative\n"
                "- Skilled Trades"
            )
        else:
            reply = (
                "👋 Welcome to JibuJob!\n"
                "Please choose an option:\n"
                "1️⃣ Sample Job Listings\n"
                "2️⃣ Training Links\n"
                "3️⃣ Mentor Introductions"
            )

        if from_number:
            send_message(from_number, reply)

    except Exception as e:
        print("❌ Error in webhook_handler:", e)

    return {"status": "ok"}
