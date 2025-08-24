import os
from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

# WhatsApp API credentials
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
    raise ValueError("Missing one or more required environment variables: WHATSAPP_TOKEN, WHATSAPP_PHONE_ID")

# In-memory state tracking per user
user_state = {}

def send_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages"
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
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_main_menu(name):
    return (
        f"Hi {name}! 👋\n\n"
        "👋 Welcome to *JibuJob Career Bot*!\n"
        "Please choose an option:\n\n"
        "1️⃣ Job Listings\n"
        "2️⃣ Training Modules\n"
        "3️⃣ Mentorship\n"
        "4️⃣ Micro-entrepreneurship\n"
        "0️⃣ Exit"
    )

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return Response(challenge, status=200)
        else:
            return Response("Verification failed", status=403)

    if request.method == "POST":
        body = request.get_json()
        # process body here
        return Response("EVENT_RECEIVED", status=200)
    data = request.get_json()
    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    phone_number = msg["from"]
                    text = msg.get("text", {}).get("body", "").strip()
                    name = msg.get("profile", {}).get("name", "there")

                    # Initialize user state if new
                    if phone_number not in user_state:
                        user_state[phone_number] = {"state": "MAIN_MENU"}

                    state = user_state[phone_number]["state"]

                    # Handle exit
                    if text == "0":
                        user_state[phone_number] = {"state": "MAIN_MENU"}
                        send_message(phone_number, get_main_menu(name))
                        continue

                    # MAIN MENU flow
                    if state == "MAIN_MENU":
                        if text == "1":
                            job_interest = user_state[phone_number].get("job_interest")
                            if job_interest:
                                send_message(
                                    phone_number,
                                    f"Last time you were looking for *{job_interest}* jobs.\n"
                                    "👉 Do you still want this, or would you like to change?\n"
                                    "Type a new job interest or 'same' to continue."
                                )
                            else:
                                send_message(phone_number, "Which type of job are you interested in?")
                            user_state[phone_number]["state"] = "JOBS"

                        elif text == "2":
                            training_interest = user_state[phone_number].get("training_interest")
                            if training_interest:
                                send_message(
                                    phone_number,
                                    f"Previously, you were exploring *{training_interest}* training.\n"
                                    "👉 Do you still want this, or would you like to change?\n"
                                    "Type a new training module or 'same' to continue."
                                )
                            else:
                                send_message(phone_number, "Which training module would you like to explore?")
                            user_state[phone_number]["state"] = "TRAINING"

                        elif text == "3":
                            mentorship_interest = user_state[phone_number].get("mentorship_interest")
                            if mentorship_interest:
                                send_message(
                                    phone_number,
                                    f"Previously, you were interested in mentorship around *{mentorship_interest}*.\n"
                                    "👉 Do you still want this, or would you like to change?\n"
                                    "Type a new mentorship area or 'same' to continue."
                                )
                            else:
                                send_message(phone_number, "Which mentorship area are you interested in?")
                            user_state[phone_number]["state"] = "MENTORSHIP"

                        elif text == "4":
                            micro_interest = user_state[phone_number].get("micro_interest")
                            if micro_interest:
                                send_message(
                                    phone_number,
                                    f"Previously, you wanted to explore *{micro_interest}* micro-business opportunities.\n"
                                    "👉 Do you still want this, or would you like to change?\n"
                                    "Type a new business idea or 'same' to continue."
                                )
                            else:
                                send_message(phone_number, "Which type of micro-entrepreneurship are you interested in?")
                            user_state[phone_number]["state"] = "MICRO"

                        else:
                            send_message(phone_number, "Invalid option. Please choose 1-4 or 0 to Exit.")

                    # JOBS flow
                    elif state == "JOBS":
                        if text.lower() == "same" and user_state[phone_number].get("job_interest"):
                            job_interest = user_state[phone_number]["job_interest"]
                            send_message(phone_number, f"Here are the latest *{job_interest}* job listings:\n👉 https://mock-jobs.com/{job_interest}")
                        else:
                            user_state[phone_number]["job_interest"] = text
                            send_message(phone_number, f"Got it! We'll track *{text}* jobs for you.\n👉 https://mock-jobs.com/{text}")
                        user_state[phone_number]["state"] = "MAIN_MENU"
                        send_message(phone_number, get_main_menu(name))

                    # TRAINING flow
                    elif state == "TRAINING":
                        if text.lower() == "same" and user_state[phone_number].get("training_interest"):
                            training_interest = user_state[phone_number]["training_interest"]
                            send_message(phone_number, f"Continuing with *{training_interest}* training.\n👉 https://mock-training.com/{training_interest}")
                        else:
                            user_state[phone_number]["training_interest"] = text
                            send_message(phone_number, f"Great! Explore *{text}* training here:\n👉 https://mock-training.com/{text}")
                        user_state[phone_number]["state"] = "MAIN_MENU"
                        send_message(phone_number, get_main_menu(name))

                    # MENTORSHIP flow
                    elif state == "MENTORSHIP":
                        if text.lower() == "same" and user_state[phone_number].get("mentorship_interest"):
                            mentorship_interest = user_state[phone_number]["mentorship_interest"]
                            send_message(phone_number, f"Connecting you with mentors in *{mentorship_interest}*.\n👉 https://mock-mentorship.com/{mentorship_interest}")
                        else:
                            user_state[phone_number]["mentorship_interest"] = text
                            send_message(phone_number, f"Awesome! Mentorship in *{text}* is available here:\n👉 https://mock-mentorship.com/{text}")
                        user_state[phone_number]["state"] = "MAIN_MENU"
                        send_message(phone_number, get_main_menu(name))

                    # MICRO flow
                    elif state == "MICRO":
                        if text.lower() == "same" and user_state[phone_number].get("micro_interest"):
                            micro_interest = user_state[phone_number]["micro_interest"]
                            send_message(phone_number, f"Here are some opportunities in *{micro_interest}* micro-entrepreneurship:\n👉 https://mock-micro.com/{micro_interest}")
                        else:
                            user_state[phone_number]["micro_interest"] = text
                            send_message(phone_number, f"Excellent! Explore *{text}* micro-entrepreneurship here:\n👉 https://mock-micro.com/{text}")
                        user_state[phone_number]["state"] = "MAIN_MENU"
                        send_message(phone_number, get_main_menu(name))

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
