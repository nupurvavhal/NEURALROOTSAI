# backend/app/services/twilio_client.py
from twilio.rest import Client
from app.core.config import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to_number: str, body_text: str):
    """
    Sends a WhatsApp message to the farmer.
    to_number: The farmer's number (e.g., 'whatsapp:+919999999999')
    """
    try:
        # Ensure the number has the 'whatsapp:' prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            body=body_text,
            to=to_number
        )
        print(f"✅ Message sent to {to_number}: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return None