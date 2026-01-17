# backend/app/routers/market.py
"""
Market API Router
REST endpoints for market analysis and driver booking
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.core.database import get_database
from app.agents.market_agent import (
    analyze_market_for_crop,
    assign_driver_for_transport,
    MarketAnalysis,
    DriverAssignment,
    MANDI_DATABASE
)

router = APIRouter(prefix="/api/market", tags=["Market"])


# ============================================================================
# MARKET ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/analyze/{farmer_id}")
async def analyze_market(
    farmer_id: str,
    crop: str = Query(..., description="Crop type to analyze"),
    quantity: float = Query(..., description="Quantity in kg", gt=0, le=10000)
) -> MarketAnalysis:
    """
    Get market analysis for a specific crop and quantity
    
    Returns all mandi options with price comparison, transport costs,
    and profit analysis.
    """
    db = await get_database()
    
    analysis = await analyze_market_for_crop(db, farmer_id, crop, quantity)
    
    # Store analysis in database
    await db["market_analyses"].insert_one(analysis.model_dump())
    
    return analysis


@router.get("/prices")
async def get_all_market_prices():
    """Get current prices for all crops across all mandis"""
    db = await get_database()
    
    items = await db["market_items"].find().to_list(length=100)
    
    for item in items:
        item["_id"] = str(item["_id"])
    
    return {"prices": items, "count": len(items)}


@router.get("/prices/{crop}")
async def get_crop_prices(crop: str):
    """Get prices for a specific crop across all mandis"""
    db = await get_database()
    
    items = await db["market_items"].find({
        "cropName": {"$regex": crop, "$options": "i"}
    }).to_list(length=50)
    
    for item in items:
        item["_id"] = str(item["_id"])
    
    if not items:
        raise HTTPException(status_code=404, detail=f"No price data found for {crop}")
    
    return {"crop": crop, "prices": items, "count": len(items)}


@router.get("/mandis")
async def get_all_mandis():
    """Get list of all supported mandis with their details"""
    return {
        "mandis": MANDI_DATABASE,
        "count": len(MANDI_DATABASE)
    }


# ============================================================================
# DRIVER & BOOKING ENDPOINTS
# ============================================================================

@router.post("/book")
async def book_transport(
    farmer_id: str,
    crop: str,
    quantity: float,
    mandi: str
) -> DriverAssignment:
    """
    Book a driver for crop transport
    
    Finds an available driver with suitable vehicle capacity
    and assigns them for the transport.
    """
    db = await get_database()
    
    assignment = await assign_driver_for_transport(
        db, farmer_id, mandi, crop, quantity
    )
    
    if not assignment:
        raise HTTPException(
            status_code=503, 
            detail="No drivers available. Please try again later."
        )
    
    return assignment


@router.get("/bookings")
async def get_all_bookings(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=200)
):
    """Get all transport bookings"""
    db = await get_database()
    
    query = {}
    if status:
        query["status"] = status
    
    bookings = await db["bookings"].find(query).sort("assigned_at", -1).limit(limit).to_list(length=limit)
    
    for booking in bookings:
        booking["_id"] = str(booking["_id"])
    
    return {"bookings": bookings, "count": len(bookings)}


@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """Get a specific booking by ID"""
    db = await get_database()
    
    booking = await db["bookings"].find_one({"booking_id": booking_id})
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking["_id"] = str(booking["_id"])
    return booking


@router.patch("/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: str,
    status: str = Query(..., description="New status: assigned, confirmed, in_transit, delivered, cancelled")
):
    """Update booking status"""
    db = await get_database()
    
    valid_statuses = ["assigned", "confirmed", "in_transit", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    result = await db["bookings"].update_one(
        {"booking_id": booking_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # If delivered or cancelled, free up the driver
    if status in ["delivered", "cancelled"]:
        booking = await db["bookings"].find_one({"booking_id": booking_id})
        if booking:
            await db["drivers"].update_one(
                {"id": booking.get("driver_id")},
                {"$set": {"status": "Available", "currentLoad": "Empty"}}
            )
    
    return {"success": True, "booking_id": booking_id, "new_status": status}


# ============================================================================
# DRIVER ENDPOINTS
# ============================================================================

@router.get("/drivers")
async def get_all_drivers():
    """Get all drivers and their status"""
    db = await get_database()
    
    drivers = await db["drivers"].find().to_list(length=50)
    
    for driver in drivers:
        driver["_id"] = str(driver["_id"])
    
    available_count = sum(1 for d in drivers if d.get("status") == "Available")
    
    return {
        "drivers": drivers,
        "total": len(drivers),
        "available": available_count,
        "busy": len(drivers) - available_count
    }


@router.get("/drivers/available")
async def get_available_drivers():
    """Get only available drivers"""
    db = await get_database()
    
    drivers = await db["drivers"].find({"status": "Available"}).to_list(length=50)
    
    for driver in drivers:
        driver["_id"] = str(driver["_id"])
    
    return {"drivers": drivers, "count": len(drivers)}


# ============================================================================
# DEMO ENDPOINT
# ============================================================================

@router.get("/demo")
async def demo_market_analysis():
    """
    Demo endpoint to test market analysis without real farmer data
    """
    db = await get_database()
    
    analysis = await analyze_market_for_crop(
        db,
        farmer_id="demo_001",
        crop_type="Tomatoes",
        quantity_kg=200
    )
    
    return {
        "message": "Demo market analysis generated",
        "analysis": analysis
    }
