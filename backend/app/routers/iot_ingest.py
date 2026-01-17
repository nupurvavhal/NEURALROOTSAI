# backend/app/routers/iot.py
from fastapi import APIRouter
from app.models.schemas import IoTDataSchema
from app.core.database import get_database
from app.core.graph import run_workflow

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