# app/main.py
import logging
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, crud, services
from .database import engine, get_db
from app.config import settings
from pydantic import BaseModel, Field

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="KaziLeo WhatsApp Bot")

# --- Pydantic Models for Webhook Validation ---
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
    try:
        if not request.entry or not request.entry[0].changes:
            return Response(status_code=200)

        change = request.entry[0].changes[0]
        value = change.value

        if value.messages and value.contacts:
            message = value.messages[0]
            contact = value.contacts[0]

            if message.type != "text" or not message.text:
                return Response(status_code=200)

            from_number = message.from_number
            user_name = contact.profile.name
            message_text = message.text.body

            # Get session and is_new flag
            session, is_new = crud.get_or_create_session(db, phone_number=from_number, user_name=user_name)

            # Pass both to the business logic handler
            await services.process_message(db, session, message_text, is_new_user=is_new)
            
            crud.update_session(db, session)
        else:
            logger.info("Received a non-message webhook event.")

    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
    
    return Response(status_code=200)
