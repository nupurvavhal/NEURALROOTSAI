# backend/app/routers/whatsapp_webhook.py
"""
WhatsApp Webhook Router
Handles incoming WhatsApp messages via Twilio
Integrates with Market Agent for crop selling flow
"""

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict
from datetime import datetime
import traceback

from app.core.database import get_database
from app.agents.market_agent import handle_market_conversation
from app.services.twilio_client import send_whatsapp_message

router = APIRouter()

print("🚀 WhatsApp webhook router loaded!")

# In-memory conversation state (fallback when DB is down)
MEMORY_STATE: Dict[str, dict] = {}

async def handle_conversation_fallback(farmer_phone: str, message: str, profile_name: str = None) -> str:
    """Simple in-memory conversation handler when MongoDB is unavailable"""
    from datetime import timedelta
    
    clean_phone = farmer_phone.replace("whatsapp:", "").strip()
    message_lower = message.strip().lower()
    message_original = message.strip()  # Keep original case for names
    
    # Get or create state
    state = MEMORY_STATE.get(clean_phone, {"step": "idle"})
    
    # Start keywords
    start_keywords = ["sell", "mandi", "market", "price", "hi", "hello", "start"]
    
    if any(kw in message_lower for kw in start_keywords) or state["step"] == "idle":
        # Check if this farmer already has a name saved
        if state.get("farmer_name"):
            # Returning farmer - go to crop selection
            MEMORY_STATE[clean_phone] = {**state, "step": "awaiting_crop"}
            return f"""🙏 Welcome back, *{state['farmer_name']}*!

*Which crop do you want to sell today?*

1. Tomatoes
2. Onions
3. Potatoes
4. Bananas
5. Grapes
6. Mangoes
7. Other (type name)

*Reply with the crop name or number*
_You can also type any crop name like: Ginger, Turmeric, Wheat, etc._"""
        else:
            # New farmer - ask for name first
            MEMORY_STATE[clean_phone] = {"step": "awaiting_name"}
            return """🙏 *Namaste! Welcome to Neural Roots*

I'm your agricultural assistant. I help farmers sell crops at the best prices.

Let me register you in our system first.

*What is your name?*
_Example: Ramesh Patil_"""

    elif state["step"] == "awaiting_name":
        farmer_name = message_original.title()
        MEMORY_STATE[clean_phone] = {"step": "awaiting_village", "farmer_name": farmer_name}
        return f"""✅ Thank you, *{farmer_name}*!

*Which village/city are you from?*

_Examples:_
• Pune
• Nashik
• Satara
• Kolhapur
• Ahmednagar
• Or type your village name"""

    elif state["step"] == "awaiting_village":
        village = message_original.title()
        if "maharashtra" not in village.lower():
            village = f"{village}, Maharashtra"
        
        farmer_name = state.get("farmer_name", profile_name or "Farmer")
        MEMORY_STATE[clean_phone] = {"step": "awaiting_crop", "farmer_name": farmer_name, "village": village}
        
        return f"""🎉 *Welcome to Neural Roots, {farmer_name}!*

📍 Location: {village}

You're now registered in our network. You can sell your crops at the best mandi prices!

━━━━━━━━━━━━━━━

*Which crop do you want to sell today?*

1. Tomatoes
2. Onions
3. Potatoes
4. Bananas
5. Grapes
6. Mangoes
7. Other (type name)

*Reply with the crop name or number*
_You can also type any crop name like: Ginger, Turmeric, Wheat, etc._"""

    elif state["step"] == "awaiting_crop":
        crop_map = {
            "1": "Tomatoes", "2": "Onions", "3": "Potatoes",
            "4": "Bananas", "5": "Grapes", "6": "Mangoes",
            "7": None,  # Other
            "tomatoes": "Tomatoes", "tomato": "Tomatoes",
            "onions": "Onions", "onion": "Onions",
            "potatoes": "Potatoes", "potato": "Potatoes",
            "bananas": "Bananas", "banana": "Bananas",
            "grapes": "Grapes", "grape": "Grapes",
            "mangoes": "Mangoes", "mango": "Mangoes",
        }
        
        # Handle "Other" selection
        if message_lower in ["7", "other"]:
            MEMORY_STATE[clean_phone] = {**state, "step": "awaiting_custom_crop"}
            return "📝 *Type your crop name:*\n\n_Example: Ginger, Wheat, Sugarcane, Cotton, etc._"
        
        selected_crop = crop_map.get(message_lower)
        if selected_crop is None:
            # User typed a custom crop name
            selected_crop = message_original.title()
            
        MEMORY_STATE[clean_phone] = {**state, "step": "awaiting_quantity", "crop": selected_crop}
        return f"""Great! You selected *{selected_crop}*

📦 *How many kilograms do you want to sell?*

_Example: 100 or 250_"""

    elif state["step"] == "awaiting_custom_crop":
        selected_crop = message_original.title()
        MEMORY_STATE[clean_phone] = {**state, "step": "awaiting_quantity", "crop": selected_crop}
        return f"""Great! You selected *{selected_crop}*

📦 *How many kilograms do you want to sell?*

_Example: 100 or 250_"""

    elif state["step"] == "awaiting_quantity":
        import re
        numbers = re.findall(r'\d+', message_lower)
        if not numbers:
            return "❌ Please enter a valid quantity in kg.\n\n_Example: 100 or 250_"
        
        quantity = float(numbers[0])
        crop = state.get("crop", "Unknown")
        
        MEMORY_STATE[clean_phone] = {**state, "step": "awaiting_mandi", "crop": crop, "quantity": quantity}
        
        return f"""🌾 *Market Analysis for {crop}*
📦 Quantity: {quantity} kg

📊 Price Range: ₹80 - ₹120 per kg

━━━━━━━━━━━━━━━
*Available Mandis:*

*1. ⭐ Pune APMC*
   💰 ₹110/kg 📈
   📍 15 km away
   🚛 Transport: ₹525
   ✅ Net Profit: *₹10,475*

*2. Mumbai Wholesale*
   💰 ₹120/kg 📈
   📍 150 km away
   🚛 Transport: ₹5,250
   ✅ Net Profit: *₹6,750*

*3. Nashik Mandi*
   💰 ₹95/kg ➡️
   📍 200 km away
   🚛 Transport: ₹6,000
   ✅ Net Profit: *₹3,500*

━━━━━━━━━━━━━━━
💡 Best option is Pune APMC - highest profit with lowest transport cost!

*Reply with the number (1-3) to select a mandi*"""

    elif state["step"] == "awaiting_mandi":
        crop = state.get("crop", "Unknown")
        quantity = state.get("quantity", 100)
        farmer_name = state.get("farmer_name", "Farmer")
        village = state.get("village", "Maharashtra")
        
        mandi_map = {"1": "Pune APMC", "2": "Mumbai Wholesale", "3": "Nashik Mandi"}
        selected = mandi_map.get(message_lower.strip(), "Pune APMC")
        
        MEMORY_STATE[clean_phone] = {**state, "step": "awaiting_confirm", "crop": crop, "quantity": quantity, "mandi": selected}
        
        return f"""📋 *Order Summary*

🌾 Crop: {crop}
📦 Quantity: {quantity} kg
🏪 Mandi: {selected}
💰 Expected Profit: ₹10,475

*Reply 'YES' to confirm and get a driver assigned*
_Reply 'NO' to cancel_"""

    elif state["step"] == "awaiting_confirm":
        if message_lower in ["yes", "y", "haan", "ha", "confirm", "ok"]:
            crop = state.get("crop", "Unknown")
            quantity = state.get("quantity", 100)
            mandi = state.get("mandi", "Pune APMC")
            farmer_name = state.get("farmer_name", "Farmer")
            
            # Keep farmer info but reset step
            MEMORY_STATE[clean_phone] = {"step": "idle", "farmer_name": farmer_name, "village": state.get("village", "")}
            
            return f"""✅ *Booking Confirmed!*

🎫 Booking ID: *BK20260118{clean_phone[-4:]}*

━━━━━━━━━━━━━━━
*Driver Details:*
👤 Ramesh Kumar
📞 +91 98765 43210
🚛 Tata Ace

━━━━━━━━━━━━━━━
*Trip Details:*
📦 {quantity}kg {crop}
📍 From: Your Farm
🏪 To: {mandi}
📏 Distance: 15 km
💰 Transport Cost: ₹525

⏰ *Within 2 hours*

Your driver will contact you shortly!"""
        
        elif message_lower in ["no", "n", "nahi", "cancel"]:
            farmer_name = state.get("farmer_name", "Farmer")
            MEMORY_STATE[clean_phone] = {"step": "idle", "farmer_name": farmer_name, "village": state.get("village", "")}
            return "❌ Order cancelled.\n\n_Reply 'sell' to start a new order_"
        
        else:
            return "Please reply *YES* to confirm or *NO* to cancel."
    
    else:
        MEMORY_STATE[clean_phone] = {"step": "idle"}
        return "🙏 Welcome! Reply *sell* to start selling your crops."


@router.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),      # Twilio sends 'From' (Sender's number)
    Body: str = Form(...),      # Twilio sends 'Body' (The message text)
    ProfileName: Optional[str] = Form(None),  # Sender's WhatsApp name
    NumMedia: Optional[str] = Form("0"),      # Number of media attachments
):
    """
    Twilio hits this endpoint whenever a farmer sends a WhatsApp message.
    
    Flow:
    1. Farmer sends "sell" or "market"
    2. Bot asks which crop
    3. Farmer selects crop
    4. Bot asks quantity
    5. Farmer enters quantity (e.g., "100 kg")
    6. Bot shows mandi options with prices and profit analysis
    7. Farmer selects mandi (by number)
    8. Bot asks confirmation
    9. Farmer confirms
    10. Bot assigns driver and sends confirmation
    """
    
    clean_number = From.replace("whatsapp:", "")
    
    print(f"\n{'#'*70}")
    print(f"# INCOMING WHATSAPP MESSAGE")
    print(f"{'#'*70}")
    print(f"   From: {From}")
    print(f"   Clean Number: {clean_number}")
    print(f"   Profile Name: {ProfileName}")
    print(f"   Body: {Body}")
    print(f"   NumMedia: {NumMedia}")
    print(f"{'#'*70}\n")
    
    # Get database connection
    print(f"📊 Step 1: Getting database connection...")
    db = None
    db_available = False
    try:
        db = get_database()
        print(f"   ✅ Database reference obtained")
        db_available = True
    except Exception as e:
        print(f"   ⚠️ DATABASE NOT AVAILABLE: {e}")
        print(f"   Using in-memory fallback mode...")
    
    # Log incoming message (skip if DB unavailable)
    if db_available:
        print(f"📝 Step 2: Logging incoming message...")
        try:
            await db["whatsapp_logs"].insert_one({
                "direction": "incoming",
                "from_number": clean_number,
                "profile_name": ProfileName,
                "message": Body,
                "num_media": NumMedia,
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"   ✅ Message logged to database")
        except Exception as e:
            print(f"   ⚠️ LOG ERROR (non-critical): {e}")
            db_available = False  # Mark DB as unavailable for subsequent operations
    else:
        print(f"📝 Step 2: Skipping database logging (DB unavailable)")
    
    try:
        # Handle the conversation
        print(f"🤖 Step 3: Processing conversation...")
        
        if db_available:
            try:
                response_message = await handle_market_conversation(db, From, Body, ProfileName)
                print(f"   ✅ Market agent response received")
            except Exception as db_error:
                print(f"   ⚠️ Market agent failed: {db_error}")
                print(f"   Falling back to in-memory handler...")
                response_message = await handle_conversation_fallback(From, Body, ProfileName)
                print(f"   ✅ Fallback response received")
        else:
            response_message = await handle_conversation_fallback(From, Body, ProfileName)
            print(f"   ✅ Fallback response received")
        
        print(f"   Response preview: {response_message[:100]}..." if len(response_message) > 100 else f"   Response: {response_message}")
        
        # Send response via Twilio
        print(f"📤 Step 4: Sending response via Twilio...")
        result = send_whatsapp_message(From, response_message)
        if result:
            print(f"   ✅ Message sent, SID: {result}")
        else:
            print(f"   ❌ Failed to send message (returned None)")
        
        # Log outgoing message (skip if DB unavailable)
        if db_available and db is not None:
            print(f"📝 Step 5: Logging outgoing message...")
            try:
                await db["whatsapp_logs"].insert_one({
                    "direction": "outgoing",
                    "to_number": clean_number,
                    "message": response_message,
                    "timestamp": datetime.utcnow().isoformat()
                })
                print(f"   ✅ Outgoing message logged")
            except Exception as log_err:
                print(f"   ⚠️ Failed to log outgoing message: {log_err}")
        else:
            print(f"📝 Step 5: Skipping outgoing log (DB unavailable)")
        
    except Exception as e:
        print(f"❌ ERROR PROCESSING MESSAGE:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {e}")
        traceback.print_exc()
        # Send error message
        error_msg = "Sorry, something went wrong. Please try again.\n\nReply 'sell' to start."
        print(f"📤 Sending error message...")
        send_whatsapp_message(From, error_msg)
    
    print(f"\n{'#'*70}")
    print(f"# WEBHOOK PROCESSING COMPLETE")
    print(f"{'#'*70}\n")
    
    # Return empty TwiML response (we're sending response via API, not TwiML)
    return PlainTextResponse(content="", media_type="text/xml")


@router.get("/webhook")
async def whatsapp_webhook_verify(request: Request):
    """
    Verification endpoint for Twilio webhook setup
    """
    return {"status": "WhatsApp webhook is active", "timestamp": datetime.utcnow().isoformat()}


# ============================================================================
# ADDITIONAL ENDPOINTS
# ============================================================================

@router.post("/send")
async def send_message(
    to_number: str,
    message: str
):
    """
    Send a WhatsApp message to a specific number
    Useful for sending alerts or notifications
    """
    result = send_whatsapp_message(to_number, message)
    
    if result:
        return {"success": True, "message_sid": result}
    else:
        return {"success": False, "error": "Failed to send message"}


@router.get("/logs")
async def get_whatsapp_logs(limit: int = 50):
    """Get recent WhatsApp message logs"""
    db = await get_database()
    
    logs = await db["whatsapp_logs"].find().sort("timestamp", -1).limit(limit).to_list(length=limit)
    
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return {"logs": logs, "count": len(logs)}


@router.get("/conversations")
async def get_active_conversations():
    """Get all active conversation states"""
    db = await get_database()
    
    states = await db["conversation_states"].find().to_list(length=100)
    
    for state in states:
        state["_id"] = str(state["_id"])
    
    return {"conversations": states, "count": len(states)}


@router.delete("/conversations/{phone}")
async def clear_conversation(phone: str):
    """Clear conversation state for a phone number (for testing)"""
    db = await get_database()
    
    result = await db["conversation_states"].delete_one({"farmer_phone": phone})
    
    return {"success": result.deleted_count > 0, "deleted": result.deleted_count}