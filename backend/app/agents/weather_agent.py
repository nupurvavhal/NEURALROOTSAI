# backend/app/agents/weather_agent.py
"""
Weather Agent - Fetches weather data and determines impact on freshness
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

class WeatherAgent:
    """
    Analyzes weather conditions and their impact on crop freshness during storage/transport.
    Can integrate with external weather APIs or use MongoDB stored weather data.
    """
    
    def __init__(self):
        self.weather_impact_factors = {
            "temperature": {"weight": 0.4, "critical_range": (5, 35)},  # Celsius
            "humidity": {"weight": 0.3, "optimal_range": (60, 95)},  # Percentage
            "precipitation": {"weight": 0.2, "impact": "increases_spoilage"},
            "wind_speed": {"weight": 0.1, "critical": 40}  # km/h
        }
    
    async def fetch_weather_forecast(
        self,
        db,
        location: str,
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """
        Fetch weather forecast from MongoDB or external API
        
        Args:
            db: MongoDB database instance
            location: Location for weather forecast
            hours_ahead: Number of hours to forecast
        
        Returns:
            Dict with weather forecast data
        """
        try:
            # Try to fetch from weather collection
            query = {
                "location": {"$regex": location, "$options": "i"},
                "timestamp": {"$gte": datetime.now()}
            }
            
            weather_data = await db.weather.find(query).sort("timestamp", 1).to_list(168)
            
            if not weather_data:
                return {
                    "status": "no_data",
                    "message": f"No weather data available for {location}",
                    "forecast": []
                }
            
            return {
                "status": "success",
                "location": location,
                "forecast_hours": hours_ahead,
                "data_points": len(weather_data),
                "forecast": [self._format_weather_entry(w) for w in weather_data[:hours_ahead]]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "forecast": []
            }
    
    async def assess_weather_impact(
        self,
        location: str,
        crop_type: str,
        transportation_duration_hours: float,
        db = None
    ) -> Dict[str, Any]:
        """
        Assess weather impact on crop freshness during transportation
        
        Args:
            location: Current location/region
            crop_type: Type of crop
            transportation_duration_hours: Expected transport time
            db: Optional MongoDB instance for weather data
        
        Returns:
            Dict with weather impact assessment
        """
        
        # Get weather forecast
        forecast = None
        if db:
            weather_response = await self.fetch_weather_forecast(
                db, location, int(transportation_duration_hours)
            )
            if weather_response.get("status") == "success":
                forecast = weather_response.get("forecast", [])
        
        if not forecast:
            # Use simulated weather data if no database available
            forecast = self._generate_simulated_forecast(transportation_duration_hours)
        
        # Analyze forecast impact
        impact_analysis = self._analyze_weather_impact(forecast, crop_type)
        
        # Get freshness degradation estimate
        degradation_rate = self._calculate_degradation_rate(impact_analysis, crop_type)
        
        return {
            "status": "success",
            "location": location,
            "crop_type": crop_type,
            "transportation_duration_hours": transportation_duration_hours,
            "weather_forecast": forecast[:6],  # Show next 6 data points
            "impact_analysis": impact_analysis,
            "freshness_degradation_rate": round(degradation_rate, 2),
            "recommendations": self._get_weather_recommendations(impact_analysis, crop_type)
        }
    
    def _format_weather_entry(self, entry: Dict) -> Dict:
        """Format weather database entry for API response"""
        return {
            "timestamp": entry.get("timestamp", "").isoformat() if hasattr(entry.get("timestamp"), "isoformat") else str(entry.get("timestamp")),
            "temperature": entry.get("temperature", 0),
            "humidity": entry.get("humidity", 0),
            "precipitation": entry.get("precipitation", 0),
            "wind_speed": entry.get("wind_speed", 0),
            "condition": entry.get("condition", "unknown")
        }
    
    def _generate_simulated_forecast(self, hours: int) -> list:
        """Generate simulated weather forecast (for demo purposes)"""
        forecast = []
        now = datetime.now()
        
        # Simulate realistic weather variations
        base_temp = 25
        base_humidity = 70
        
        for i in range(min(int(hours), 24)):
            temp_variation = -5 if i < 6 else (3 if i < 12 else (-2 if i < 18 else 1))
            humidity_variation = 5 if i % 4 == 0 else -3
            
            forecast.append({
                "timestamp": (now + timedelta(hours=i)).isoformat(),
                "temperature": base_temp + temp_variation + (i % 3) - 1,
                "humidity": max(40, min(95, base_humidity + humidity_variation)),
                "precipitation": 0 if i % 6 != 3 else 5,
                "wind_speed": 5 + (i % 4),
                "condition": "partly_cloudy" if i % 3 != 0 else "clear"
            })
        
        return forecast
    
    def _analyze_weather_impact(self, forecast: list, crop_type: str) -> Dict[str, Any]:
        """Analyze weather forecast impact"""
        if not forecast:
            return {
                "avg_temperature": 0,
                "avg_humidity": 0,
                "max_precipitation": 0,
                "risk_level": "UNKNOWN"
            }
        
        temperatures = [f.get("temperature", 0) for f in forecast]
        humidities = [f.get("humidity", 0) for f in forecast]
        precipitations = [f.get("precipitation", 0) for f in forecast]
        wind_speeds = [f.get("wind_speed", 0) for f in forecast]
        
        avg_temp = sum(temperatures) / len(temperatures) if temperatures else 0
        avg_humidity = sum(humidities) / len(humidities) if humidities else 0
        max_precipitation = max(precipitations) if precipitations else 0
        max_wind = max(wind_speeds) if wind_speeds else 0
        
        # Determine risk level
        risk_score = 0
        
        # Temperature risk
        if avg_temp < 5 or avg_temp > 35:
            risk_score += 40
        elif avg_temp < 10 or avg_temp > 30:
            risk_score += 20
        
        # Humidity risk
        if avg_humidity < 60 or avg_humidity > 95:
            risk_score += 25
        
        # Precipitation risk
        if max_precipitation > 0:
            risk_score += 20
        
        # Wind risk
        if max_wind > 40:
            risk_score += 15
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "avg_temperature": round(avg_temp, 1),
            "avg_humidity": round(avg_humidity, 1),
            "max_precipitation": round(max_precipitation, 1),
            "max_wind_speed": round(max_wind, 1),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "optimal_conditions": risk_level == "LOW"
        }
    
    def _calculate_degradation_rate(self, impact_analysis: Dict, crop_type: str) -> float:
        """Calculate freshness degradation rate based on weather"""
        risk_level = impact_analysis.get("risk_level", "MEDIUM")
        
        base_degradation = {
            "LOW": 0.5,      # 0.5% per hour
            "MEDIUM": 1.0,   # 1% per hour
            "HIGH": 2.0,     # 2% per hour
            "CRITICAL": 4.0  # 4% per hour
        }.get(risk_level, 1.0)
        
        # Adjust based on crop sensitivity
        crop_sensitivity = {
            "tomato": 1.2,          # Very sensitive
            "leafy_greens": 1.5,    # Most sensitive
            "mango": 0.8,           # Less sensitive
            "potato": 0.5,          # Very resistant
            "onion": 0.4             # Very resistant
        }.get(crop_type.lower(), 1.0)
        
        return base_degradation * crop_sensitivity
    
    def _get_weather_recommendations(self, impact_analysis: Dict, crop_type: str) -> list:
        """Get weather-based recommendations"""
        risk_level = impact_analysis.get("risk_level", "MEDIUM")
        avg_temp = impact_analysis.get("avg_temperature", 25)
        
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.append("URGENT: Use insulated/refrigerated transport")
            recommendations.append("Consider delaying shipment")
            recommendations.append("Monitor temperature closely")
        elif risk_level == "HIGH":
            recommendations.append("Use refrigerated transport recommended")
            recommendations.append("Increase monitoring frequency")
            recommendations.append("Plan for possible delays")
        
        if avg_temp > 30:
            recommendations.append("Temperature high - keep in shade/cool environment")
        elif avg_temp < 10:
            recommendations.append("Temperature low - consider insulation")
        
        if impact_analysis.get("max_precipitation", 0) > 0:
            recommendations.append("Waterproof packaging required")
        
        if not recommendations:
            recommendations.append("Weather conditions favorable for transport")
        
        return recommendations
