import os
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN") or ""
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or ""
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "jibujob-verify"
DATABASE_URL = os.getenv("DATABASE_URL") or ""
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v19.0")
