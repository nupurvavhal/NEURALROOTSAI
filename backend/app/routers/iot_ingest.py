# backend/app/routers/iot_ingest.py
"""IoT Ingest Router - Handles ESP32 device connections and sensor data"""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.models.schemas import IoTDataSchema
from app.core.database import get_database
from app.core.graph import run_workflow
from pathlib import Path
from uuid import uuid4
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.post("/ingest")
async def ingest_iot_data(data: IoTDataSchema):
    """
    ESP32 hits this endpoint.
    1. Save raw data to DB (For Admin Dashboard).
    2. Trigger AI Brain to check freshness.
    """
    db = get_database()
    
    # 1. Save to MongoDB 'iot_logs' collection
    new_entry = data.dict()
    await db.iot_logs.insert_one(new_entry)
    print(f"📡 IoT Data Received from {data.farmer_id}: {data.temperature}°C")

    # 2. Trigger the Brain (Simulated for now)
    # We tell the brain: "New Data arrived for this farmer!"
    await run_workflow(
        farmer_id=data.farmer_id, 
        event_type="IOT_DATA_RECEIVED", 
        data=new_entry
    )

    return {"status": "success", "message": "Data saved & AI triggered"}


@router.post("/ingest/upload")
async def ingest_iot_upload(
    farmer_id: str = Form(...),
    temperature: float = Form(...),
    humidity: float = Form(...),
    image: UploadFile = File(...),
    timestamp: Optional[str] = Form(None),
):
    """Accept multipart form-data with an image and sensor readings."""
    db = get_database()

    uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{farmer_id}_{uuid4().hex}_{image.filename}"
    file_path = uploads_dir / safe_name

    try:
        file_path.write_bytes(await image.read())
    except Exception as exc:  # pragma: no cover - simple IO guard
        raise HTTPException(status_code=500, detail=f"Failed to save image: {exc}")

    new_entry = {
        "farmer_id": farmer_id,
        "temperature": temperature,
        "humidity": humidity,
        "image_url": f"/uploads/{safe_name}",
        "timestamp": timestamp,
    }

    await db.iot_logs.insert_one(new_entry)
    await run_workflow(
        farmer_id=farmer_id,
        event_type="IOT_DATA_RECEIVED",
        data=new_entry,
    )

    return {"status": "success", "image_url": new_entry["image_url"]}


# ============================================================================
# ESP32 SPECIFIC ENDPOINTS
# ============================================================================

@router.get("/esp32/data")
async def esp32_data_info():
    """
    INFO: This endpoint expects POST with multipart form-data
    
    ✅ CORRECT USAGE (POST):
    - Content-Type: multipart/form-data
    - Form fields:
      * device_id (string): e.g., "esp32cam_01"
      * temp (float): e.g., 26.5
      * hum (float): e.g., 65.0
      * image (file, optional): JPG image
    
    ❌ NOT A GET ENDPOINT - you're hitting this with GET
    Use POST from ESP32 or curl:
    curl -X POST http://server:8000/api/iot/esp32/data \\
      -F "device_id=esp32cam_01" \\
      -F "temp=26.5" \\
      -F "hum=65.0" \\
      -F "image=@capture.jpg"
    """
    return {
        "error": "Use POST method",
        "endpoint": "POST /api/iot/esp32/data",
        "content_type": "multipart/form-data",
        "fields_required": ["device_id", "temp", "hum"],
        "fields_optional": ["image"]
    }

@router.post("/esp32/data")
async def esp32_sensor_data(
    device_id: str = Form(...),
    temp: float = Form(...),
    hum: float = Form(...),
    image: Optional[UploadFile] = File(None),
):
    """
    ✅ ESP32-CAM DATA UPLOAD ENDPOINT
    
    Accepts multipart/form-data with sensor readings and optional image.
    
    Process:
    1. Save image to uploads/ directory (if provided)
    2. Store sensor data in MongoDB iot_logs collection
    3. Update device status in iot_devices collection
    4. Trigger AI workflow for analysis (freshness, alerts, etc.)
    
    Request:
    - Method: POST
    - Content-Type: multipart/form-data
    - Fields:
      * device_id (required): Device identifier string
      * temp (required): Temperature in Celsius (float)
      * hum (required): Humidity percentage (float)
      * image (optional): JPEG image file
    
    Response: {"status": "success", "image_saved": bool}
    """
    db = get_database()
    timestamp = datetime.utcnow().isoformat()
    
    image_url = ""
    
    # Handle image upload if provided
    if image and image.filename:
        uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = f"{device_id}_{uuid4().hex}_{image.filename}"
        file_path = uploads_dir / safe_name
        
        try:
            contents = await image.read()
            file_path.write_bytes(contents)
            image_url = f"/uploads/{safe_name}"
            print(f"📷 Image saved: {safe_name}")
        except Exception as exc:
            print(f"⚠️ Image save failed: {exc}")
    
    # Create the sensor reading entry
    new_entry = {
        "farmer_id": device_id,
        "device_id": device_id,
        "temperature": temp,
        "humidity": hum,
        "image_url": image_url,
        "timestamp": timestamp,
        "created_at": datetime.utcnow(),
    }
    
    # Save to database
    await db.iot_logs.insert_one(new_entry)
    print(f"📡 ESP32 Data: {device_id} | Temp: {temp}°C | Hum: {hum}%")
    
    # Update device status
    await db.iot_devices.update_one(
        {"device_id": device_id},
        {
            "$set": {
                "device_id": device_id,
                "last_seen": datetime.utcnow(),
                "last_temp": temp,
                "last_hum": hum,
                "status": "online",
            },
            "$inc": {"total_readings": 1},
        },
        upsert=True,
    )
    
    # Trigger AI workflow
    try:
        await run_workflow(
            farmer_id=device_id,
            event_type="IOT_DATA_RECEIVED",
            data=new_entry,
        )
    except Exception as e:
        print(f"⚠️ Workflow error: {e}")
    
    return JSONResponse(
        content={
            "status": "success",
            "message": "Data received",
            "timestamp": timestamp,
            "image_saved": bool(image_url),
        },
        status_code=200,
    )


@router.get("/devices")
async def list_iot_devices():
    """List all registered IoT devices with their status."""
    db = get_database()
    
    try:
        devices = await db.iot_devices.find().to_list(100)
        for device in devices:
            device["_id"] = str(device["_id"])
            # Check if device is online (seen in last 10 minutes)
            if "last_seen" in device:
                diff = (datetime.utcnow() - device["last_seen"]).total_seconds()
                device["status"] = "online" if diff < 600 else "offline"
                device["last_seen"] = device["last_seen"].isoformat()
            if "created_at" in device:
                device["created_at"] = device["created_at"].isoformat() if hasattr(device["created_at"], 'isoformat') else str(device["created_at"])
        return {"success": True, "devices": devices}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/devices/{device_id}")
async def get_device_status(device_id: str):
    """Get status and latest reading for a specific device."""
    db = get_database()
    
    try:
        device = await db.iot_devices.find_one({"device_id": device_id})
        if not device:
            return {"success": False, "message": "Device not found"}
        
        device["_id"] = str(device["_id"])
        if "last_seen" in device:
            device["last_seen"] = device["last_seen"].isoformat()
        
        # Get last 10 readings
        readings = await db.iot_logs.find(
            {"device_id": device_id}
        ).sort("timestamp", -1).limit(10).to_list(10)
        
        for r in readings:
            r["_id"] = str(r["_id"])
            if "created_at" in r:
                r["created_at"] = r["created_at"].isoformat() if hasattr(r["created_at"], 'isoformat') else str(r["created_at"])
        
        return {
            "success": True,
            "device": device,
            "recent_readings": readings,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/readings/{device_id}")
async def get_device_readings(device_id: str, limit: int = 50):
    """Get sensor readings for a device."""
    db = get_database()
    
    try:
        readings = await db.iot_logs.find(
            {"$or": [{"device_id": device_id}, {"farmer_id": device_id}]}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        for r in readings:
            r["_id"] = str(r["_id"])
            if "created_at" in r:
                r["created_at"] = r["created_at"].isoformat() if hasattr(r["created_at"], 'isoformat') else str(r["created_at"])
        
        return {"success": True, "readings": readings, "count": len(readings)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/ping")
async def ping():
    """Simple ping endpoint for ESP32 to check server connectivity."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}