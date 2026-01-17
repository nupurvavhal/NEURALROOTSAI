# backend/app/agents/market_agent.py
"""
Market Agent - Analyzes market prices and helps farmers choose optimal mandi
Includes WhatsApp conversation flow for crop selling decisions
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Try to import Gemini
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-genai not installed, using rule-based market analysis")


# ============================================================================
# DATA MODELS
# ============================================================================

class MandiOption(BaseModel):
    """Single mandi option for selling crops"""
    mandi_id: str
    mandi_name: str
    location: str
    current_price: float           # Price per kg
    trend: str                     # "up", "down", "stable"
    spoilage_risk: str             # "Low", "Medium", "Critical"
    distance_km: float             # Approx distance from farmer
    estimated_revenue: float       # For the given quantity
    transport_cost: float          # Estimated transport cost
    net_profit: float              # Revenue - transport cost
    profit_margin_percent: float   # Profit margin percentage
    recommended: bool              # Is this the best option?
    recommendation_reason: str


class MarketAnalysis(BaseModel):
    """Complete market analysis for a farmer's crop"""
    farmer_id: str
    farmer_name: str
    farmer_location: str
    crop_type: str
    quantity_kg: float
    
    # All mandi options (sorted by net profit)
    mandi_options: List[MandiOption]
    
    # Best recommendation
    best_mandi: str
    best_price: float
    best_profit: float
    
    # Analysis summary
    price_range: str              # "₹X - ₹Y per kg"
    profit_gap: str               # Difference between best and worst
    market_insight: str           # AI-generated insight
    
    # Timing advice
    sell_urgency: str             # "immediate", "within_24h", "flexible"
    urgency_reason: str
    
    generated_at: str


class DriverAssignment(BaseModel):
    """Driver assignment for crop transport"""
    booking_id: str
    farmer_id: str
    farmer_name: str
    farmer_phone: str
    
    # Driver details
    driver_id: str
    driver_name: str
    driver_phone: str
    vehicle_type: str
    vehicle_capacity_kg: int
    
    # Transport details
    pickup_location: str
    destination_mandi: str
    crop_type: str
    quantity_kg: float
    estimated_distance_km: float
    estimated_cost: float
    
    # Status
    status: str                   # "assigned", "confirmed", "in_transit", "delivered"
    assigned_at: str
    estimated_pickup_time: str


class ConversationState(BaseModel):
    """Tracks WhatsApp conversation state for a farmer"""
    farmer_id: str
    farmer_phone: str
    farmer_name: Optional[str] = None  # WhatsApp profile name
    farmer_village: Optional[str] = None  # Farmer's village/location
    is_new_farmer: bool = False  # Whether this is a new farmer registration
    current_step: str             # "awaiting_name", "awaiting_village", "awaiting_crop", "awaiting_quantity", "awaiting_mandi_choice", "awaiting_confirmation"
    
    # Collected data
    selected_crop: Optional[str] = None
    quantity_kg: Optional[float] = None
    selected_mandi: Optional[str] = None
    expected_profit: Optional[float] = None  # Expected profit from selected mandi
    market_analysis: Optional[Dict] = None
    
    # Timestamps
    started_at: str
    last_interaction: str
    expires_at: str


# ============================================================================
# MANDI DATABASE (Expanded with coordinates)
# ============================================================================

MANDI_DATABASE = {
    "Pune APMC": {"location": "Pune", "lat": 18.5204, "lon": 73.8567, "transport_rate_per_km": 3.5},
    "Nashik Mandi": {"location": "Nashik", "lat": 19.9975, "lon": 73.7898, "transport_rate_per_km": 3.0},
    "Nashik Grape Market": {"location": "Nashik", "lat": 20.0063, "lon": 73.7890, "transport_rate_per_km": 3.0},
    "Mumbai Wholesale": {"location": "Mumbai", "lat": 19.0760, "lon": 72.8777, "transport_rate_per_km": 4.0},
    "Kolhapur Market": {"location": "Kolhapur", "lat": 16.7050, "lon": 74.2433, "transport_rate_per_km": 3.2},
    "Ratnagiri APMC": {"location": "Ratnagiri", "lat": 16.9902, "lon": 73.3120, "transport_rate_per_km": 3.5},
    "Jalgaon APMC": {"location": "Jalgaon", "lat": 21.0077, "lon": 75.5626, "transport_rate_per_km": 3.0},
    "Satara Mandi": {"location": "Satara", "lat": 17.6805, "lon": 74.0183, "transport_rate_per_km": 3.2},
    "Solapur APMC": {"location": "Solapur", "lat": 17.6599, "lon": 75.9064, "transport_rate_per_km": 3.0},
    "Sangli Spice Market": {"location": "Sangli", "lat": 16.8524, "lon": 74.5815, "transport_rate_per_km": 3.2},
    "Aurangabad Market": {"location": "Aurangabad", "lat": 19.8762, "lon": 75.3433, "transport_rate_per_km": 3.0},
    "Pune Vegetable Market": {"location": "Pune", "lat": 18.5314, "lon": 73.8446, "transport_rate_per_km": 3.5},
}

FARMER_LOCATIONS = {
    "Pune, Maharashtra": {"lat": 18.5204, "lon": 73.8567},
    "Nashik, Maharashtra": {"lat": 19.9975, "lon": 73.7898},
    "Satara, Maharashtra": {"lat": 17.6805, "lon": 74.0183},
    "Kolhapur, Maharashtra": {"lat": 16.7050, "lon": 74.2433},
    "Ahmednagar, Maharashtra": {"lat": 19.0948, "lon": 74.7480},
    "Solapur, Maharashtra": {"lat": 17.6599, "lon": 75.9064},
    "Sangli, Maharashtra": {"lat": 16.8524, "lon": 74.5815},
    "Aurangabad, Maharashtra": {"lat": 19.8762, "lon": 75.3433},
    "Jalgaon, Maharashtra": {"lat": 21.0077, "lon": 75.5626},
    "Ratnagiri, Maharashtra": {"lat": 16.9902, "lon": 73.3120},
}

VEHICLE_CAPACITIES = {
    "Tata Ace": 750,
    "Mahindra Pickup": 1000,
    "Tata 407": 2500,
    "Ashok Leyland Dost": 1500,
    "Eicher Pro 1049": 4000,
    "Mahindra Bolero Pickup": 1200,
    "Tata 709": 5000,
}

# Default prices for common crops (₹ per kg) - used when not in database
DEFAULT_CROP_PRICES = {
    # Vegetables
    "tomatoes": {"price": 80, "trend": "up", "spoilage": "Critical", "aliases": ["tomato", "tamatar"]},
    "onions": {"price": 40, "trend": "stable", "spoilage": "Low", "aliases": ["onion", "pyaz", "pyaaz", "kanda"]},
    "potatoes": {"price": 30, "trend": "stable", "spoilage": "Low", "aliases": ["potato", "aloo", "batata"]},
    "cauliflower": {"price": 50, "trend": "up", "spoilage": "Medium", "aliases": ["gobi", "phool gobi"]},
    "cabbage": {"price": 25, "trend": "down", "spoilage": "Medium", "aliases": ["patta gobi", "band gobi"]},
    "spinach": {"price": 40, "trend": "stable", "spoilage": "Critical", "aliases": ["palak"]},
    "brinjal": {"price": 35, "trend": "stable", "spoilage": "Medium", "aliases": ["eggplant", "baingan", "vangi"]},
    "lady finger": {"price": 45, "trend": "up", "spoilage": "Critical", "aliases": ["okra", "bhindi"]},
    "green chilli": {"price": 60, "trend": "up", "spoilage": "Medium", "aliases": ["mirchi", "hari mirchi"]},
    "capsicum": {"price": 70, "trend": "up", "spoilage": "Medium", "aliases": ["shimla mirch", "bell pepper"]},
    "carrot": {"price": 40, "trend": "stable", "spoilage": "Low", "aliases": ["gajar"]},
    "beans": {"price": 55, "trend": "stable", "spoilage": "Medium", "aliases": ["french beans"]},
    "peas": {"price": 80, "trend": "up", "spoilage": "Medium", "aliases": ["matar", "green peas"]},
    "bitter gourd": {"price": 50, "trend": "stable", "spoilage": "Medium", "aliases": ["karela"]},
    "bottle gourd": {"price": 30, "trend": "stable", "spoilage": "Medium", "aliases": ["lauki", "dudhi"]},
    "cucumber": {"price": 35, "trend": "stable", "spoilage": "Medium", "aliases": ["kheera", "kakdi"]},
    "pumpkin": {"price": 25, "trend": "stable", "spoilage": "Low", "aliases": ["kaddu", "bhopla"]},
    "radish": {"price": 20, "trend": "down", "spoilage": "Medium", "aliases": ["mooli"]},
    "coriander": {"price": 100, "trend": "up", "spoilage": "Critical", "aliases": ["dhania", "kothimbir"]},
    "mint": {"price": 80, "trend": "stable", "spoilage": "Critical", "aliases": ["pudina"]},
    "ginger": {"price": 120, "trend": "up", "spoilage": "Low", "aliases": ["adrak"]},
    "garlic": {"price": 150, "trend": "up", "spoilage": "Low", "aliases": ["lehsun", "lasun"]},
    
    # Fruits
    "bananas": {"price": 40, "trend": "stable", "spoilage": "Medium", "aliases": ["banana", "kela"]},
    "mangoes": {"price": 150, "trend": "up", "spoilage": "Critical", "aliases": ["mango", "aam", "hapus", "alphonso"]},
    "grapes": {"price": 120, "trend": "up", "spoilage": "Critical", "aliases": ["grape", "angoor"]},
    "oranges": {"price": 60, "trend": "stable", "spoilage": "Low", "aliases": ["orange", "santra", "narangi"]},
    "apples": {"price": 150, "trend": "stable", "spoilage": "Low", "aliases": ["apple", "seb"]},
    "pomegranate": {"price": 180, "trend": "up", "spoilage": "Low", "aliases": ["anar", "dalimb"]},
    "papaya": {"price": 35, "trend": "stable", "spoilage": "Critical", "aliases": ["papita"]},
    "watermelon": {"price": 20, "trend": "down", "spoilage": "Medium", "aliases": ["tarbooz", "kalingad"]},
    "guava": {"price": 50, "trend": "stable", "spoilage": "Medium", "aliases": ["amrud", "peru"]},
    "custard apple": {"price": 100, "trend": "up", "spoilage": "Critical", "aliases": ["sitaphal", "sharifa"]},
    "chikoo": {"price": 60, "trend": "stable", "spoilage": "Medium", "aliases": ["sapota", "sapodilla"]},
    "coconut": {"price": 25, "trend": "stable", "spoilage": "Low", "aliases": ["nariyal"]},
    "lemon": {"price": 80, "trend": "up", "spoilage": "Low", "aliases": ["nimbu", "limbu"]},
    
    # Grains & Pulses
    "wheat": {"price": 25, "trend": "stable", "spoilage": "Low", "aliases": ["gehun"]},
    "rice": {"price": 40, "trend": "stable", "spoilage": "Low", "aliases": ["chawal", "tandul"]},
    "jowar": {"price": 30, "trend": "stable", "spoilage": "Low", "aliases": ["sorghum"]},
    "bajra": {"price": 28, "trend": "stable", "spoilage": "Low", "aliases": ["pearl millet"]},
    "maize": {"price": 22, "trend": "stable", "spoilage": "Low", "aliases": ["corn", "makka"]},
    "tur dal": {"price": 120, "trend": "up", "spoilage": "Low", "aliases": ["arhar", "toor"]},
    "chana": {"price": 70, "trend": "stable", "spoilage": "Low", "aliases": ["chickpea", "gram"]},
    "moong": {"price": 100, "trend": "up", "spoilage": "Low", "aliases": ["green gram", "moong dal"]},
    "urad": {"price": 110, "trend": "up", "spoilage": "Low", "aliases": ["black gram", "urad dal"]},
    "groundnut": {"price": 60, "trend": "stable", "spoilage": "Low", "aliases": ["peanut", "moongphali", "shengdana"]},
    "soybean": {"price": 50, "trend": "stable", "spoilage": "Low", "aliases": ["soya"]},
    
    # Cash Crops
    "sugarcane": {"price": 3, "trend": "stable", "spoilage": "Low", "aliases": ["ganna", "oos"]},
    "cotton": {"price": 70, "trend": "up", "spoilage": "Low", "aliases": ["kapas"]},
    "turmeric": {"price": 100, "trend": "up", "spoilage": "Low", "aliases": ["haldi"]},
}


def get_crop_default_price(crop_name: str) -> dict:
    """Get default price info for a crop by name or alias"""
    crop_lower = crop_name.lower().strip()
    
    # Direct match
    if crop_lower in DEFAULT_CROP_PRICES:
        info = DEFAULT_CROP_PRICES[crop_lower]
        return {"price": info["price"], "trend": info["trend"], "spoilage": info["spoilage"]}
    
    # Check aliases
    for crop, info in DEFAULT_CROP_PRICES.items():
        if crop_lower in info.get("aliases", []):
            return {"price": info["price"], "trend": info["trend"], "spoilage": info["spoilage"]}
    
    # Partial match
    for crop, info in DEFAULT_CROP_PRICES.items():
        if crop_lower in crop or crop in crop_lower:
            return {"price": info["price"], "trend": info["trend"], "spoilage": info["spoilage"]}
        for alias in info.get("aliases", []):
            if crop_lower in alias or alias in crop_lower:
                return {"price": info["price"], "trend": info["trend"], "spoilage": info["spoilage"]}
    
    # Unknown crop - return reasonable default
    return {"price": 50, "trend": "stable", "spoilage": "Medium"}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate approximate distance in km using Haversine formula"""
    import math
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return round(R * c, 1)


def get_farmer_coordinates(location: str) -> tuple:
    """Get coordinates for a farmer's location"""
    loc_data = FARMER_LOCATIONS.get(location)
    if loc_data:
        return loc_data["lat"], loc_data["lon"]
    # Default to Pune
    return 18.5204, 73.8567


# ============================================================================
# MARKET ANALYSIS FUNCTIONS
# ============================================================================

async def analyze_market_for_crop(
    db,
    farmer_id: str,
    crop_type: str,
    quantity_kg: float,
    farmer_village: str = "Pune, Maharashtra"
) -> MarketAnalysis:
    """
    Analyze market prices across all mandis for a specific crop
    
    Args:
        db: MongoDB database instance
        farmer_id: Farmer's ID
        crop_type: Type of crop to sell
        quantity_kg: Quantity in kilograms
        farmer_village: Farmer's village/location
        
    Returns:
        MarketAnalysis with all mandi options
    """
    
    # Get farmer details
    farmer = await db["farmers"].find_one({"id": farmer_id})
    if not farmer:
        farmer = {"name": "Unknown Farmer", "village": farmer_village, "id": farmer_id}
    
    farmer_lat, farmer_lon = get_farmer_coordinates(farmer.get("village", farmer_village))
    
    # Get default price info for this crop
    default_price_info = get_crop_default_price(crop_type)
    default_price = default_price_info["price"]
    default_trend = default_price_info["trend"]
    default_spoilage = default_price_info["spoilage"]
    
    print(f"📊 Analyzing market for {crop_type}: Default price ₹{default_price}/kg")
    
    # Get market prices for this crop from database
    market_items = await db["market_items"].find({
        "cropName": {"$regex": crop_type, "$options": "i"}
    }).to_list(length=20)
    
    # If no exact match, get all items and filter
    if not market_items:
        market_items = await db["market_items"].find().to_list(length=50)
        # Try partial match
        crop_lower = crop_type.lower()
        market_items = [m for m in market_items if crop_lower in m.get("cropName", "").lower()]
    
    # If still no match, create market options with realistic prices based on default
    if not market_items:
        print(f"   No DB prices found, using default prices for {crop_type}")
        # Create varied prices across different mandis (±20% variation)
        import random
        market_items = [
            {"id": "M001", "cropName": crop_type, "mandiName": "Pune APMC", 
             "price": round(default_price * random.uniform(0.95, 1.15)), "trend": default_trend, "spoilageRisk": default_spoilage},
            {"id": "M002", "cropName": crop_type, "mandiName": "Mumbai Wholesale", 
             "price": round(default_price * random.uniform(1.05, 1.25)), "trend": "up", "spoilageRisk": default_spoilage},
            {"id": "M003", "cropName": crop_type, "mandiName": "Nashik Mandi", 
             "price": round(default_price * random.uniform(0.90, 1.10)), "trend": default_trend, "spoilageRisk": default_spoilage},
            {"id": "M004", "cropName": crop_type, "mandiName": "Kolhapur Market", 
             "price": round(default_price * random.uniform(0.92, 1.12)), "trend": default_trend, "spoilageRisk": default_spoilage},
            {"id": "M005", "cropName": crop_type, "mandiName": "Solapur APMC", 
             "price": round(default_price * random.uniform(0.88, 1.08)), "trend": "stable", "spoilageRisk": default_spoilage},
        ]
    
    # Calculate options for each mandi
    mandi_options = []
    
    for item in market_items:
        mandi_name = item.get("mandiName", "Unknown Mandi")
        mandi_info = MANDI_DATABASE.get(mandi_name, {"location": "Unknown", "lat": 18.5204, "lon": 73.8567, "transport_rate_per_km": 3.5})
        
        # Calculate distance
        distance = calculate_distance(
            farmer_lat, farmer_lon,
            mandi_info.get("lat", 18.5204), mandi_info.get("lon", 73.8567)
        )
        
        # Calculate financials
        price_per_kg = item.get("price", default_price)
        revenue = price_per_kg * quantity_kg
        transport_cost = distance * mandi_info.get("transport_rate_per_km", 3.5) * (quantity_kg / 100)  # Cost scales with quantity
        net_profit = revenue - transport_cost
        profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
        
        mandi_options.append(MandiOption(
            mandi_id=item.get("id", "M000"),
            mandi_name=mandi_name,
            location=mandi_info.get("location", "Unknown"),
            current_price=price_per_kg,
            trend=item.get("trend", "stable"),
            spoilage_risk=item.get("spoilageRisk", "Medium"),
            distance_km=distance,
            estimated_revenue=round(revenue, 2),
            transport_cost=round(transport_cost, 2),
            net_profit=round(net_profit, 2),
            profit_margin_percent=round(profit_margin, 1),
            recommended=False,
            recommendation_reason=""
        ))
    
    # Sort by net profit (descending)
    mandi_options.sort(key=lambda x: x.net_profit, reverse=True)
    
    # Mark the best option
    if mandi_options:
        best = mandi_options[0]
        best.recommended = True
        best.recommendation_reason = f"Highest net profit (₹{best.net_profit:.0f}) with {best.profit_margin_percent}% margin"
        
        # Calculate profit gap
        if len(mandi_options) > 1:
            worst = mandi_options[-1]
            profit_gap = f"₹{best.net_profit - worst.net_profit:.0f} difference between best and worst option"
        else:
            profit_gap = "Single option available"
    else:
        profit_gap = "No market data available"
    
    # Get AI insights
    market_insight = await get_ai_market_insight(crop_type, quantity_kg, mandi_options)
    
    # Determine sell urgency based on spoilage risk
    spoilage_risks = [m.spoilage_risk for m in mandi_options]
    if "Critical" in spoilage_risks:
        sell_urgency = "immediate"
        urgency_reason = f"{crop_type} has high spoilage risk. Sell within 24 hours for best quality."
    elif "Medium" in spoilage_risks:
        sell_urgency = "within_24h"
        urgency_reason = f"Moderate spoilage risk for {crop_type}. Recommend selling within 48 hours."
    else:
        sell_urgency = "flexible"
        urgency_reason = f"{crop_type} has good shelf life. You can wait for better prices."
    
    # Price range
    if mandi_options:
        min_price = min(m.current_price for m in mandi_options)
        max_price = max(m.current_price for m in mandi_options)
        price_range = f"₹{min_price} - ₹{max_price} per kg"
    else:
        price_range = "No price data"
    
    return MarketAnalysis(
        farmer_id=farmer_id,
        farmer_name=farmer.get("name", "Unknown"),
        farmer_location=farmer.get("village", "Unknown"),
        crop_type=crop_type,
        quantity_kg=quantity_kg,
        mandi_options=mandi_options,
        best_mandi=mandi_options[0].mandi_name if mandi_options else "None",
        best_price=mandi_options[0].current_price if mandi_options else 0,
        best_profit=mandi_options[0].net_profit if mandi_options else 0,
        price_range=price_range,
        profit_gap=profit_gap,
        market_insight=market_insight,
        sell_urgency=sell_urgency,
        urgency_reason=urgency_reason,
        generated_at=datetime.utcnow().isoformat()
    )


async def get_ai_market_insight(crop_type: str, quantity_kg: float, options: List[MandiOption]) -> str:
    """Get AI-generated market insight"""
    
    if not GEMINI_AVAILABLE:
        return generate_rule_based_insight(crop_type, quantity_kg, options)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return generate_rule_based_insight(crop_type, quantity_kg, options)
    
    try:
        client = genai.Client(api_key=api_key)
        
        options_text = "\n".join([
            f"- {o.mandi_name}: ₹{o.current_price}/kg, Distance: {o.distance_km}km, Net Profit: ₹{o.net_profit}"
            for o in options[:5]
        ])
        
        prompt = f"""You are a market advisor for Indian farmers. Give a brief 2-3 sentence recommendation.

CROP: {crop_type}
QUANTITY: {quantity_kg} kg

MANDI OPTIONS:
{options_text}

Provide a simple, actionable recommendation focusing on which mandi to choose and why. Keep it farmer-friendly."""

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"⚠️ Gemini market insight error: {e}")
        return generate_rule_based_insight(crop_type, quantity_kg, options)


def generate_rule_based_insight(crop_type: str, quantity_kg: float, options: List[MandiOption]) -> str:
    """Generate rule-based market insight when AI is unavailable"""
    
    if not options:
        return f"No market data available for {crop_type}. Contact local mandi for current prices."
    
    best = options[0]
    
    if best.trend == "up":
        trend_advice = "Prices are rising - good time to sell!"
    elif best.trend == "down":
        trend_advice = "Prices are falling - consider selling soon before further drop."
    else:
        trend_advice = "Prices are stable."
    
    return f"Best option is {best.mandi_name} at ₹{best.current_price}/kg. " \
           f"You'll earn ₹{best.net_profit:.0f} after transport costs. {trend_advice}"


# ============================================================================
# DRIVER ASSIGNMENT
# ============================================================================

async def assign_driver_for_transport(
    db,
    farmer_id: str,
    farmer_phone: str,
    farmer_name: str,
    destination_mandi: str,
    crop_type: str,
    quantity_kg: float,
    expected_profit: float = 0
) -> Optional[DriverAssignment]:
    """
    Find and assign an available driver for crop transport
    Also updates farmer and driver records in the database
    
    Args:
        db: MongoDB database instance
        farmer_id: Farmer's ID
        farmer_phone: Farmer's phone number
        farmer_name: Farmer's name (from WhatsApp profile)
        destination_mandi: Selected mandi name
        crop_type: Type of crop
        quantity_kg: Quantity in kg
        expected_profit: Expected profit from sale
        
    Returns:
        DriverAssignment or None if no driver available
    """
    
    print(f"🚛 Assigning driver for {farmer_name} ({farmer_phone})")
    print(f"   Crop: {crop_type}, Quantity: {quantity_kg}kg, Mandi: {destination_mandi}")
    
    # Get or create farmer
    farmer = await db["farmers"].find_one({"id": farmer_id})
    if not farmer:
        # Create new farmer record
        farmer = {
            "id": farmer_id,
            "name": farmer_name or "Farmer",
            "phone": farmer_phone,
            "village": "Pune, Maharashtra",  # Default, can be updated later
            "status": "Connected",
            "rating": 4.5,
            "totalEarnings": 0,
            "history": [],
            "created_at": datetime.utcnow().isoformat()
        }
        await db["farmers"].insert_one(farmer)
        print(f"   ✅ Created new farmer record: {farmer_id}")
    else:
        # Update farmer name if we have a better one from WhatsApp
        if farmer_name and farmer_name != "Farmer" and farmer.get("name") in ["Unknown", "Farmer", None]:
            await db["farmers"].update_one(
                {"id": farmer_id},
                {"$set": {"name": farmer_name}}
            )
            farmer["name"] = farmer_name
    
    # Get available drivers
    available_drivers = await db["drivers"].find({"status": "Available"}).to_list(length=10)
    
    if not available_drivers:
        print(f"   ❌ No available drivers found")
        return None
    
    print(f"   Found {len(available_drivers)} available drivers")
    
    # Find driver with suitable vehicle capacity
    suitable_drivers = []
    for driver in available_drivers:
        vehicle_type = driver.get("vehicleType", "Tata Ace")
        capacity = VEHICLE_CAPACITIES.get(vehicle_type, 1000)
        
        if capacity >= quantity_kg:
            suitable_drivers.append((driver, capacity))
    
    # Sort by capacity (prefer smaller suitable vehicle)
    suitable_drivers.sort(key=lambda x: x[1])
    
    if not suitable_drivers:
        # If no suitable vehicle, use largest available
        driver = max(available_drivers, key=lambda d: VEHICLE_CAPACITIES.get(d.get("vehicleType", "Tata Ace"), 1000))
    else:
        driver = suitable_drivers[0][0]
    
    print(f"   Selected driver: {driver.get('name')} ({driver.get('id')})")
    
    # Get mandi info
    mandi_info = MANDI_DATABASE.get(destination_mandi, {"location": "Unknown", "lat": 18.5204, "lon": 73.8567, "transport_rate_per_km": 3.5})
    farmer_lat, farmer_lon = get_farmer_coordinates(farmer.get("village", "Pune, Maharashtra"))
    
    distance = calculate_distance(
        farmer_lat, farmer_lon,
        mandi_info.get("lat", 18.5204), mandi_info.get("lon", 73.8567)
    )
    
    transport_cost = distance * mandi_info.get("transport_rate_per_km", 3.5) * (quantity_kg / 100)
    
    # Generate booking ID
    booking_id = f"BK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Create assignment
    assignment = DriverAssignment(
        booking_id=booking_id,
        farmer_id=farmer_id,
        farmer_name=farmer.get("name", "Unknown"),
        farmer_phone=farmer_phone,
        driver_id=driver.get("id", "D000"),
        driver_name=driver.get("name", "Unknown"),
        driver_phone=driver.get("phone", "Unknown"),
        vehicle_type=driver.get("vehicleType", "Tata Ace"),
        vehicle_capacity_kg=VEHICLE_CAPACITIES.get(driver.get("vehicleType", "Tata Ace"), 1000),
        pickup_location=farmer.get("village", "Unknown"),
        destination_mandi=destination_mandi,
        crop_type=crop_type,
        quantity_kg=quantity_kg,
        estimated_distance_km=distance,
        estimated_cost=round(transport_cost, 2),
        status="assigned",
        assigned_at=datetime.utcnow().isoformat(),
        estimated_pickup_time="Within 2 hours"
    )
    
    # Update driver status in database
    await db["drivers"].update_one(
        {"id": driver.get("id")},
        {
            "$set": {
                "status": "Busy",
                "currentLoad": f"{quantity_kg}kg {crop_type}",
                "currentBooking": booking_id,
                "destination": destination_mandi,
                "lastUpdated": datetime.utcnow().isoformat()
            }
        }
    )
    print(f"   ✅ Updated driver {driver.get('id')} status to Busy")
    
    # Update farmer with transaction history
    transaction = {
        "booking_id": booking_id,
        "crop": crop_type,
        "quantity_kg": quantity_kg,
        "mandi": destination_mandi,
        "expected_profit": expected_profit,
        "driver_id": driver.get("id"),
        "driver_name": driver.get("name"),
        "status": "assigned",
        "created_at": datetime.utcnow().isoformat()
    }
    
    await db["farmers"].update_one(
        {"id": farmer_id},
        {
            "$push": {"history": transaction},
            "$set": {
                "status": "Connected",
                "lastActivity": datetime.utcnow().isoformat()
            },
            "$inc": {"totalEarnings": expected_profit}
        }
    )
    print(f"   ✅ Updated farmer {farmer_id} with transaction")
    
    # Store booking in database
    booking_data = assignment.model_dump()
    booking_data["expected_profit"] = expected_profit
    booking_data["farmer_profile_name"] = farmer_name
    await db["bookings"].insert_one(booking_data)
    print(f"   ✅ Created booking {booking_id}")
    
    return assignment


# ============================================================================
# WHATSAPP MESSAGE FORMATTERS
# ============================================================================

def format_market_options_message(analysis: MarketAnalysis) -> str:
    """Format market analysis as WhatsApp message"""
    
    msg = f"🌾 *Market Analysis for {analysis.crop_type}*\n"
    msg += f"📦 Quantity: {analysis.quantity_kg} kg\n\n"
    msg += f"📊 Price Range: {analysis.price_range}\n"
    msg += f"⏰ {analysis.urgency_reason}\n\n"
    msg += "━━━━━━━━━━━━━━━\n"
    msg += "*Available Mandis:*\n\n"
    
    for i, opt in enumerate(analysis.mandi_options[:5], 1):
        star = "⭐ " if opt.recommended else ""
        trend_icon = "📈" if opt.trend == "up" else "📉" if opt.trend == "down" else "➡️"
        
        msg += f"*{i}. {star}{opt.mandi_name}*\n"
        msg += f"   💰 ₹{opt.current_price}/kg {trend_icon}\n"
        msg += f"   📍 {opt.distance_km} km away\n"
        msg += f"   🚛 Transport: ₹{opt.transport_cost:.0f}\n"
        msg += f"   ✅ Net Profit: *₹{opt.net_profit:.0f}*\n\n"
    
    msg += "━━━━━━━━━━━━━━━\n"
    msg += f"💡 {analysis.market_insight}\n\n"
    msg += "*Reply with the number (1-5) to select a mandi*"
    
    return msg


def format_driver_assignment_message(assignment: DriverAssignment) -> str:
    """Format driver assignment as WhatsApp message"""
    
    msg = f"✅ *Booking Confirmed!*\n\n"
    msg += f"🎫 Booking ID: *{assignment.booking_id}*\n\n"
    msg += "━━━━━━━━━━━━━━━\n"
    msg += "*Driver Details:*\n"
    msg += f"👤 {assignment.driver_name}\n"
    msg += f"📞 {assignment.driver_phone}\n"
    msg += f"🚛 {assignment.vehicle_type}\n\n"
    msg += "━━━━━━━━━━━━━━━\n"
    msg += "*Trip Details:*\n"
    msg += f"📦 {assignment.quantity_kg}kg {assignment.crop_type}\n"
    msg += f"📍 From: {assignment.pickup_location}\n"
    msg += f"🏪 To: {assignment.destination_mandi}\n"
    msg += f"📏 Distance: {assignment.estimated_distance_km} km\n"
    msg += f"💰 Transport Cost: ₹{assignment.estimated_cost:.0f}\n\n"
    msg += f"⏰ *{assignment.estimated_pickup_time}*\n\n"
    msg += "Your driver will contact you shortly!"
    
    return msg


def format_crop_selection_message(farmer_name: str, available_crops: List[str]) -> str:
    """Format crop selection prompt"""
    
    msg = f"🙏 Namaste {farmer_name}!\n\n"
    msg += "Welcome to Neural Roots Market Assistant.\n\n"
    msg += "*Which crop do you want to sell today?*\n\n"
    
    for i, crop in enumerate(available_crops, 1):
        msg += f"{i}. {crop}\n"
    
    msg += "\n*Reply with the crop name or number*"
    
    return msg


def format_quantity_prompt_message(crop_type: str) -> str:
    """Format quantity input prompt"""
    
    msg = f"Great! You selected *{crop_type}*\n\n"
    msg += "📦 *How many kilograms do you want to sell?*\n\n"
    msg += "_Example: 100 or 250_"
    
    return msg


# ============================================================================
# CONVERSATION STATE MANAGEMENT
# ============================================================================

async def get_conversation_state(db, farmer_phone: str) -> Optional[ConversationState]:
    """Get current conversation state for a farmer"""
    state = await db["conversation_states"].find_one({"farmer_phone": farmer_phone})
    if state:
        state.pop("_id", None)
        return ConversationState(**state)
    return None


async def save_conversation_state(db, state: ConversationState):
    """Save conversation state"""
    await db["conversation_states"].update_one(
        {"farmer_phone": state.farmer_phone},
        {"$set": state.model_dump()},
        upsert=True
    )


async def clear_conversation_state(db, farmer_phone: str):
    """Clear conversation state"""
    await db["conversation_states"].delete_one({"farmer_phone": farmer_phone})


# ============================================================================
# MAIN CONVERSATION HANDLER
# ============================================================================

async def handle_market_conversation(
    db,
    farmer_phone: str,
    message: str,
    profile_name: Optional[str] = None
) -> str:
    """
    Handle WhatsApp conversation flow for market agent
    
    Args:
        db: MongoDB database instance
        farmer_phone: WhatsApp phone number (with whatsapp: prefix)
        message: The message text from farmer
        profile_name: WhatsApp profile name of the farmer
    
    Returns response message to send back
    """
    from datetime import timedelta
    
    # Normalize phone number
    clean_phone = farmer_phone.replace("whatsapp:", "").strip()
    
    # Get current conversation state
    state = await get_conversation_state(db, clean_phone)
    
    # Clean up the message
    message_lower = message.strip().lower()
    message_original = message.strip()  # Keep original case for names
    
    # Check for keywords to start new conversation
    start_keywords = ["sell", "mandi", "market", "price", "बेचना", "मंडी", "hi", "hello", "start"]
    
    if any(kw in message_lower for kw in start_keywords) or state is None:
        # Start new conversation
        # Find farmer by phone
        farmer = await db["farmers"].find_one({
            "phone": {"$regex": clean_phone[-10:]}  # Match last 10 digits
        })
        
        is_new_farmer = farmer is None
        
        if is_new_farmer:
            # New farmer - need to collect details
            new_state = ConversationState(
                farmer_id=f"F_{clean_phone[-10:]}",
                farmer_phone=clean_phone,
                farmer_name=profile_name,  # May be None
                is_new_farmer=True,
                current_step="awaiting_name",
                started_at=datetime.utcnow().isoformat(),
                last_interaction=datetime.utcnow().isoformat(),
                expires_at=(datetime.utcnow() + timedelta(hours=1)).isoformat()
            )
            await save_conversation_state(db, new_state)
            
            # Welcome message asking for name
            msg = "🙏 *Namaste! Welcome to Neural Roots*\n\n"
            msg += "I'm your agricultural assistant. I help farmers sell crops at the best prices.\n\n"
            msg += "Let me register you in our system first.\n\n"
            msg += "*What is your name?*\n"
            msg += "_Example: Ramesh Patil_"
            return msg
        else:
            # Existing farmer - go directly to crop selection
            farmer_name = farmer.get("name", profile_name or "Farmer")
            farmer_village = farmer.get("village", "Pune, Maharashtra")
            
            # Get crops this farmer has grown (from history or default)
            available_crops = ["Tomatoes", "Onions", "Potatoes", "Bananas", "Grapes", "Mangoes", "Other (type name)"]
            if farmer.get("history"):
                farmer_crops = list(set(h.get("crop") for h in farmer["history"] if h.get("crop")))
                if farmer_crops:
                    available_crops = farmer_crops + ["Other (type name)"]
            
            # Save initial state
            new_state = ConversationState(
                farmer_id=farmer.get("id"),
                farmer_phone=clean_phone,
                farmer_name=farmer_name,
                farmer_village=farmer_village,
                is_new_farmer=False,
                current_step="awaiting_crop",
                started_at=datetime.utcnow().isoformat(),
                last_interaction=datetime.utcnow().isoformat(),
                expires_at=(datetime.utcnow() + timedelta(hours=1)).isoformat()
            )
            await save_conversation_state(db, new_state)
            
            return format_crop_selection_message(farmer_name, available_crops)
    
    # Handle based on current step
    if state.current_step == "awaiting_name":
        # Farmer entered their name
        farmer_name = message_original.title()  # Capitalize properly
        
        # Update state
        state.farmer_name = farmer_name
        state.current_step = "awaiting_village"
        state.last_interaction = datetime.utcnow().isoformat()
        await save_conversation_state(db, state)
        
        msg = f"✅ Thank you, *{farmer_name}*!\n\n"
        msg += "*Which village/city are you from?*\n\n"
        msg += "_Examples:_\n"
        msg += "• Pune\n"
        msg += "• Nashik\n"
        msg += "• Satara\n"
        msg += "• Kolhapur\n"
        msg += "• Ahmednagar\n"
        msg += "• Or type your village name"
        return msg
    
    elif state.current_step == "awaiting_village":
        # Farmer entered their village
        village_input = message_original.title()
        
        # Try to match to known locations or create new
        known_locations = list(FARMER_LOCATIONS.keys())
        matched_village = None
        
        for loc in known_locations:
            if village_input.lower() in loc.lower() or loc.lower().startswith(village_input.lower()):
                matched_village = loc
                break
        
        if not matched_village:
            # Add Maharashtra suffix if just a city name
            if "maharashtra" not in village_input.lower():
                matched_village = f"{village_input}, Maharashtra"
            else:
                matched_village = village_input
        
        # Create farmer in database
        farmer_data = {
            "id": state.farmer_id,
            "name": state.farmer_name,
            "phone": state.farmer_phone,
            "village": matched_village,
            "status": "Connected",
            "rating": 4.5,
            "totalEarnings": 0,
            "history": [],
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db["farmers"].insert_one(farmer_data)
        print(f"✅ Created new farmer: {state.farmer_name} from {matched_village}")
        
        # Update state
        state.farmer_village = matched_village
        state.is_new_farmer = False
        state.current_step = "awaiting_crop"
        state.last_interaction = datetime.utcnow().isoformat()
        await save_conversation_state(db, state)
        
        # Show welcome and crop selection
        available_crops = ["Tomatoes", "Onions", "Potatoes", "Bananas", "Grapes", "Mangoes", "Other (type name)"]
        
        msg = f"🎉 *Welcome to Neural Roots, {state.farmer_name}!*\n\n"
        msg += f"📍 Location: {matched_village}\n\n"
        msg += "You're now registered in our network. You can sell your crops at the best mandi prices!\n\n"
        msg += "━━━━━━━━━━━━━━━\n\n"
        msg += "*Which crop do you want to sell today?*\n\n"
        
        for i, crop in enumerate(available_crops, 1):
            msg += f"{i}. {crop}\n"
        
        msg += "\n*Reply with the crop name or number*\n"
        msg += "_You can also type any crop name like: Ginger, Turmeric, Wheat, etc._"
        
        return msg
    
    elif state.current_step == "awaiting_crop":
        # Parse crop selection - accept BOTH numbers and free text crop names
        crop_map = {
            "1": "Tomatoes", "2": "Onions", "3": "Potatoes",
            "4": "Bananas", "5": "Grapes", "6": "Mangoes",
            "7": None,  # "Other" option - farmer will type name
            "tomatoes": "Tomatoes", "tomato": "Tomatoes", "टमाटर": "Tomatoes",
            "onions": "Onions", "onion": "Onions", "प्याज": "Onions",
            "potatoes": "Potatoes", "potato": "Potatoes", "aloo": "Potatoes", "आलू": "Potatoes",
            "bananas": "Bananas", "banana": "Bananas", "kela": "Bananas", "केला": "Bananas",
            "grapes": "Grapes", "grape": "Grapes", "angoor": "Grapes", "अंगूर": "Grapes",
            "mangoes": "Mangoes", "mango": "Mangoes", "aam": "Mangoes", "आम": "Mangoes",
        }
        
        # Check if user selected "other" or typed number 7
        if message_lower in ["7", "other"]:
            msg = "📝 *Type your crop name:*\n\n"
            msg += "_Example: Ginger, Wheat, Sugarcane, Cotton, etc._"
            
            state.current_step = "awaiting_custom_crop"
            state.last_interaction = datetime.utcnow().isoformat()
            await save_conversation_state(db, state)
            return msg
        
        # Get the crop from map or use the typed name directly
        selected_crop = crop_map.get(message_lower)
        
        if selected_crop is None:
            # User typed a custom crop name - capitalize it properly
            selected_crop = message_original.title()
        
        # Validate: check if we can find price info (from DB or defaults)
        crop_info = get_crop_default_price(selected_crop)
        
        # Update state
        state.selected_crop = selected_crop
        state.current_step = "awaiting_quantity"
        state.last_interaction = datetime.utcnow().isoformat()
        await save_conversation_state(db, state)
        
        # Show price hint if available
        price_hint = f"\n\n💰 _Current avg price: ~₹{crop_info['price']}/kg_" if crop_info else ""
        
        return format_quantity_prompt_message(selected_crop) + price_hint
    
    elif state.current_step == "awaiting_custom_crop":
        # User typed custom crop name
        selected_crop = message_original.title()
        
        # Update state
        state.selected_crop = selected_crop
        state.current_step = "awaiting_quantity"
        state.last_interaction = datetime.utcnow().isoformat()
        await save_conversation_state(db, state)
        
        crop_info = get_crop_default_price(selected_crop)
        price_hint = f"\n\n💰 _Current avg price: ~₹{crop_info['price']}/kg_" if crop_info else ""
        
        return format_quantity_prompt_message(selected_crop) + price_hint
    
    elif state.current_step == "awaiting_quantity":
        # Parse quantity
        try:
            # Extract number from message
            import re
            numbers = re.findall(r'\d+', message_lower)
            if numbers:
                quantity = float(numbers[0])
            else:
                return "❌ Please enter a valid quantity in kg.\n\n_Example: 100 or 250_"
        except:
            return "❌ Please enter a valid quantity in kg.\n\n_Example: 100 or 250_"
        
        if quantity <= 0 or quantity > 10000:
            return "❌ Please enter a quantity between 1 and 10000 kg."
        
        # Get market analysis
        analysis = await analyze_market_for_crop(
            db,
            state.farmer_id,
            state.selected_crop,
            quantity
        )
        
        # Update state
        state.quantity_kg = quantity
        state.market_analysis = analysis.model_dump()
        state.current_step = "awaiting_mandi_choice"
        state.last_interaction = datetime.utcnow().isoformat()
        await save_conversation_state(db, state)
        
        return format_market_options_message(analysis)
    
    elif state.current_step == "awaiting_mandi_choice":
        # Parse mandi selection
        try:
            choice = int(message)
            if choice < 1 or choice > len(state.market_analysis.get("mandi_options", [])):
                return f"❌ Please select a number between 1 and {len(state.market_analysis.get('mandi_options', []))}"
            
            selected_option = state.market_analysis["mandi_options"][choice - 1]
            selected_mandi = selected_option["mandi_name"]
            expected_profit = selected_option.get("net_profit", 0)
        except:
            # Try to match mandi name
            mandi_options = state.market_analysis.get("mandi_options", [])
            selected_mandi = None
            expected_profit = 0
            for opt in mandi_options:
                if opt["mandi_name"].lower() in message_lower:
                    selected_mandi = opt["mandi_name"]
                    expected_profit = opt.get("net_profit", 0)
                    break
            
            if not selected_mandi:
                return "❌ Please reply with a number (1-5) to select a mandi."
        
        # Update state with mandi and expected profit
        state.selected_mandi = selected_mandi
        state.expected_profit = expected_profit
        state.current_step = "awaiting_confirmation"
        state.last_interaction = datetime.utcnow().isoformat()
        await save_conversation_state(db, state)
        
        # Ask for confirmation
        selected_opt = next((o for o in state.market_analysis["mandi_options"] if o["mandi_name"] == selected_mandi), None)
        
        msg = f"📋 *Order Summary*\n\n"
        msg += f"🌾 Crop: {state.selected_crop}\n"
        msg += f"📦 Quantity: {state.quantity_kg} kg\n"
        msg += f"🏪 Mandi: {selected_mandi}\n"
        if selected_opt:
            msg += f"💰 Expected Profit: ₹{selected_opt['net_profit']:.0f}\n"
        msg += "\n*Reply 'YES' to confirm and get a driver assigned*\n"
        msg += "_Reply 'NO' to cancel_"
        
        return msg
    
    elif state.current_step == "awaiting_confirmation":
        if message_lower in ["yes", "y", "haan", "ha", "confirm", "ok"]:
            # Assign driver with farmer details
            assignment = await assign_driver_for_transport(
                db=db,
                farmer_id=state.farmer_id,
                farmer_phone=clean_phone,
                farmer_name=state.farmer_name or "Farmer",
                destination_mandi=state.selected_mandi,
                crop_type=state.selected_crop,
                quantity_kg=state.quantity_kg,
                expected_profit=state.expected_profit or 0
            )
            
            # Clear conversation state
            await clear_conversation_state(db, clean_phone)
            
            if assignment:
                return format_driver_assignment_message(assignment)
            else:
                return "❌ Sorry, no drivers are available right now. Please try again in some time.\n\n_Reply 'sell' to start again_"
        
        elif message_lower in ["no", "n", "nahi", "cancel"]:
            await clear_conversation_state(db, clean_phone)
            return "❌ Order cancelled.\n\n_Reply 'sell' to start a new order_"
        
        else:
            return "Please reply *YES* to confirm or *NO* to cancel."
    
    else:
        # Unknown state, reset
        await clear_conversation_state(db, clean_phone)
        return "🙏 Welcome! Reply *sell* to start selling your crops."


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "MandiOption",
    "MarketAnalysis",
    "DriverAssignment",
    "ConversationState",
    "analyze_market_for_crop",
    "assign_driver_for_transport",
    "handle_market_conversation",
    "format_market_options_message",
    "format_driver_assignment_message",
]
