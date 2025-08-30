# app/whatsapp_client.py
import httpx
import logging
from .config import settings

logger = logging.getLogger(__name__)

# WhatsApp's character limit for a single message
CHAR_LIMIT = 4096

# Global flag to control behavior for local testing
MOCK_MODE = False

async def send_whatsapp_message(to: str, message: str):
    """
    Sends a message. If MOCK_MODE is True, it prints to the console.
    Otherwise, it sends a real WhatsApp message.
    """
    # If we are in mock mode for local testing, just print the output.
    if MOCK_MODE:
        message_chunks = [message[i:i + CHAR_LIMIT] for i in range(0, len(message), CHAR_LIMIT)]
        for chunk in message_chunks:
            print(chunk)
        return

    # --- This is the original code for sending a real message ---
    message_chunks = [message[i:i + CHAR_LIMIT] for i in range(0, len(message), CHAR_LIMIT)]

    for chunk in message_chunks:
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": chunk},
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(settings.GRAPH_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                logger.info(f"Message chunk sent to {to}")
            except httpx.HTTPStatusError as e:
                logger.error(f"Error sending message chunk: {e.response.text}")
            except Exception as e:
                logger.error(f"An unexpected error occurred while sending message chunk: {str(e)}")
