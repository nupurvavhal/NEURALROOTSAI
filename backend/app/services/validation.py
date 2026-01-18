# backend/app/services/validation.py
from typing import Dict, Any, List, Optional
import re

ALLOWED_CROPS = {
    "tomato", "onion", "mango", "potato", "carrot",
    "cucumber", "lettuce", "spinach", "kale", "leafy_greens"
}


def validate_crop_data(db, crop_data: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    crop_name = str(crop_data.get("crop_name", "")).strip()
    temperature = crop_data.get("temperature")
    humidity = crop_data.get("humidity")
    age_hours = crop_data.get("age_hours", 0)
    quantity = crop_data.get("quantity", 0)

    if not crop_name:
        errors.append("crop_name is required")
    elif not re.match(r"^[A-Za-z_\- ]{2,50}$", crop_name):
        errors.append("crop_name must contain only letters, spaces, hyphen or underscore (2-50 chars)")

    if temperature is None:
        errors.append("temperature is required")
    elif not (-10 <= float(temperature) <= 60):
        errors.append("temperature must be between -10 and 60 °C")

    if humidity is None:
        errors.append("humidity is required")
    elif not (0 <= float(humidity) <= 100):
        errors.append("humidity must be between 0 and 100 %")

    if age_hours is None:
        errors.append("age_hours is required (can be 0)")
    elif float(age_hours) < 0:
        errors.append("age_hours cannot be negative")

    if quantity is None:
        errors.append("quantity is required")
    elif float(quantity) <= 0:
        errors.append("quantity must be > 0")

    # Recommend known crop names
    if crop_name and crop_name.lower() not in ALLOWED_CROPS:
        warnings.append("Unknown crop_name; using generic thresholds")

    # Check market data presence
    try:
        if crop_name:
            count = await_count(db, "wholesalers", {"crop_name": {"$regex": crop_name, "$options": "i"}})
            if count == 0:
                warnings.append("No wholesalers data found for crop; pricing may be limited")
    except Exception:
        warnings.append("Could not verify wholesalers collection; ensure DB connection")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_logistics_params(db, logistics: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    distance_km = logistics.get("distance_km", 0)
    if distance_km is None or float(distance_km) <= 0:
        errors.append("distance_km must be > 0")
    elif float(distance_km) > 2000:
        warnings.append("distance_km very high; ensure route feasibility")

    try:
        count = await_count(db, "drivers", {"status": "available"})
        if count == 0:
            warnings.append("No available drivers found; logistics may fail")
    except Exception:
        warnings.append("Could not verify drivers collection; ensure DB connection")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_market_params(db, market: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    urgency = market.get("urgency")
    if urgency and urgency not in {"LOW", "MEDIUM", "HIGH"}:
        errors.append("urgency must be one of LOW, MEDIUM, HIGH")

    target_location = market.get("target_location")
    if target_location and len(str(target_location)) > 100:
        errors.append("target_location too long (max 100 chars)")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# Helper: count documents in a collection (async Motor client)
async def await_count(db, collection_name: str, query: Dict[str, Any]) -> int:
    try:
        return await db[collection_name].count_documents(query)
    except Exception:
        return 0
