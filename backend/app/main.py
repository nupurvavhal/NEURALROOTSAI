# backend/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import connect_to_mongo, close_mongo_connection  
from app.routers import whatsapp_webhook,iot_ingest

# Lifecycle Manager (Connect DB on startup)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan, title="Neural Roots AI Backend")

# Register the WhatsApp router
app.include_router(whatsapp_webhook.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(iot_ingest.router, prefix="/api/iot", tags=["IoT"])

@app.get("/")
def health_check():
    return {"status": "Neural Roots System Operational 🚀"}