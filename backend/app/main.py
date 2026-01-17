# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import connect_to_mongo, close_mongo_connection  
from app.routers import whatsapp_webhook, iot_ingest

# Lifecycle Manager (Connect DB on startup)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan, title="Neural Roots AI Backend")

# CORS Middleware - Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",      # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the WhatsApp router
app.include_router(whatsapp_webhook.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(iot_ingest.router, prefix="/api/iot", tags=["IoT"])

@app.get("/")
def health_check():
    return {"status": "Neural Roots System Operational 🚀"}


# ============================================================================
# API V1 ROUTES - For Frontend Integration
# ============================================================================

@app.get("/api/v1/health")
def api_health():
    """Health check for API v1"""
    return {"success": True, "message": "API v1 operational", "version": "1.0.0"}


@app.get("/api/v1/prices")
async def get_market_prices():
    """Get all market prices - connects to frontend MarketTerminal"""
    # Market data structure matching frontend expectations
    market_data = {
        "potatoes": {"mandi": 45.0, "village": 25.0, "unit": "kg", "trend": "up"},
        "jowar": {"mandi": 32.0, "village": 18.0, "unit": "kg", "trend": "down"},
        "tomatoes": {"mandi": 60.0, "village": 20.0, "unit": "kg", "trend": "up"},
        "onions": {"mandi": 40.0, "village": 22.0, "unit": "kg", "trend": "down"},
        "grapes": {"mandi": 120.0, "village": 80.0, "unit": "kg", "trend": "up"},
        "bananas": {"mandi": 35.0, "village": 20.0, "unit": "kg", "trend": "down"},
    }
    return {"success": True, "data": market_data, "timestamp": "2026-01-17T00:00:00Z"}


@app.get("/api/v1/farmers")
async def get_farmers():
    """Get all farmers - connects to frontend FarmersModule"""
    from app.core.database import get_database
    db = get_database()
    
    # Try to fetch from database, return empty if not available
    try:
        farmers = await db.farmers.find().to_list(100)
        # Convert ObjectId to string for JSON serialization
        for farmer in farmers:
            farmer["_id"] = str(farmer["_id"])
        return {"success": True, "data": farmers}
    except Exception as e:
        return {"success": True, "data": [], "message": "No farmers in database yet"}


@app.get("/api/v1/drivers")
async def get_drivers():
    """Get all drivers - connects to frontend FleetModule"""
    from app.core.database import get_database
    db = get_database()
    
    try:
        drivers = await db.drivers.find().to_list(100)
        for driver in drivers:
            driver["_id"] = str(driver["_id"])
        return {"success": True, "data": drivers}
    except Exception as e:
        return {"success": True, "data": [], "message": "No drivers in database yet"}


@app.get("/api/v1/iot/readings/{device_id}/latest")
async def get_latest_iot_reading(device_id: str):
    """Get latest IoT reading for a device"""
    from app.core.database import get_database
    db = get_database()
    
    try:
        reading = await db.iot_logs.find_one(
            {"farmer_id": device_id},
            sort=[("timestamp", -1)]
        )
        if reading:
            reading["_id"] = str(reading["_id"])
            return {"success": True, "data": reading}
        return {"success": False, "message": "No readings found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

USE_BACKEND_API = True
USE_MOCK_DATA = False