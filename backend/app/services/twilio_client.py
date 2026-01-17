# backend/app/services/twilio_client.py
import traceback
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.core.config import settings

print(f"🔧 TWILIO CONFIG CHECK:")
print(f"   - Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}...")
print(f"   - Auth Token: {settings.TWILIO_AUTH_TOKEN[:5]}...")
print(f"   - WhatsApp Number: {settings.TWILIO_WHATSAPP_NUMBER}")

try:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    print(f"✅ Twilio client initialized successfully")
except Exception as e:
    print(f"❌ TWILIO CLIENT INIT ERROR: {e}")
    client = None

def send_whatsapp_message(to_number: str, body_text: str):
    """
    Sends a WhatsApp message to the farmer.
    to_number: The farmer's number (e.g., 'whatsapp:+919999999999')
    """
    print(f"\n{'='*60}")
    print(f"📤 SENDING WHATSAPP MESSAGE")
    print(f"{'='*60}")
    print(f"   To: {to_number}")
    print(f"   Body: {body_text[:100]}..." if len(body_text) > 100 else f"   Body: {body_text}")
    print(f"   From: {settings.TWILIO_WHATSAPP_NUMBER}")
    
    if client is None:
        print(f"❌ ERROR: Twilio client is not initialized!")
        return None
    
    try:
        # Ensure the number has the 'whatsapp:' prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
            print(f"   Added whatsapp: prefix -> {to_number}")

        print(f"   Calling Twilio API...")
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            body=body_text,
            to=to_number
        )
        print(f"✅ MESSAGE SENT SUCCESSFULLY!")
        print(f"   SID: {message.sid}")
        print(f"   Status: {message.status}")
        print(f"   Error Code: {message.error_code}")
        print(f"   Error Message: {message.error_message}")
        return message.sid
    except TwilioRestException as e:
        print(f"❌ TWILIO REST EXCEPTION:")
        print(f"   Error Code: {e.code}")
        print(f"   Error Message: {e.msg}")
        print(f"   Status: {e.status}")
        print(f"   URI: {e.uri}")
        return None
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {e}")
        print(f"   Traceback:")
        traceback.print_exc()
        return None