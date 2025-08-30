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

    # External API Keys
    JOB_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Derived variable for the Graph API URL
    @property
    def GRAPH_API_URL(self) -> str:
        return f"https://graph.facebook.com/v22.0/{self.WHATSAPP_PHONE_ID}/messages"

    # Session timeout in minutes (e.g., 5 minutes)
    SESSION_TIMEOUT_MINUTES: int = 5

    model_config = SettingsConfigDict(env_file=env_path, extra='ignore')

# Create a single, importable instance of the settings
settings = Settings()
