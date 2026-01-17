# backend/app/models/schemas.py
from pydantic import BaseModel
from typing import Optional

class IoTDataSchema(BaseModel):
    farmer_id: str          # e.g., "919999999999" (Phone number acting as ID)
    temperature: float      # e.g., 28.5
    humidity: float         # e.g., 65.0
    image_url: str          # URL from Firebase/S3 (We will simulate this for now)
    timestamp: Optional[str] = None