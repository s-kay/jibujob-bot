from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from config import VERIFY_TOKEN
from services import send_whatsapp_text
from session_manager import get_or_create_session, save_session
from bot_logic import decide_reply

router = APIRouter()

# GET /webhook — verification handshake
@router.get("/webhook")
async def verify_webhook(request: Request):
    qp = request.query_params
    if qp.get("hub.mode") == "subscribe" and qp.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(content=qp.get("hub.challenge", ""))
    return PlainTextResponse(content="Verification failed", status_code=403)

# POST /webhook — incoming events
@router.post("/webhook")
async def incoming_webhook(request: Request):
    body = await request.json()
    try:
        # WhatsApp sends many event shapes; guard everything
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                # Only act on messages; ignore statuses/etc.
                for msg in value.get("messages", []):
                    wa_id = msg.get("from")                  # "2547xxxxxxx"
                    text  = (msg.get("text") or {}).get("body", "")

                    if not wa_id:
                        continue

                    sess = get_or_create_session(wa_id)
                    new_state, reply, new_data = decide_reply(sess, text)
                    sess.state, sess.data = new_state, new_data
                    save_session(sess)

                    await send_whatsapp_text(wa_id, reply)

    except Exception as e:
        # Log, but never break webhook contract
        print("Webhook error:", e)

    return JSONResponse({"status": "ok"})
