# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Neural Roots AI"
    
    # Twilio Settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str  

    class Config:
        env_file = ".env"
        extra="ignore"

settings = Settings()