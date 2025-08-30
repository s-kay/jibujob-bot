import logging
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

# Import modules from our application structure
from . import models, crud, services, whatsapp_client
from .database import engine, get_db
from .config import settings
from pydantic import BaseModel, Field

models.Base.metadata.create_all(bind=engine)

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
@app.get("/", response_class=FileResponse)
def read_root():
    return "index.html"

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
        change = request.entry[0].changes[0]
        value = change.value

        if value.messages and value.contacts:
            message = value.messages[0]
            contact = value.contacts[0]
            
            from_number = message.from_number
            user_name = contact.profile.name
            message_text = message.text.body if message.text else ""

            # Clear any old replies for this user
            if from_number in whatsapp_client.WEB_REPLIES:
                whatsapp_client.WEB_REPLIES.pop(from_number)

            session, is_new = crud.get_or_create_session(db, phone_number=from_number, user_name=user_name)
            await services.process_message(db, session, message_text, is_new_user=is_new)
            crud.update_session(db, session)

            # --- THE FIX FOR THE WEB ---
            # If this was a web user, retrieve and return the stored replies
            if from_number.startswith("web-"):
                replies = whatsapp_client.WEB_REPLIES.pop(from_number, [])
                return JSONResponse(content={"replies": replies})

    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
    
    # For regular WhatsApp messages, just return OK
    return Response(status_code=200)

