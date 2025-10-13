import httpx
import logging
from app.config import settings
import asyncio
from typing import List, Dict, Any

# This list is used by the web pilot to pass messages back
mock_replies = []

async def send_whatsapp_message(to: str, message: str):
    """
    Sends a free-form text message. Used for replies inside the 24-hour window.
    """
    global mock_replies
    # THE FIX IS HERE: Changed "cli-" to "cli_" to match the test script.
    is_mock_user = to.startswith("web-") or to.startswith("cli_")

    if is_mock_user:
        if to.startswith("cli_") or to.startswith("web-"):
            print(f"\nKaziLeo:\n{message}")
        mock_replies.append(message)
        return

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp", "to": to, "type": "text",
        "text": {"body": message},
    }
    url = f"https://graph.facebook.com/{settings.GRAPH_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            response.raise_for_status()
            logging.info(f"Message sent to {to}")
        except httpx.HTTPStatusError as e:
            logging.error(f"Error sending message: {e.response.text}")
        except Exception as e:
            logging.error(f"Unexpected error in whatsapp_client: {str(e)}", exc_info=True)


async def send_template_message(to: str, template_name: str, components: List[Dict[str, Any]]):
    """
    Sends a pre-approved WhatsApp message template.
    Used for proactive notifications outside the 24-hour window.
    """
    # In test/mock mode, we just format the template for printing
    # THE FIX IS HERE: Changed "cli-" to "cli_" to match the test script.
    is_mock_user = to.startswith("web-") or to.startswith("cli_")
    if is_mock_user:
        formatted_params = [p['text'] for c in components if c['type'] == 'body' for p in c['parameters']]
        mock_message = f"[TEMPLATE: {template_name}] with params: {formatted_params}"
        print(f"\nKaziLeo:\n{mock_message}")
        return

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": components
        }
    }
    url = f"https://graph.facebook.com/{settings.GRAPH_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            response.raise_for_status()
            logging.info(f"Template message '{template_name}' sent to {to}")
        except httpx.HTTPStatusError as e:
            logging.error(f"Error sending template message: {e.response.text}")
        except Exception as e:
            logging.error(f"Unexpected error in whatsapp_client (template): {str(e)}", exc_info=True)


async def get_mock_replies():
    """Returns all stored mock replies and then clears the list."""
    global mock_replies
    await asyncio.sleep(0.1) 
    replies = list(mock_replies)
    mock_replies.clear()
    return replies

