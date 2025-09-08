import logging
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from . import models, crud, services, whatsapp_client
from .database import engine, get_db
from .config import settings
from pydantic import BaseModel, Field

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="KaziLeo WhatsApp Bot")

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
    statuses: Optional[List[Any]] = None # To handle status updates

class Change(BaseModel):
    value: Value
    field: str

class Entry(BaseModel):
    id: str
    changes: List[Change]

class WebhookRequest(BaseModel):
    object: str
    entry: List[Entry]


@app.get("/", response_class=FileResponse, include_in_schema=False)
def read_root():
    return "index.html"

@app.post("/webchat", tags=["Web Pilot"])
async def handle_webchat(request: Request, db: Session = Depends(get_db)):
    """Endpoint for the web pilot to send messages."""
    data = await request.json()
    user_input = data.get("message", "")
    session_id = data.get("session_id", "web-default")
    
    session, is_new = crud.get_or_create_session(db, phone_number=session_id, user_name="Friend")
    await services.process_message(db, session, user_input, is_new_user=is_new)
    crud.update_session(db, session)
    
    replies = await whatsapp_client.get_mock_replies()
    return {"replies": replies}

@app.get("/webhook", tags=["WhatsApp"])
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

@app.post("/webhook", tags=["WhatsApp"])
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

            session, is_new = crud.get_or_create_session(db, phone_number=from_number, user_name=user_name)
            await services.process_message(db, session, message_text, is_new_user=is_new)
            crud.update_session(db, session)
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
    
    return Response(status_code=200)

