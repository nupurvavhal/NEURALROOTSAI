# backend/app/routers/whatsapp_webhook.py
"""
WhatsApp Webhook Router
Handles incoming WhatsApp messages via Twilio
Integrates with Market Agent for crop selling flow
Includes Weather Alerts and Precautions
"""

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict, List
from datetime import datetime
import traceback

from app.core.database import get_database
from app.agents.market_agent import handle_market_conversation
from app.services.twilio_client import send_whatsapp_message
from app.agents.weather_agent import predict_weather_for_farmer, CROP_WEATHER_SENSITIVITY
from app.services.weather_api import get_weather_by_city, get_forecast_by_city, MAHARASHTRA_LOCATIONS

router = APIRouter()

print("🚀 WhatsApp webhook router loaded!")


# ============================================================================
# WEATHER HELPER FUNCTIONS
# ============================================================================

async def get_weather_update_for_whatsapp(location: str, crops: List[str] = None) -> str:
    """
    Generate a WhatsApp-formatted weather update with precautions
    """
    try:
        # Default crops if none specified
        if not crops:
            crops = ["tomatoes", "onions", "potatoes"]
        
        # Get weather prediction
        prediction = await predict_weather_for_farmer(
            farmer_id="whatsapp_user",
            farmer_name="Farmer",
            location=location,
            crops=crops
        )
        
        # Format current weather
        weather_msg = f"""🌤️ *WEATHER UPDATE - {prediction.location.upper()}*
━━━━━━━━━━━━━━━━━━

🌡️ *Current Conditions:*
• Temperature: *{prediction.current_temp}°C*
• Humidity: *{prediction.current_humidity}%*
• Sky: {prediction.current_conditions.title()}

📊 *Risk Level: {prediction.overall_risk.upper()}* {'🔴' if prediction.overall_risk == 'critical' else '🟠' if prediction.overall_risk == 'high' else '🟡' if prediction.overall_risk == 'medium' else '🟢'}
"""

        # Add alerts if any
        if prediction.alerts:
            weather_msg += "\n⚠️ *WEATHER ALERTS:*\n"
            for alert in prediction.alerts[:3]:  # Max 3 alerts
                severity_emoji = "🔴" if alert.severity == "critical" else "🟠" if alert.severity == "high" else "🟡"
                weather_msg += f"{severity_emoji} {alert.title}\n"
                weather_msg += f"   {alert.message}\n"
                weather_msg += f"   ⏰ Expected: {alert.expected_time}\n\n"
        
        # Add crop-specific precautions
        if prediction.crop_precautions:
            weather_msg += "\n🌾 *CROP PRECAUTIONS:*\n"
            for precaution in prediction.crop_precautions[:3]:
                risk_emoji = "🔴" if precaution.risk_level == "high" else "🟡" if precaution.risk_level == "medium" else "🟢"
                weather_msg += f"\n{risk_emoji} *{precaution.crop_name}* ({precaution.risk_level} risk)\n"
                for p in precaution.precautions[:2]:
                    weather_msg += f"   ✅ {p}\n"
                if precaution.harvest_recommendation:
                    weather_msg += f"   🚨 {precaution.harvest_recommendation}\n"
        
        # Add immediate actions
        if prediction.immediate_actions and prediction.immediate_actions[0] != "No immediate actions required":
            weather_msg += "\n⚡ *IMMEDIATE ACTIONS:*\n"
            for action in prediction.immediate_actions[:3]:
                weather_msg += f"• {action}\n"
        
        # Add next 24h actions
        if prediction.next_24h_actions and prediction.next_24h_actions[0] != "Continue regular farming practices":
            weather_msg += "\n📅 *NEXT 24 HOURS:*\n"
            for action in prediction.next_24h_actions[:3]:
                weather_msg += f"• {action}\n"
        
        # Footer with forecast summary
        weather_msg += f"""
━━━━━━━━━━━━━━━━━━
📝 *Summary:* {prediction.forecast_summary}

_Reply 'weather' for updates anytime_
_Reply 'sell' to sell your crops_"""

        return weather_msg
        
    except Exception as e:
        print(f"❌ Weather update error: {e}")
        traceback.print_exc()
        return f"""🌤️ *Weather Update - {location}*

⚠️ Unable to fetch detailed weather data.

*General Precautions:*
• Monitor local weather news
• Keep crops covered if rain expected
• Water crops during morning/evening
• Check drainage systems

_Try again later for full forecast_
_Reply 'sell' to sell your crops_"""


async def get_quick_weather(location: str) -> str:
    """Get a quick weather summary"""
    try:
        current = await get_weather_by_city(location)
        if current:
            emoji = "🌧️" if "rain" in current.weather_main.lower() else "☀️" if "clear" in current.weather_main.lower() else "⛅"
            return f"""{emoji} *{location.title()} - Now*

🌡️ {current.temperature}°C (feels like {current.feels_like}°C)
💧 Humidity: {current.humidity}%
💨 Wind: {current.wind_speed} m/s
🌥️ {current.weather_description.title()}

_Reply 'weather details' for full forecast_"""
        else:
            return f"❌ Could not fetch weather for {location}. Try: Pune, Mumbai, Nashik, etc."
    except Exception as e:
        return f"❌ Weather service error. Please try again."

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
    
    # ========================================
    # WEATHER COMMANDS - Check first
    # ========================================
    weather_keywords = ["weather", "mausam", "barish", "rain", "forecast", "climate", "temperature", "temp"]
    
    if any(kw in message_lower for kw in weather_keywords):
        # Check if they specified a location
        location = state.get("village", "Pune")  # Default to saved village or Pune
        
        # Try to extract location from message
        for loc in MAHARASHTRA_LOCATIONS.keys():
            if loc in message_lower:
                location = loc.title()
                break
        
        # Check for quick weather vs detailed
        if "detail" in message_lower or "full" in message_lower:
            crops = state.get("crops", ["tomatoes", "onions"])
            return await get_weather_update_for_whatsapp(location, crops)
        else:
            # Return quick weather + offer detailed
            quick = await get_quick_weather(location)
            quick += "\n\n📋 *For detailed forecast with precautions, reply:*\n_'weather details'_ or _'weather pune'_"
            return quick
    
    # Start keywords
    start_keywords = ["sell", "mandi", "market", "price", "hi", "hello", "start"]
    
    if any(kw in message_lower for kw in start_keywords) or state["step"] == "idle":
        # Check if this farmer already has a name saved
        if state.get("farmer_name"):
            # Returning farmer - go to crop selection
            MEMORY_STATE[clean_phone] = {**state, "step": "awaiting_crop"}
            return f"""🙏 Welcome back, *{state['farmer_name']}*!

*What would you like to do today?*

🌾 *SELL CROPS* - Reply 'sell'
🌤️ *WEATHER UPDATE* - Reply 'weather'

━━━━━━━━━━━━━━━

Or select a crop to sell:

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

I'm your agricultural assistant. I help farmers:
• 🌾 Sell crops at the best prices
• 🌤️ Get weather updates & precautions
• 🚛 Book transport to mandis

Let me register you first.

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

You're now registered in our network!

━━━━━━━━━━━━━━━

*What would you like to do?*

🌾 *SELL CROPS* - Reply 'sell' or select below
🌤️ *WEATHER UPDATE* - Reply 'weather'

━━━━━━━━━━━━━━━

*Select a crop to sell:*

1. Tomatoes
2. Onions
3. Potatoes
4. Bananas
5. Grapes
6. Mangoes
7. Other (type name)

*Reply with the crop name or number*
_Or type 'weather' for weather updates_"""

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
        return """🙏 Welcome to *Neural Roots*!

*Available Commands:*
🌾 Reply *'sell'* - Sell your crops
🌤️ Reply *'weather'* - Get weather updates
📊 Reply *'price'* - Check mandi prices

_What would you like to do?_"""


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
        
        # ========================================
        # CHECK FOR WEATHER COMMANDS FIRST
        # ========================================
        message_lower = Body.strip().lower()
        weather_keywords = ["weather", "mausam", "barish", "rain", "forecast", "climate", "temperature", "temp"]
        
        if any(kw in message_lower for kw in weather_keywords):
            print(f"   🌤️ Weather command detected!")
            
            # Get farmer's saved location from memory or default
            farmer_state = MEMORY_STATE.get(clean_number, {})
            location = farmer_state.get("village", "Pune")
            if "," in location:
                location = location.split(",")[0].strip()
            
            # Try to extract location from message
            for loc in MAHARASHTRA_LOCATIONS.keys():
                if loc in message_lower:
                    location = loc.title()
                    break
            
            print(f"   📍 Location: {location}")
            
            # Check for quick weather vs detailed
            if "detail" in message_lower or "full" in message_lower:
                crops = farmer_state.get("crops", ["tomatoes", "onions"])
                response_message = await get_weather_update_for_whatsapp(location, crops)
            else:
                # Return quick weather + offer detailed
                response_message = await get_quick_weather(location)
                response_message += "\n\n📋 *For detailed forecast with precautions, reply:*\n_'weather details'_ or _'weather pune'_"
            
            print(f"   ✅ Weather response generated")
        
        elif db_available:
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


# ============================================================================
# WEATHER ALERT ENDPOINTS
# ============================================================================

@router.post("/weather-alert")
async def send_weather_alert(
    to_number: str,
    location: str = "Pune",
    crops: Optional[str] = None  # Comma-separated crops
):
    """
    Send a weather alert with precautions to a specific farmer
    
    Example: /weather-alert?to_number=+919999999999&location=Nashik&crops=tomatoes,onions
    """
    crop_list = crops.split(",") if crops else ["tomatoes", "onions"]
    crop_list = [c.strip() for c in crop_list]
    
    weather_msg = await get_weather_update_for_whatsapp(location, crop_list)
    result = send_whatsapp_message(to_number, weather_msg)
    
    if result:
        return {"success": True, "message_sid": result, "location": location, "crops": crop_list}
    else:
        return {"success": False, "error": "Failed to send weather alert"}


@router.post("/broadcast-weather-alerts")
async def broadcast_weather_alerts():
    """
    Send weather alerts to all registered farmers based on their location and crops
    This can be triggered by a cron job or manual API call
    """
    sent_count = 0
    failed_count = 0
    results = []
    
    try:
        db = get_database()
        
        # Get all farmers from database
        farmers = await db["farmers"].find().to_list(length=100)
        
        for farmer in farmers:
            phone = farmer.get("phone") or farmer.get("whatsapp_number")
            if not phone:
                continue
                
            location = farmer.get("location", farmer.get("village", "Pune"))
            crops = farmer.get("crops", ["tomatoes", "onions"])
            
            try:
                weather_msg = await get_weather_update_for_whatsapp(location, crops)
                result = send_whatsapp_message(phone, weather_msg)
                
                if result:
                    sent_count += 1
                    results.append({"phone": phone, "status": "sent", "sid": result})
                else:
                    failed_count += 1
                    results.append({"phone": phone, "status": "failed"})
            except Exception as e:
                failed_count += 1
                results.append({"phone": phone, "status": "error", "error": str(e)})
        
        # Also send to in-memory registered users
        for phone, state in MEMORY_STATE.items():
            if state.get("farmer_name"):
                full_phone = f"+91{phone}" if not phone.startswith("+") else phone
                location = state.get("village", "Pune").split(",")[0]
                crops = state.get("crops", ["tomatoes", "onions"])
                
                try:
                    weather_msg = await get_weather_update_for_whatsapp(location, crops)
                    result = send_whatsapp_message(full_phone, weather_msg)
                    
                    if result:
                        sent_count += 1
                        results.append({"phone": full_phone, "status": "sent", "sid": result})
                except Exception as e:
                    pass
        
        return {
            "success": True,
            "sent": sent_count,
            "failed": failed_count,
            "details": results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "sent": sent_count}


@router.get("/weather/{location}")
async def get_weather_for_location(
    location: str,
    crops: Optional[str] = None
):
    """
    Get formatted weather update for a location (preview without sending)
    
    Example: /weather/pune?crops=tomatoes,onions
    """
    crop_list = crops.split(",") if crops else ["tomatoes", "onions"]
    crop_list = [c.strip() for c in crop_list]
    
    weather_msg = await get_weather_update_for_whatsapp(location, crop_list)
    
    return {
        "location": location,
        "crops": crop_list,
        "message": weather_msg,
        "message_length": len(weather_msg)
    }