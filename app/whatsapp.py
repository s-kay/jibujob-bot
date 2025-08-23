import requests
from app.config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, GRAPH_API_VERSION

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()
