# backend/app/routers/iot.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.database import get_database
from app.agents.freshness_agent import analyze_freshness, SensorInput
from datetime import datetime

router = APIRouter()


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class IoTDataSchema(BaseModel):
    """Schema for IoT sensor data + ML classification"""
    farmer_id: str
    device_id: str
    crop_type: str
    temperature: float
    humidity: float
    crop_classification: str  # "fresh" or "rotten" from your Colab model
    image_url: str = None
    timestamp: str = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/ingest")
async def ingest_iot_data(data: IoTDataSchema):
    """
    ESP32/IoT device hits this endpoint with sensor data + ML classification
    
    Flow:
    1. Receive sensor data (temp, humidity) + ML classification (fresh/rotten)
    2. Send to Gemini AI agent for freshness analysis
    3. Gemini returns: freshness_score, health_status, shelf_life, alerts
    4. Save everything to MongoDB
    5. Return analysis to device
    """
    db = get_database()
    
    try:
        print(f"\n📡 IoT Data Received:")
        print(f"   Farmer: {data.farmer_id}")
        print(f"   Crop: {data.crop_type}")
        print(f"   Classification: {data.crop_classification}")
        print(f"   Temp: {data.temperature}°C, Humidity: {data.humidity}%")
        
        # Step 1: Prepare data for Gemini agent
        sensor_input = SensorInput(
            farmer_id=data.farmer_id,
            device_id=data.device_id,
            crop_type=data.crop_type,
            temperature=data.temperature,
            humidity=data.humidity,
            crop_classification=data.crop_classification,
            image_url=data.image_url
        )
        
        # Step 2: Analyze with Gemini AI
        print(f"   🤖 Sending to Gemini AI for analysis...")
        analysis = await analyze_freshness(sensor_input)
        
        print(f"   ✅ Gemini Analysis Complete:")
        print(f"      Freshness Score: {analysis.freshness_score}/100")
        print(f"      Health Status: {analysis.health_status}")
        print(f"      Shelf Life: {analysis.shelf_life_hours}h")
        if analysis.alert_generated:
            print(f"      🚨 ALERT: {analysis.alert_message}")
        
        # Step 3: Save to MongoDB with Gemini predictions
        iot_entry = {
            # Original sensor data
            "farmer_id": data.farmer_id,
            "device_id": data.device_id,
            "crop_type": data.crop_type,
            "temperature": data.temperature,
            "humidity": data.humidity,
            "crop_classification": data.crop_classification,
            "image_url": data.image_url,
            
            # Gemini AI predictions
            "freshness_score": analysis.freshness_score,
            "health_status": analysis.health_status,
            "shelf_life_hours": analysis.shelf_life_hours,
            "alert_generated": analysis.alert_generated,
            "alert_type": analysis.alert_type,
            "alert_message": analysis.alert_message,
            "recommendations": analysis.recommendations,
            "ai_confidence": analysis.confidence,
            
            # Metadata
            "timestamp": data.timestamp or datetime.utcnow().isoformat(),
            "analyzed_at": analysis.analyzed_at,
            "createdAt": datetime.utcnow().isoformat(),
        }
        
        result = await db.iot_logs.insert_one(iot_entry)
        print(f"   💾 Saved to MongoDB: {result.inserted_id}")
        
        # Step 4: Return comprehensive response
        return {
            "success": True,
            "message": "IoT data processed successfully",
            "sensor_data": {
                "temperature": data.temperature,
                "humidity": data.humidity,
                "classification": data.crop_classification,
            },
            "gemini_analysis": {
                "freshness_score": analysis.freshness_score,
                "health_status": analysis.health_status,
                "shelf_life_hours": analysis.shelf_life_hours,
                "confidence": analysis.confidence,
            },
            "alert": {
                "generated": analysis.alert_generated,
                "type": analysis.alert_type,
                "message": analysis.alert_message,
            } if analysis.alert_generated else None,
            "recommendations": analysis.recommendations,
            "database_id": str(result.inserted_id)
        }
        
    except Exception as e:
        print(f"   ❌ Error processing IoT data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/readings/{farmer_id}/latest")
async def get_latest_reading(farmer_id: str):
    """Get latest IoT reading with Gemini analysis for a farmer"""
    db = get_database()
    
    reading = await db.iot_logs.find_one(
        {"farmer_id": farmer_id},
        sort=[("timestamp", -1)]
    )
    
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found")
    
    reading["_id"] = str(reading["_id"])
    return {"success": True, "data": reading}


@router.get("/alerts")
async def get_active_alerts():
    """Get all active alerts from recent IoT readings"""
    db = get_database()
    
    alerts = await db.iot_logs.find(
        {"alert_generated": True},
        sort=[("timestamp", -1)]
    ).to_list(50)
    
    for alert in alerts:
        alert["_id"] = str(alert["_id"])
    
    return {
        "success": True,
        "count": len(alerts),
        "alerts": alerts
    }
