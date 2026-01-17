# backend/app/agents/weather_agent.py
"""
Weather Prediction Agent
Analyzes weather forecasts and alerts farmers about conditions
that could affect crop health and spoilage
"""

import os
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Import weather API service
from app.services.weather_api import (
    get_weather_forecast,
    get_weather_by_city,
    get_forecast_by_city,
    WeatherForecast,
    WeatherCondition,
    ForecastItem,
    MAHARASHTRA_LOCATIONS
)

# Try to import Gemini
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-genai not installed, using rule-based weather analysis")


# ============================================================================
# DATA MODELS
# ============================================================================

class WeatherAlert(BaseModel):
    """Single weather alert for farmer"""
    alert_type: str         # "rain", "heat", "cold", "wind", "storm", "humidity"
    severity: str           # "low", "medium", "high", "critical"
    title: str
    message: str
    expected_time: str      # When the weather event is expected
    duration_hours: int     # How long it will last
    affected_crops: List[str]


class CropPrecaution(BaseModel):
    """Precautionary measure for a specific crop"""
    crop_name: str
    risk_level: str         # "low", "medium", "high"
    risks: List[str]
    precautions: List[str]
    harvest_recommendation: Optional[str] = None


class WeatherPrediction(BaseModel):
    """Complete weather prediction and farmer alerts"""
    farmer_id: str
    farmer_name: str
    location: str
    lat: float
    lon: float
    
    # Current conditions
    current_temp: float
    current_humidity: int
    current_conditions: str
    
    # Forecast summary
    forecast_summary: str
    
    # Alerts (sorted by severity)
    alerts: List[WeatherAlert]
    
    # Crop-specific precautions
    crop_precautions: List[CropPrecaution]
    
    # Overall risk assessment
    overall_risk: str       # "low", "medium", "high", "critical"
    risk_score: int         # 0-100
    
    # Recommended actions
    immediate_actions: List[str]
    next_24h_actions: List[str]
    next_week_actions: List[str]
    
    # Timestamps
    generated_at: str
    valid_until: str


# ============================================================================
# CROP RISK PROFILES
# ============================================================================

CROP_WEATHER_SENSITIVITY = {
    "tomatoes": {
        "max_temp": 35,
        "min_temp": 10,
        "optimal_humidity": (60, 80),
        "rain_tolerance": "medium",
        "wind_tolerance": "low",
        "risks": ["heat stress", "fungal diseases in rain", "fruit cracking"]
    },
    "potatoes": {
        "max_temp": 30,
        "min_temp": 5,
        "optimal_humidity": (65, 85),
        "rain_tolerance": "medium",
        "wind_tolerance": "medium",
        "risks": ["late blight in rain", "heat damage", "tuber rot"]
    },
    "onions": {
        "max_temp": 35,
        "min_temp": 10,
        "optimal_humidity": (50, 70),
        "rain_tolerance": "low",
        "wind_tolerance": "high",
        "risks": ["purple blotch in rain", "bulb rot", "bacterial infections"]
    },
    "bananas": {
        "max_temp": 38,
        "min_temp": 15,
        "optimal_humidity": (70, 90),
        "rain_tolerance": "high",
        "wind_tolerance": "low",
        "risks": ["wind damage to leaves", "panama disease", "cold damage"]
    },
    "mangoes": {
        "max_temp": 40,
        "min_temp": 10,
        "optimal_humidity": (50, 70),
        "rain_tolerance": "low",
        "wind_tolerance": "medium",
        "risks": ["anthracnose in rain", "flower drop", "fruit fly"]
    },
    "grapes": {
        "max_temp": 38,
        "min_temp": 5,
        "optimal_humidity": (40, 60),
        "rain_tolerance": "low",
        "wind_tolerance": "medium",
        "risks": ["downy mildew", "berry splitting", "fungal rot"]
    },
    "sugarcane": {
        "max_temp": 40,
        "min_temp": 15,
        "optimal_humidity": (70, 85),
        "rain_tolerance": "high",
        "wind_tolerance": "medium",
        "risks": ["red rot in waterlogging", "lodging in storms"]
    },
    "cotton": {
        "max_temp": 38,
        "min_temp": 15,
        "optimal_humidity": (50, 70),
        "rain_tolerance": "medium",
        "wind_tolerance": "medium",
        "risks": ["boll rot in rain", "pest infestations"]
    },
    "wheat": {
        "max_temp": 30,
        "min_temp": 5,
        "optimal_humidity": (50, 70),
        "rain_tolerance": "medium",
        "wind_tolerance": "medium",
        "risks": ["rust diseases", "lodging in rain"]
    },
    "rice": {
        "max_temp": 38,
        "min_temp": 15,
        "optimal_humidity": (70, 90),
        "rain_tolerance": "very_high",
        "wind_tolerance": "medium",
        "risks": ["blast disease", "bacterial blight"]
    }
}


# ============================================================================
# WEATHER ANALYSIS FUNCTIONS
# ============================================================================

def analyze_forecast_for_alerts(forecast: WeatherForecast, farmer_crops: List[str]) -> List[WeatherAlert]:
    """
    Analyze forecast and generate weather alerts
    """
    alerts = []
    
    # Group forecasts by day
    daily_forecasts = {}
    for f in forecast.forecasts:
        date = f.datetime.split(" ")[0]
        if date not in daily_forecasts:
            daily_forecasts[date] = []
        daily_forecasts[date].append(f)
    
    for date, day_forecasts in daily_forecasts.items():
        # Check for rain
        rain_periods = [f for f in day_forecasts if f.rain_probability > 0.5 or f.weather_main in ["Rain", "Thunderstorm"]]
        if rain_periods:
            total_rain = sum(f.rain_volume or 0 for f in rain_periods)
            severity = "critical" if total_rain > 30 else "high" if total_rain > 15 else "medium" if total_rain > 5 else "low"
            
            affected = [crop for crop in farmer_crops 
                       if CROP_WEATHER_SENSITIVITY.get(crop.lower(), {}).get("rain_tolerance") in ["low", "medium"]]
            
            if affected or severity in ["high", "critical"]:
                alerts.append(WeatherAlert(
                    alert_type="rain",
                    severity=severity,
                    title=f"🌧️ Rain Expected on {date}",
                    message=f"Expected rainfall: {total_rain:.1f}mm. {len(rain_periods)} periods of rain predicted.",
                    expected_time=rain_periods[0].datetime,
                    duration_hours=len(rain_periods) * 3,
                    affected_crops=affected or farmer_crops
                ))
        
        # Check for high temperature
        high_temps = [f for f in day_forecasts if f.temperature > 38]
        if high_temps:
            max_temp = max(f.temperature for f in high_temps)
            severity = "critical" if max_temp > 42 else "high" if max_temp > 40 else "medium"
            
            affected = [crop for crop in farmer_crops 
                       if CROP_WEATHER_SENSITIVITY.get(crop.lower(), {}).get("max_temp", 40) < max_temp]
            
            if affected:
                alerts.append(WeatherAlert(
                    alert_type="heat",
                    severity=severity,
                    title=f"🔥 Extreme Heat Warning for {date}",
                    message=f"Temperature expected to reach {max_temp}°C. Heat stress risk for crops.",
                    expected_time=high_temps[0].datetime,
                    duration_hours=len(high_temps) * 3,
                    affected_crops=affected
                ))
        
        # Check for storms
        storms = [f for f in day_forecasts if "Thunderstorm" in f.weather_main or "storm" in f.weather_description.lower()]
        if storms:
            alerts.append(WeatherAlert(
                alert_type="storm",
                severity="high",
                title=f"⛈️ Storm Warning for {date}",
                message=f"Thunderstorms expected. Secure equipment and protect vulnerable crops.",
                expected_time=storms[0].datetime,
                duration_hours=len(storms) * 3,
                affected_crops=farmer_crops
            ))
        
        # Check for high winds
        windy = [f for f in day_forecasts if f.wind_speed > 10]
        if windy:
            max_wind = max(f.wind_speed for f in windy)
            severity = "high" if max_wind > 15 else "medium"
            
            affected = [crop for crop in farmer_crops 
                       if CROP_WEATHER_SENSITIVITY.get(crop.lower(), {}).get("wind_tolerance") == "low"]
            
            if affected:
                alerts.append(WeatherAlert(
                    alert_type="wind",
                    severity=severity,
                    title=f"💨 High Wind Alert for {date}",
                    message=f"Wind speeds up to {max_wind:.1f} m/s expected. Support tall crops and banana plants.",
                    expected_time=windy[0].datetime,
                    duration_hours=len(windy) * 3,
                    affected_crops=affected
                ))
        
        # Check for high humidity (disease risk)
        humid = [f for f in day_forecasts if f.humidity > 85]
        if len(humid) >= 4:  # Multiple high humidity periods
            alerts.append(WeatherAlert(
                alert_type="humidity",
                severity="medium",
                title=f"💧 High Humidity Alert for {date}",
                message="Extended high humidity (>85%) increases fungal disease risk. Consider preventive fungicide.",
                expected_time=humid[0].datetime,
                duration_hours=len(humid) * 3,
                affected_crops=farmer_crops
            ))
    
    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda x: severity_order.get(x.severity, 4))
    
    return alerts


def generate_crop_precautions(forecast: WeatherForecast, crops: List[str], alerts: List[WeatherAlert]) -> List[CropPrecaution]:
    """
    Generate crop-specific precautions based on weather
    """
    precautions = []
    
    # Get next 3 days average conditions
    next_3_days = forecast.forecasts[:24]  # 8 periods/day * 3 days
    avg_temp = sum(f.temperature for f in next_3_days) / len(next_3_days)
    avg_humidity = sum(f.humidity for f in next_3_days) / len(next_3_days)
    rain_expected = any(f.rain_probability > 0.5 for f in next_3_days)
    
    for crop in crops:
        crop_lower = crop.lower()
        sensitivity = CROP_WEATHER_SENSITIVITY.get(crop_lower, {})
        
        risks = []
        crop_precautions = []
        harvest_rec = None
        
        # Temperature risks
        max_temp_threshold = sensitivity.get("max_temp", 35)
        if avg_temp > max_temp_threshold:
            risks.append(f"Heat stress (avg temp {avg_temp:.1f}°C exceeds {max_temp_threshold}°C threshold)")
            crop_precautions.extend([
                "Apply mulch to reduce soil temperature",
                "Water crops during early morning or evening",
                "Consider shade nets for sensitive crops"
            ])
        
        # Rain risks
        rain_tolerance = sensitivity.get("rain_tolerance", "medium")
        if rain_expected and rain_tolerance in ["low", "medium"]:
            risks.append("Fungal disease risk due to rain")
            crop_precautions.extend([
                "Apply preventive fungicide before rain",
                "Ensure proper drainage in fields",
                "Avoid harvesting immediately after rain"
            ])
            if rain_tolerance == "low":
                harvest_rec = "Consider early harvest before heavy rain to prevent crop damage"
        
        # Humidity risks
        optimal_humidity = sensitivity.get("optimal_humidity", (50, 80))
        if avg_humidity > optimal_humidity[1]:
            risks.append(f"High humidity ({avg_humidity:.0f}%) increases disease risk")
            crop_precautions.append("Increase plant spacing for air circulation")
        
        # Determine risk level
        alert_severities = [a.severity for a in alerts if crop in a.affected_crops]
        if "critical" in alert_severities:
            risk_level = "high"
        elif "high" in alert_severities or len(risks) >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        precautions.append(CropPrecaution(
            crop_name=crop,
            risk_level=risk_level,
            risks=risks or ["No significant weather risks"],
            precautions=crop_precautions or ["Continue normal farming practices"],
            harvest_recommendation=harvest_rec
        ))
    
    # Sort by risk level
    risk_order = {"high": 0, "medium": 1, "low": 2}
    precautions.sort(key=lambda x: risk_order.get(x.risk_level, 3))
    
    return precautions


def calculate_overall_risk(alerts: List[WeatherAlert], precautions: List[CropPrecaution]) -> tuple:
    """Calculate overall risk level and score"""
    if not alerts:
        return "low", 15
    
    severity_scores = {"critical": 100, "high": 75, "medium": 50, "low": 25}
    risk_scores = {"high": 80, "medium": 50, "low": 20}
    
    # Factor in alert severities
    alert_score = max(severity_scores.get(a.severity, 0) for a in alerts) if alerts else 0
    
    # Factor in crop risks
    crop_score = max(risk_scores.get(p.risk_level, 0) for p in precautions) if precautions else 0
    
    # Combined score
    final_score = int((alert_score * 0.6) + (crop_score * 0.4))
    
    if final_score >= 80:
        return "critical", final_score
    elif final_score >= 60:
        return "high", final_score
    elif final_score >= 40:
        return "medium", final_score
    else:
        return "low", final_score


def generate_action_items(alerts: List[WeatherAlert], precautions: List[CropPrecaution]) -> tuple:
    """Generate prioritized action items"""
    immediate = []
    next_24h = []
    next_week = []
    
    # Immediate actions (critical/high alerts)
    for alert in alerts:
        if alert.severity in ["critical", "high"]:
            if alert.alert_type == "rain":
                immediate.append("Cover harvested crops and exposed produce")
                immediate.append("Check and clear drainage channels")
            elif alert.alert_type == "heat":
                immediate.append("Increase irrigation frequency")
                immediate.append("Harvest ripe produce early morning")
            elif alert.alert_type == "storm":
                immediate.append("Secure farming equipment and structures")
                immediate.append("Support tall plants and banana crops")
            elif alert.alert_type == "wind":
                immediate.append("Install windbreaks if possible")
                immediate.append("Stake vulnerable plants")
    
    # Next 24 hours
    for precaution in precautions:
        if precaution.risk_level in ["high", "medium"]:
            if precaution.harvest_recommendation:
                next_24h.append(precaution.harvest_recommendation)
            next_24h.extend(precaution.precautions[:2])
    
    # Next week
    next_week = [
        "Monitor crops daily for disease symptoms",
        "Prepare storage facilities for harvested crops",
        "Review irrigation schedule based on weather",
        "Stock necessary pesticides and fungicides"
    ]
    
    # Remove duplicates while preserving order
    immediate = list(dict.fromkeys(immediate))[:5]
    next_24h = list(dict.fromkeys(next_24h))[:5]
    next_week = list(dict.fromkeys(next_week))[:4]
    
    return immediate, next_24h, next_week


# ============================================================================
# AI-ENHANCED ANALYSIS (with Gemini)
# ============================================================================

async def get_ai_weather_insights(forecast: WeatherForecast, crops: List[str], alerts: List[WeatherAlert]) -> Optional[str]:
    """
    Use Gemini AI for enhanced weather insights
    """
    if not GEMINI_AVAILABLE:
        return None
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Prepare weather summary
        next_3_days = forecast.forecasts[:24]
        temps = [f.temperature for f in next_3_days]
        
        prompt = f"""You are an agricultural weather advisor for Indian farmers in Maharashtra.

WEATHER DATA:
- Location: {forecast.location}, India
- Next 3 days temperature range: {min(temps):.1f}°C to {max(temps):.1f}°C
- Rain probability: {max(f.rain_probability for f in next_3_days) * 100:.0f}%
- Current alerts: {len(alerts)} ({', '.join(a.alert_type for a in alerts) if alerts else 'None'})

FARMER'S CROPS: {', '.join(crops)}

ALERTS: 
{chr(10).join(f'- {a.title}: {a.message}' for a in alerts[:3]) if alerts else 'No critical alerts'}

Provide a brief (2-3 sentences) personalized weather advisory for this farmer in simple language. 
Focus on the most important action they should take. Be specific to their crops.
Respond in English but keep it simple for farmers."""

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"⚠️ Gemini weather insights error: {e}")
        return None


# ============================================================================
# MAIN AGENT FUNCTION
# ============================================================================

async def predict_weather_for_farmer(
    farmer_id: str,
    farmer_name: str,
    location: str,
    crops: List[str],
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> WeatherPrediction:
    """
    Main function to generate complete weather prediction for a farmer
    
    Args:
        farmer_id: Unique farmer identifier
        farmer_name: Farmer's name
        location: Location name (city/village)
        crops: List of crops the farmer grows
        lat: Optional latitude (will lookup from location if not provided)
        lon: Optional longitude
        
    Returns:
        WeatherPrediction with alerts and recommendations
    """
    
    # Get coordinates if not provided
    if lat is None or lon is None:
        loc_lower = location.lower().replace(" ", "")
        for loc_name, coords in MAHARASHTRA_LOCATIONS.items():
            if loc_name in loc_lower or loc_lower in loc_name:
                lat = coords["lat"]
                lon = coords["lon"]
                break
        else:
            # Default to Pune
            lat = 18.5204
            lon = 73.8567
    
    # Fetch weather data
    current_weather = await get_weather_by_city(location)
    forecast = await get_forecast_by_city(location)
    
    # Analyze forecast
    alerts = analyze_forecast_for_alerts(forecast, crops)
    
    # Generate crop precautions
    crop_precautions = generate_crop_precautions(forecast, crops, alerts)
    
    # Calculate risk
    overall_risk, risk_score = calculate_overall_risk(alerts, crop_precautions)
    
    # Generate actions
    immediate, next_24h, next_week = generate_action_items(alerts, crop_precautions)
    
    # Get AI insights
    ai_summary = await get_ai_weather_insights(forecast, crops, alerts)
    
    # Generate forecast summary
    next_3_days = forecast.forecasts[:24]
    temps = [f.temperature for f in next_3_days]
    rain_days = sum(1 for f in next_3_days if f.rain_probability > 0.5)
    
    forecast_summary = ai_summary or f"Next 3 days: {min(temps):.0f}-{max(temps):.0f}°C. " \
                       f"{'Rain expected.' if rain_days > 4 else 'Mostly dry conditions.'} " \
                       f"Overall risk level: {overall_risk.upper()}."
    
    return WeatherPrediction(
        farmer_id=farmer_id,
        farmer_name=farmer_name,
        location=forecast.location,
        lat=lat,
        lon=lon,
        current_temp=current_weather.temperature,
        current_humidity=current_weather.humidity,
        current_conditions=current_weather.weather_description,
        forecast_summary=forecast_summary,
        alerts=alerts,
        crop_precautions=crop_precautions,
        overall_risk=overall_risk,
        risk_score=risk_score,
        immediate_actions=immediate or ["No immediate actions required"],
        next_24h_actions=next_24h or ["Continue regular farming practices"],
        next_week_actions=next_week,
        generated_at=datetime.utcnow().isoformat(),
        valid_until=(datetime.utcnow() + timedelta(hours=12)).isoformat()
    )


# ============================================================================
# BATCH PROCESSING
# ============================================================================

async def predict_weather_for_all_farmers(db) -> List[WeatherPrediction]:
    """
    Generate weather predictions for all farmers in database
    """
    predictions = []
    
    farmers_collection = db["farmers"]
    farmers = await farmers_collection.find().to_list(length=100)
    
    for farmer in farmers:
        prediction = await predict_weather_for_farmer(
            farmer_id=str(farmer["_id"]),
            farmer_name=farmer.get("name", "Unknown"),
            location=farmer.get("location", "Pune"),
            crops=farmer.get("crops", ["tomatoes"]),
            lat=farmer.get("coordinates", {}).get("lat"),
            lon=farmer.get("coordinates", {}).get("lon")
        )
        predictions.append(prediction)
    
    return predictions


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "WeatherAlert",
    "CropPrecaution", 
    "WeatherPrediction",
    "predict_weather_for_farmer",
    "predict_weather_for_all_farmers",
    "CROP_WEATHER_SENSITIVITY"
]
