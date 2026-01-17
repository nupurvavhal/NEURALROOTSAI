# backend/app/routers/whatsapp.py
from fastapi import APIRouter, Form, Request
# We import the run_workflow stub (we will create this next)
from app.core.graph import run_workflow 

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),  # Twilio sends 'From' (Sender's number)
    Body: str = Form(...)   # Twilio sends 'Body' (The message text)
):
    """
    Twilio hits this endpoint whenever a farmer sends a message.
    """
    clean_number = From.replace("whatsapp:", "")
    print(f"📩 Received message from {clean_number}: {Body}")

    # Trigger the AI Brain logic
    # We pass 'WHATSAPP_REPLY' as the event type
    await run_workflow(
        farmer_id=clean_number, 
        event_type="WHATSAPP_REPLY", 
        data={"text": Body}
    )

    return {"status": "received"}