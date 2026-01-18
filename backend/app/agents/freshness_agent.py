# backend/app/agents/freshness_agent.py
"""
Freshness Agent - Predicts crop/vegetable/fruit freshness based on IoT data and ML model
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np

class FreshnessAgent:
    """
    Analyzes temperature, humidity, and age data to predict freshness levels.
    Uses ML thresholds and historical patterns.
    """
    
    def __init__(self):
        self.freshness_thresholds = {
            "tomato": {"temp_optimal": (20, 25), "humidity_optimal": (85, 95), "shelf_life": 7},
            "onion": {"temp_optimal": (0, 5), "humidity_optimal": (65, 70), "shelf_life": 60},
            "mango": {"temp_optimal": (13, 18), "humidity_optimal": (80, 90), "shelf_life": 14},
            "potato": {"temp_optimal": (4, 10), "humidity_optimal": (85, 95), "shelf_life": 90},
            "carrot": {"temp_optimal": (0, 4), "humidity_optimal": (90, 95), "shelf_life": 60},
            "cucumber": {"temp_optimal": (10, 15), "humidity_optimal": (85, 90), "shelf_life": 5},
            "leafy_greens": {"temp_optimal": (0, 5), "humidity_optimal": (90, 95), "shelf_life": 3},
        }
    
    def get_crop_type(self, crop_name: str) -> str:
        """Normalize crop name to known types"""
        crop_lower = crop_name.lower()
        
        # Map common crop names to categories
        mapping = {
            "tomato": "tomato",
            "onion": "onion",
            "mango": "mango",
            "potato": "potato",
            "carrot": "carrot",
            "cucumber": "cucumber",
            "lettuce": "leafy_greens",
            "spinach": "leafy_greens",
            "kale": "leafy_greens",
        }
        
        for key, value in mapping.items():
            if key in crop_lower:
                return value
        
        # Default to generic vegetable thresholds
        return "tomato"
    
    async def predict_freshness(
        self,
        crop_name: str,
        temperature: float,
        humidity: float,
        age_hours: Optional[float] = None,
        iot_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Predict freshness level based on conditions
        
        Args:
            crop_name: Name of the crop
            temperature: Current temperature in Celsius
            humidity: Current humidity percentage
            age_hours: Hours since harvest/storage
            iot_data: Optional raw IoT sensor data
        
        Returns:
            Dict with freshness score (0-100) and details
        """
        crop_type = self.get_crop_type(crop_name)
        thresholds = self.freshness_thresholds.get(crop_type, self.freshness_thresholds["tomato"])
        
        # Calculate temperature score
        temp_optimal_min, temp_optimal_max = thresholds["temp_optimal"]
        temp_score = self._calculate_environmental_score(
            temperature, 
            temp_optimal_min, 
            temp_optimal_max
        )
        
        # Calculate humidity score
        humidity_optimal_min, humidity_optimal_max = thresholds["humidity_optimal"]
        humidity_score = self._calculate_environmental_score(
            humidity,
            humidity_optimal_min,
            humidity_optimal_max
        )
        
        # Calculate age-based degradation
        age_score = 100.0
        if age_hours is not None:
            shelf_life_hours = thresholds["shelf_life"] * 24
            degradation_rate = 100.0 / shelf_life_hours
            age_score = max(0, 100 - (age_hours * degradation_rate))
        
        # Weighted freshness score
        # 40% Environment, 30% Temperature, 30% Age
        freshness_score = (
            temp_score * 0.30 +
            humidity_score * 0.40 +
            age_score * 0.30
        )
        
        # Determine freshness level
        if freshness_score >= 80:
            freshness_level = "EXCELLENT"
        elif freshness_score >= 60:
            freshness_level = "GOOD"
        elif freshness_score >= 40:
            freshness_level = "FAIR"
        elif freshness_score >= 20:
            freshness_level = "POOR"
        else:
            freshness_level = "CRITICAL"
        
        return {
            "freshness_score": round(freshness_score, 2),
            "freshness_level": freshness_level,
            "temperature": temperature,
            "humidity": humidity,
            "age_hours": age_hours,
            "temp_score": round(temp_score, 2),
            "humidity_score": round(humidity_score, 2),
            "age_score": round(age_score, 2),
            "crop_type": crop_type,
            "recommendations": self._get_recommendations(freshness_level, crop_type)
        }
    
    def _calculate_environmental_score(self, value: float, optimal_min: float, optimal_max: float) -> float:
        """Calculate a score for environmental conditions (0-100)"""
        if optimal_min <= value <= optimal_max:
            return 100.0
        
        # Calculate distance from optimal range
        if value < optimal_min:
            distance = optimal_min - value
        else:
            distance = value - optimal_max
        
        # Score decreases with distance (roughly 5% per degree or percent off)
        score = max(0, 100 - (distance * 5))
        return score
    
    def _get_recommendations(self, freshness_level: str, crop_type: str) -> list:
        """Get actionable recommendations based on freshness level"""
        recommendations = {
            "EXCELLENT": [
                "Ready for immediate market distribution",
                "Maintain current storage conditions",
                "Can withstand longer transportation"
            ],
            "GOOD": [
                "Suitable for distribution",
                "Monitor storage conditions closely",
                "Prioritize sales within 2-3 days"
            ],
            "FAIR": [
                "Use priority shipping",
                "Increase market urgency",
                "Consider discounted pricing",
                "Check for visible deterioration"
            ],
            "POOR": [
                "Immediate distribution required",
                "High discount pricing",
                "Risk of waste within 24-48 hours",
                "Local markets preferred"
            ],
            "CRITICAL": [
                "Do not distribute - risk of spoilage",
                "Consider compost/waste",
                "Investigate storage failure",
                "Prevent financial loss"
            ]
        }
        
        return recommendations.get(freshness_level, [])
