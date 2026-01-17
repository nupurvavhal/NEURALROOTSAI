# backend/app/agents/freshness_agent.py
"""
Freshness Analysis Agent
Receives IoT sensor data + crop classification from ML model
Sends to Gemini API for freshness analysis and predictions
"""

import os
import json
from google import genai
from google.genai import types
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API with new SDK
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# ============================================================================
# INPUT/OUTPUT SCHEMAS
# ============================================================================

class SensorInput(BaseModel):
    """Input from IoT sensors + ML model"""
    farmer_id: str
    device_id: str
    crop_type: str
    
    # From IoT sensors
    temperature: float      # Celsius
    humidity: float         # Percentage 0-100
    
    # From trained classification model (Google Colab)
    crop_classification: str  # "fresh" or "rotten"
    
    # Optional metadata
    image_url: Optional[str] = None
    location: Optional[str] = None


class FreshnessAnalysis(BaseModel):
    """Output from Gemini API analysis"""
    freshness_score: int          # 0-100
    health_status: str            # "excellent", "good", "warning", "critical"
    shelf_life_hours: int         # Predicted remaining shelf life
    alert_generated: bool
    alert_type: Optional[str] = None
    alert_message: Optional[str] = None
    recommendations: list[str] = []
    confidence: float             # 0-1
    analyzed_at: str


# ============================================================================
# GEMINI ANALYSIS AGENT
# ============================================================================

async def analyze_freshness(sensor_data: SensorInput) -> FreshnessAnalysis:
    """
    Analyze crop freshness using Gemini AI
    
    Args:
        sensor_data: IoT sensor readings + ML classification
        
    Returns:
        FreshnessAnalysis with predictions and recommendations
    """
    
    # Build prompt for Gemini
    prompt = f"""
You are an expert agricultural AI analyzing crop freshness for supply chain optimization.

**Sensor Data Analysis:**
- Crop Type: {sensor_data.crop_type}
- ML Classification: {sensor_data.crop_classification}
- Temperature: {sensor_data.temperature}°C
- Humidity: {sensor_data.humidity}%
- Farmer ID: {sensor_data.farmer_id}
- Device ID: {sensor_data.device_id}

**Your Task:**
Analyze the above data and provide a detailed freshness assessment. Consider:
1. The ML model classified the crop as: {sensor_data.crop_classification}
2. Temperature and humidity impact on {sensor_data.crop_type}
3. Optimal storage conditions for {sensor_data.crop_type}
4. Risk factors and shelf life prediction

**Respond in this exact JSON format:**
{{
    "freshness_score": <integer 0-100>,
    "health_status": "<excellent|good|warning|critical>",
    "shelf_life_hours": <integer hours remaining>,
    "alert_generated": <true|false>,
    "alert_type": "<temperature_high|temperature_low|humidity_high|humidity_low|spoilage_detected|null>",
    "alert_message": "<message or null>",
    "recommendations": ["recommendation 1", "recommendation 2", ...],
    "confidence": <float 0-1>
}}

**Guidelines:**
- If classification is "rotten", freshness_score < 40, health_status should be "critical"
- If classification is "fresh" with good conditions, freshness_score > 80
- Generate alert if temperature/humidity is outside optimal range
- Shelf life depends on crop type and current conditions
- Provide 2-4 actionable recommendations

Respond ONLY with valid JSON, no additional text.
"""

    try:
        # Call Gemini API with new SDK
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parse JSON response
        analysis_data = json.loads(response_text)
        
        # Add timestamp
        analysis_data["analyzed_at"] = datetime.utcnow().isoformat()
        
        # Create and return FreshnessAnalysis object
        return FreshnessAnalysis(**analysis_data)
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Gemini response: {e}")
        print(f"Raw response: {response_text}")
        
        # Fallback analysis based on classification
        return create_fallback_analysis(sensor_data)
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return create_fallback_analysis(sensor_data)


def create_fallback_analysis(sensor_data: SensorInput) -> FreshnessAnalysis:
    """
    Fallback analysis if Gemini API fails
    Uses rule-based logic based on ML classification and sensor data
    """
    
    # Base score on ML classification
    if sensor_data.crop_classification.lower() == "rotten":
        freshness_score = 30
        health_status = "critical"
        shelf_life_hours = 12
        alert_generated = True
        alert_type = "spoilage_detected"
        alert_message = f"{sensor_data.crop_type} classified as rotten - immediate action required"
    else:  # fresh
        freshness_score = 85
        health_status = "good"
        shelf_life_hours = 72
        alert_generated = False
        alert_type = None
        alert_message = None
    
    # Adjust for temperature
    if sensor_data.temperature > 35:
        freshness_score -= 20
        health_status = "warning"
        alert_generated = True
        alert_type = "temperature_high"
        alert_message = f"High temperature ({sensor_data.temperature}°C) detected"
        shelf_life_hours = max(24, shelf_life_hours // 2)
    elif sensor_data.temperature < 5:
        freshness_score -= 10
        alert_generated = True
        alert_type = "temperature_low"
        alert_message = f"Low temperature ({sensor_data.temperature}°C) may cause damage"
    
    # Adjust for humidity
    if sensor_data.humidity > 85:
        freshness_score -= 15
        if not alert_generated:
            alert_generated = True
            alert_type = "humidity_high"
            alert_message = f"High humidity ({sensor_data.humidity}%) increases spoilage risk"
    
    freshness_score = max(0, min(100, freshness_score))
    
    return FreshnessAnalysis(
        freshness_score=freshness_score,
        health_status=health_status,
        shelf_life_hours=shelf_life_hours,
        alert_generated=alert_generated,
        alert_type=alert_type,
        alert_message=alert_message,
        recommendations=[
            "Monitor storage conditions regularly",
            "Consider immediate sale or processing if critical",
            "Maintain optimal temperature and humidity"
        ],
        confidence=0.75,
        analyzed_at=datetime.utcnow().isoformat()
    )


# ============================================================================
# BATCH ANALYSIS
# ============================================================================

async def analyze_batch(sensor_readings: list[SensorInput]) -> list[FreshnessAnalysis]:
    """
    Analyze multiple sensor readings in batch
    
    Args:
        sensor_readings: List of sensor data
        
    Returns:
        List of freshness analyses
    """
    results = []
    for reading in sensor_readings:
        try:
            analysis = await analyze_freshness(reading)
            results.append(analysis)
        except Exception as e:
            print(f"❌ Error analyzing {reading.farmer_id}: {e}")
            results.append(create_fallback_analysis(reading))
    
    return results


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_optimal_conditions(crop_type: str) -> Dict[str, tuple]:
    """
    Get optimal temperature and humidity ranges for different crops
    
    Returns:
        dict with (min_temp, max_temp, min_humidity, max_humidity)
    """
    conditions = {
        "tomatoes": (10, 21, 85, 95),
        "potatoes": (4, 10, 85, 95),
        "onions": (0, 4, 65, 70),
        "grapes": (0, 2, 90, 95),
        "bananas": (13, 15, 85, 90),
        "mangoes": (10, 13, 85, 90),
        "wheat": (15, 25, 40, 60),
        "rice": (12, 15, 12, 14),
        "sugarcane": (20, 30, 70, 80),
    }
    
    return conditions.get(crop_type.lower(), (15, 25, 60, 80))  # Default


def is_within_optimal_range(sensor_data: SensorInput) -> bool:
    """Check if sensor readings are within optimal range for the crop"""
    min_temp, max_temp, min_hum, max_hum = get_optimal_conditions(sensor_data.crop_type)
    
    temp_ok = min_temp <= sensor_data.temperature <= max_temp
    hum_ok = min_hum <= sensor_data.humidity <= max_hum
    
    return temp_ok and hum_ok


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "SensorInput",
    "FreshnessAnalysis",
    "analyze_freshness",
    "analyze_batch",
    "get_optimal_conditions",
    "is_within_optimal_range"
]
