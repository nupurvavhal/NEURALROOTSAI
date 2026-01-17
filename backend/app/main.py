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
    """Get all market prices from database - connects to frontend MarketTerminal"""
    from app.core.database import get_database
    db = get_database()
    
    try:
        market_items = await db.market_items.find().to_list(100)
        for item in market_items:
            item["_id"] = str(item["_id"])
        return {"success": True, "data": market_items}
    except Exception as e:
        # Fallback to hardcoded data
        market_data = [
            {"id": "M001", "cropName": "Alphonso Mangoes", "mandiName": "Ratnagiri APMC", "price": 400, "trend": "up", "spoilageRisk": "Critical"},
            {"id": "M002", "cropName": "Onions", "mandiName": "Nashik Mandi", "price": 90, "trend": "down", "spoilageRisk": "Low"},
            {"id": "M003", "cropName": "Tomatoes", "mandiName": "Pune APMC", "price": 150, "trend": "up", "spoilageRisk": "Critical"},
        ]
        return {"success": True, "data": market_data}


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


@app.get("/api/v1/wholesalers")
async def get_wholesalers():
    """Get all wholesalers - connects to frontend WholesalersModule"""
    from app.core.database import get_database
    db = get_database()
    
    try:
        wholesalers = await db.wholesalers.find().to_list(100)
        for wholesaler in wholesalers:
            wholesaler["_id"] = str(wholesaler["_id"])
        return {"success": True, "data": wholesalers}
    except Exception as e:
        return {"success": True, "data": [], "message": "No wholesalers in database yet"}


@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_analytics():
    """Get dashboard analytics data"""
    from app.core.database import get_database
    db = get_database()
    
    try:
        # Count documents in each collection
        farmers_count = await db.farmers.count_documents({})
        drivers_count = await db.drivers.count_documents({})
        iot_count = await db.iot_logs.count_documents({})
        
        return {
            "success": True,
            "data": {
                "totalFarmers": farmers_count,
                "totalDrivers": drivers_count,
                "totalIotReadings": iot_count,
                "systemStatus": "operational"
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}