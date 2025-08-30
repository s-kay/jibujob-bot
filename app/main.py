# app/main.py
import logging
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

# Import modules from our application structure
from . import models, crud, services
from .database import engine, get_db
from .config import settings
from pydantic import BaseModel, Field

# --- Boilerplate: Create database tables on startup ---
models.Base.metadata.create_all(bind=engine)

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="KaziLeo WhatsApp Bot")

# --- Pydantic Models for WhatsApp Webhook Validation ---
# (These models define the structure of the incoming data from WhatsApp)
class TextMessage(BaseModel):
    body: str

class Message(BaseModel):
    id: str
    from_number: str = Field(..., alias='from')
    timestamp: str
    type: str
    text: Optional[TextMessage] = None

class Profile(BaseModel):
    name: str

class Contact(BaseModel):
    profile: Profile
    wa_id: str

class Value(BaseModel):
    messaging_product: str
    metadata: dict
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None

class Change(BaseModel):
    value: Value
    field: str

class Entry(BaseModel):
    id: str
    changes: List[Change]

class WebhookRequest(BaseModel):
    object: str
    entry: List[Entry]


# --- API Endpoints ---

@app.get("/", response_class=FileResponse)
def read_root():
    """
    Serves the main index.html file for the Web Pilot.
    """
    return "index.html"

@app.get("/webhook", tags=["Webhook"])
async def verify_webhook(request: Request):
    """
    Handles the webhook verification request from Meta.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.VERIFY_TOKEN:
        logger.info("Webhook verified successfully.")
        return Response(content=challenge, media_type="text/plain", status_code=200)
    else:
        logger.error("Webhook verification failed.")
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook", tags=["Webhook"])
async def handle_webhook(request: WebhookRequest, db: Session = Depends(get_db)):
    """
    Handles incoming messages from WhatsApp users or the Web Pilot.
    """
    try:
        if not request.entry or not request.entry[0].changes:
            logger.warning("Webhook received with no entries or changes.")
            return Response(status_code=200)

        change = request.entry[0].changes[0]
        value = change.value

        if value.messages and value.contacts:
            message = value.messages[0]
            contact = value.contacts[0]

            if message.type != "text" or not message.text:
                logger.info(f"Received non-text message type: {message.type}")
                return Response(status_code=200)

            from_number = message.from_number
            user_name = contact.profile.name
            message_text = message.text.body

            session, is_new = crud.get_or_create_session(db, phone_number=from_number, user_name=user_name)
            await services.process_message(db, session, message_text, is_new_user=is_new)
            crud.update_session(db, session)
        else:
            logger.info(f"Received a non-message webhook event (e.g., status update).")

    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
    
    return Response(status_code=200)