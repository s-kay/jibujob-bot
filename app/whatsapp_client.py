import httpx
import logging
from app.config import settings
import asyncio

# A temporary in-memory store for web replies.
# In a real production web app, you would use a more robust system like WebSockets.
WEB_REPLIES = {}

async def send_whatsapp_message(to: str, message: str):
    """
    Sends a message. If the recipient 'to' starts with 'web-', it stores the
    message for the web client to retrieve. Otherwise, it sends to WhatsApp.
    """
    if to.startswith("web-"):
        if to not in WEB_REPLIES:
            WEB_REPLIES[to] = []
        WEB_REPLIES[to].append(message)
        logging.info(f"Stored web reply for {to}: {message}")
        return

    # Original WhatsApp sending logic
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }
    
    url = f"https://graph.facebook.com/v{settings.GRAPH_API_VERSION}/{settings.WHATSAPP_PHONE_ID}/messages"

    async with httpx.AsyncClient() as client:
        try:
            # Split long messages into chunks
            if len(message) > 4096:
                chunks = [message[i:i+4096] for i in range(0, len(message), 4096)]
                for i, chunk in enumerate(chunks):
                    chunk_payload = payload.copy()
                    chunk_payload["text"]["body"] = f"({i+1}/{len(chunks)})\n{chunk}"
                    await client.post(url, headers=headers, json=chunk_payload, timeout=20)
                    await asyncio.sleep(1) # Small delay between chunks
            else:
                response = await client.post(url, headers=headers, json=payload, timeout=20)
                response.raise_for_status()
            
            logging.info(f"Message sent to {to}")
        except httpx.HTTPStatusError as e:
            logging.error(f"Error sending message: {e.response.text}")
        except Exception as e:
            logging.error(f"Unexpected error in send_whatsapp_message: {str(e)}")

