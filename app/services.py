import httpx
from config import WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, GRAPH_API_VERSION

API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_ID}/messages"
HEADERS = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}

async def send_whatsapp_text(to: str, body: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(API_URL, headers=HEADERS, json=payload)
        r.raise_for_status()
        return r.json()
