# backend/app/core/graph.py
from app.services.twilio_client import send_whatsapp_message

# Temperature thresholds for alerts
TEMP_HIGH_THRESHOLD = 35.0  # °C - Spoilage risk
TEMP_LOW_THRESHOLD = 5.0    # °C - Cold damage risk
HUMIDITY_HIGH_THRESHOLD = 85.0  # % - Mold risk

async def run_workflow(farmer_id: str, event_type: str, data: dict = None):
    """
    The Central Brain (Stub). 
    Eventually, this will manage the state machine.
    """
    print(f"🧠 Brain Processing: {event_type} for {farmer_id}")
    
    if event_type == "IOT_DATA_RECEIVED":
        # Process sensor data from ESP32
        temp = data.get("temperature", 0)
        hum = data.get("humidity", 0)
        device_id = data.get("device_id", farmer_id)
        
        print(f"📊 Sensor Analysis: Temp={temp}°C, Humidity={hum}%")
        
        # Check for alerts
        alerts = []
        if temp > TEMP_HIGH_THRESHOLD:
            alerts.append(f"⚠️ HIGH TEMP ALERT: {temp}°C - Produce spoilage risk!")
        elif temp < TEMP_LOW_THRESHOLD:
            alerts.append(f"🥶 LOW TEMP ALERT: {temp}°C - Cold damage risk!")
        
        if hum > HUMIDITY_HIGH_THRESHOLD:
            alerts.append(f"💧 HIGH HUMIDITY: {hum}% - Mold growth risk!")
        
        if alerts:
            print(f"🚨 ALERTS for {device_id}: {alerts}")
            # TODO: Send WhatsApp alert to farmer
            # send_whatsapp_message(farmer_id, "\n".join(alerts))
        else:
            print(f"✅ Conditions normal for {device_id}")
        
        return {"status": "processed", "alerts": alerts}
    
    elif event_type == "WHATSAPP_REPLY":
        user_text = data.get("text", "")
        
        # SIMPLE ECHO TEST LOGIC
        if "hello" in user_text.lower():
            response = "Hello Farmer! Neural Roots AI is online. 🌱"
        elif "price" in user_text.lower():
            response = "Current Mandi Price: ₹40/kg. City Price: ₹65/kg."
        elif "temp" in user_text.lower() or "sensor" in user_text.lower():
            response = "Checking your latest sensor data... 📡"
        else:
            response = f"I received: '{user_text}'. Waiting for AI logic..."
        
        # Send the response back
        send_whatsapp_message(farmer_id, response)
        return {"status": "replied", "message": response}
    
    return {"status": "unknown_event"}