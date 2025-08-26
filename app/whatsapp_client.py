# app/whatsapp_client.py
import httpx
import logging
from .config import settings

logger = logging.getLogger(__name__)

async def send_whatsapp_message(to: str, message: str):
    """
    Sends a text message to a user via the WhatsApp Graph API.
    """
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

    async with httpx.AsyncClient() as client:
        try:
            # Use the GRAPH_API_URL directly from the settings object
            response = await client.post(settings.GRAPH_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"Message sent to {to}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error sending message: {e.response.text}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending message: {str(e)}")
