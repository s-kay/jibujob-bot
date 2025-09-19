# app/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Define the path to the .env file in the project root
env_path = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    """
    Manages application settings and environment variables.
    """
    # Database configuration
    DATABASE_URL: str = "sqlite:///./kazileo.db"


    # WhatsApp API configuration
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""
    VERIFY_TOKEN: str = ""
    GRAPH_API_URL: str = ""

    # External API Keys
    JOB_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None



    # Session timeout in minutes (e.g., 5 minutes)
    SESSION_TIMEOUT_MINUTES: int = 5

    # --- NEW SETTINGS FOR PARTNER DASHBOARD ---
    JWT_SECRET_KEY: str = "a_very_long_and_super_secret_string_for_jwt_tokens"
    JWT_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=env_path, extra='ignore')

# Create a single, importable instance of the settings
settings = Settings()
