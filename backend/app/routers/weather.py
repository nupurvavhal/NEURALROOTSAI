# backend/app/routers/weather.py
"""
Weather API Router
Endpoints for weather predictions and farmer alerts
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.core.database import get_database
from app.agents.weather_agent import (
    predict_weather_for_farmer,
    predict_weather_for_all_farmers,
    WeatherPrediction,
    WeatherAlert,
    CROP_WEATHER_SENSITIVITY
)
from app.services.weather_api import (
    get_current_weather,
    get_weather_forecast,
    get_weather_by_city,
    get_forecast_by_city,
    MAHARASHTRA_LOCATIONS
)

router = APIRouter(prefix="/api/weather", tags=["Weather"])


# ============================================================================
# WEATHER DATA ENDPOINTS
# ============================================================================

@router.get("/current/{city}")
async def get_city_weather(city: str):
    """Get current weather for a city"""
    weather = await get_weather_by_city(city)
    if not weather:
        raise HTTPException(status_code=404, detail=f"Weather data not found for {city}")
    return weather


@router.get("/forecast/{city}")
async def get_city_forecast(city: str):
    """Get 5-day weather forecast for a city"""
    forecast = await get_forecast_by_city(city)
    if not forecast:
        raise HTTPException(status_code=404, detail=f"Forecast not found for {city}")
    return forecast


@router.get("/locations")
async def get_available_locations():
    """Get list of supported Maharashtra locations"""
    return {
        "locations": list(MAHARASHTRA_LOCATIONS.keys()),
        "count": len(MAHARASHTRA_LOCATIONS)
    }


# ============================================================================
# FARMER WEATHER PREDICTION ENDPOINTS
# ============================================================================

@router.get("/predict/{farmer_id}", response_model=WeatherPrediction)
async def get_farmer_weather_prediction(farmer_id: str):
    """
    Get personalized weather prediction and alerts for a specific farmer
    
    - Fetches farmer's location and crops from database
    - Analyzes weather forecast
    - Generates alerts and precautionary measures
    """
    db = await get_database()
    
    # Try to find farmer by ID or by farmer_id field
    from bson import ObjectId
    
    farmer = None
    try:
        farmer = await db["farmers"].find_one({"_id": ObjectId(farmer_id)})
    except:
        farmer = await db["farmers"].find_one({"farmer_id": farmer_id})
    
    if not farmer:
        # Return demo prediction if farmer not found
        prediction = await predict_weather_for_farmer(
            farmer_id=farmer_id,
            farmer_name="Demo Farmer",
            location="Pune",
            crops=["tomatoes", "onions"]
        )
        return prediction
    
    # Generate prediction for farmer
    prediction = await predict_weather_for_farmer(
        farmer_id=str(farmer["_id"]),
        farmer_name=farmer.get("name", "Unknown"),
        location=farmer.get("location", "Pune"),
        crops=farmer.get("crops", ["tomatoes"]),
        lat=farmer.get("coordinates", {}).get("lat"),
        lon=farmer.get("coordinates", {}).get("lon")
    )
    
    # Store prediction in database
    await db["weather_predictions"].insert_one(prediction.model_dump())
    
    return prediction


@router.get("/predict-all", response_model=List[WeatherPrediction])
async def get_all_farmers_weather_predictions():
    """
    Generate weather predictions for all farmers in the database
    
    This is useful for batch processing and sending bulk alerts
    """
    db = await get_database()
    predictions = await predict_weather_for_all_farmers(db)
    
    # Store all predictions
    if predictions:
        await db["weather_predictions"].insert_many([p.model_dump() for p in predictions])
    
    return predictions


# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

@router.get("/alerts/active")
async def get_active_weather_alerts(
    location: Optional[str] = Query(None, description="Filter by location"),
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical")
):
    """
    Get all active weather alerts from recent predictions
    """
    db = await get_database()
    
    # Get predictions from last 12 hours
    cutoff = datetime.utcnow().replace(hour=datetime.utcnow().hour - 12)
    
    query = {}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    
    predictions = await db["weather_predictions"].find(query).sort("generated_at", -1).limit(50).to_list(length=50)
    
    # Extract unique alerts
    alerts = []
    seen_alerts = set()
    
    for pred in predictions:
        for alert in pred.get("alerts", []):
            alert_key = f"{alert['alert_type']}_{alert['expected_time']}"
            if alert_key not in seen_alerts:
                if severity is None or alert["severity"] == severity:
                    alert["farmer_id"] = pred["farmer_id"]
                    alert["farmer_name"] = pred["farmer_name"]
                    alert["location"] = pred["location"]
                    alerts.append(alert)
                    seen_alerts.add(alert_key)
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "retrieved_at vandaag": datetime.utcnow().isoformat()
    }


@router.get("/alerts/by-crop/{crop}")
async def get_alerts_by_crop(crop: str):
    """
    Get weather alerts affecting a specific crop type
    """
    db = await get_database()
    
    # Get recent predictions
    predictions = await db["weather_predictions"].find().sort("generated_at", -1).limit(50).to_list(length=50)
    
    alerts = []
    for pred in predictions:
        for alert in pred.get("alerts", []):
            if crop.lower() in [c.lower() for c in alert.get("affected_crops", [])]:
                alert["farmer_id"] = pred["farmer_id"]
                alert["farmer_name"] = pred["farmer_name"]
                alert["location"] = pred["location"]
                alerts.append(alert)
    
    return {
        "crop": crop,
        "alerts": alerts,
        "count": len(alerts)
    }


# ============================================================================
# CROP SENSITIVITY INFO
# ============================================================================

@router.get("/crops/sensitivity")
async def get_crop_weather_sensitivity():
    """
    Get weather sensitivity information for all supported crops
    
    This helps understand which crops are at risk under different conditions
    """
    return {
        "crops": CROP_WEATHER_SENSITIVITY,
        "supported_crops": list(CROP_WEATHER_SENSITIVITY.keys())
    }


@router.get("/crops/{crop}/sensitivity")
async def get_single_crop_sensitivity(crop: str):
    """Get weather sensitivity for a specific crop"""
    crop_lower = crop.lower()
    if crop_lower not in CROP_WEATHER_SENSITIVITY:
        raise HTTPException(
            status_code=404, 
            detail=f"Crop '{crop}' not found. Available: {list(CROP_WEATHER_SENSITIVITY.keys())}"
        )
    
    return {
        "crop": crop,
        "sensitivity": CROP_WEATHER_SENSITIVITY[crop_lower]
    }


# ============================================================================
# DEMO ENDPOINT
# ============================================================================

@router.get("/demo")
async def demo_weather_prediction():
    """
    Demo endpoint to test weather prediction without database
    """
    prediction = await predict_weather_for_farmer(
        farmer_id="demo_001",
        farmer_name="Rajesh Kumar",
        location="Nashik",
        crops=["grapes", "onions", "tomatoes"]
    )
    
    return {
        "message": "Demo weather prediction generated",
        "prediction": prediction
    }
