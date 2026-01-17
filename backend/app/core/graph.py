# backend/app/core/graph.py
from app.services.twilio_client import send_whatsapp_message

async def run_workflow(farmer_id: str, event_type: str, data: dict = None):
    """
    The Central Brain (Stub). 
    Eventually, this will manage the state machine.
    """
    print(f"🧠 Brain Processing: {event_type} for {farmer_id}")
    
    if event_type == "WHATSAPP_REPLY":
        user_text = data.get("text", "")
        
        # SIMPLE ECHO TEST LOGIC
        if "hello" in user_text.lower():
            response = "Hello Farmer! Neural Roots AI is online. 🌱"
        elif "price" in user_text.lower():
            response = "Current Mandi Price: ₹40/kg. City Price: ₹65/kg."
        else:
            response = f"I received: '{user_text}'. Waiting for AI logic..."
        
        # Send the response back
        send_whatsapp_message(farmer_id, response)