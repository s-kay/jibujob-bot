# app/main.py
import logging
from fastapi import FastAPI, Request, Response, HTTPException, Depends
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
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "KaziLeo API is running."}

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
    Handles incoming messages from WhatsApp users.
    """
    try:
        # The webhook sends a list of entries, but we typically only care about the first one.
        if not request.entry or not request.entry[0].changes:
            logger.warning("Webhook received with no entries or changes.")
            return Response(status_code=200)

        change = request.entry[0].changes[0]
        value = change.value

        # ** THE FIX IS HERE: Check if the notification is a user message **
        if value.messages and value.contacts:
            message = value.messages[0]
            contact = value.contacts[0]

            # We only want to process incoming text messages for now
            if message.type != "text" or not message.text:
                logger.info(f"Received non-text message type: {message.type}")
                return Response(status_code=200)

            from_number = message.from_number
            user_name = contact.profile.name
            message_text = message.text.body

            # Get or create the user's session from the database
            session = crud.get_or_create_session(db, phone_number=from_number, user_name=user_name)

            # Pass the session and message to the business logic handler
            await services.process_message(db, session, message_text)
            
            # Commit any changes made to the session during processing
            crud.update_session(db, session)
        else:
            # This handles other events like message status updates (sent, delivered, read)
            logger.info(f"Received a non-message webhook event (e.g., status update).")

    except (IndexError, KeyError) as e:
        logger.warning(f"Could not parse webhook data: {e}. Payload: {request.dict()}")
    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
    
    # Always return 200 OK to WhatsApp to acknowledge receipt
    return Response(status_code=200)
