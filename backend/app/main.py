# backend/main.py
from fastapi import FastAPI
from app.routers import whatsapp_webhook

app = FastAPI(title="Neural Roots AI Backend")

# Register the WhatsApp router
app.include_router(whatsapp_webhook.router, prefix="/api/whatsapp", tags=["WhatsApp"])

@app.get("/")
def health_check():
    return {"status": "Neural Roots System Operational 🚀"}