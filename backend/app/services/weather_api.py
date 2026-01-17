# backend/app/services/weather_api.py
"""
Weather API Service
Fetches weather data from OpenWeatherMap API
"""

import os
import httpx
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# OpenWeatherMap API (Free tier: 1000 calls/day)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"


# ============================================================================
# DATA MODELS
# ============================================================================

class WeatherCondition(BaseModel):
    """Current weather condition"""
    temperature: float          # Celsius
    feels_like: float
    humidity: int               # Percentage
    pressure: int               # hPa
    wind_speed: float           # m/s
    wind_direction: int         # degrees
    clouds: int                 # Percentage
    visibility: int             # meters
    weather_main: str           # "Rain", "Clear", "Clouds", etc.
    weather_description: str    # "light rain", "scattered clouds"
    weather_icon: str           # Icon code
    rain_1h: Optional[float] = None     # Rain volume last 1h (mm)
    rain_3h: Optional[float] = None     # Rain volume last 3h (mm)
    timestamp: str


class ForecastItem(BaseModel):
    """Single forecast period"""
    datetime: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    weather_main: str
    weather_description: str
    rain_probability: float     # 0-1
    rain_volume: Optional[float] = None  # mm


class WeatherForecast(BaseModel):
    """5-day weather forecast"""
    location: str
    country: str
    lat: float
    lon: float
    forecasts: List[ForecastItem]
    fetched_at: str


# ============================================================================
# INDIAN CITIES/VILLAGES COORDINATES
# ============================================================================

MAHARASHTRA_LOCATIONS = {
    "pune": {"lat": 18.5204, "lon": 73.8567},
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "nashik": {"lat": 19.9975, "lon": 73.7898},
    "kolhapur": {"lat": 16.7050, "lon": 74.2433},
    "satara": {"lat": 17.6805, "lon": 74.0183},
    "solapur": {"lat": 17.6599, "lon": 75.9064},
    "ahmednagar": {"lat": 19.0948, "lon": 74.7480},
    "aurangabad": {"lat": 19.8762, "lon": 75.3433},
    "jalgaon": {"lat": 21.0077, "lon": 75.5626},
    "sangli": {"lat": 16.8524, "lon": 74.5815},
    "ratnagiri": {"lat": 16.9902, "lon": 73.3120},
    "nagpur": {"lat": 21.1458, "lon": 79.0882},
}


# ============================================================================
# API FUNCTIONS
# ============================================================================

async def get_current_weather(lat: float, lon: float) -> Optional[WeatherCondition]:
    """
    Fetch current weather for coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        WeatherCondition or None if API fails
    """
    if not OPENWEATHER_API_KEY:
        print("⚠️ OPENWEATHER_API_KEY not set, using mock data")
        return get_mock_current_weather(lat, lon)
    
    url = f"{BASE_URL}/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            rain_1h = data.get("rain", {}).get("1h")
            rain_3h = data.get("rain", {}).get("3h")
            
            return WeatherCondition(
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                wind_speed=data["wind"]["speed"],
                wind_direction=data["wind"].get("deg", 0),
                clouds=data["clouds"]["all"],
                visibility=data.get("visibility", 10000),
                weather_main=data["weather"][0]["main"],
                weather_description=data["weather"][0]["description"],
                weather_icon=data["weather"][0]["icon"],
                rain_1h=rain_1h,
                rain_3h=rain_3h,
                timestamp=datetime.utcnow().isoformat()
            )
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return get_mock_current_weather(lat, lon)


async def get_weather_forecast(lat: float, lon: float) -> Optional[WeatherForecast]:
    """
    Fetch 5-day/3-hour weather forecast
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        WeatherForecast or None
    """
    if not OPENWEATHER_API_KEY:
        print("⚠️ OPENWEATHER_API_KEY not set, using mock data")
        return get_mock_forecast(lat, lon)
    
    url = f"{BASE_URL}/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data["list"]:
                forecasts.append(ForecastItem(
                    datetime=item["dt_txt"],
                    temperature=item["main"]["temp"],
                    feels_like=item["main"]["feels_like"],
                    humidity=item["main"]["humidity"],
                    wind_speed=item["wind"]["speed"],
                    weather_main=item["weather"][0]["main"],
                    weather_description=item["weather"][0]["description"],
                    rain_probability=item.get("pop", 0),
                    rain_volume=item.get("rain", {}).get("3h")
                ))
            
            return WeatherForecast(
                location=data["city"]["name"],
                country=data["city"]["country"],
                lat=data["city"]["coord"]["lat"],
                lon=data["city"]["coord"]["lon"],
                forecasts=forecasts,
                fetched_at=datetime.utcnow().isoformat()
            )
    except Exception as e:
        print(f"❌ Weather Forecast API error: {e}")
        return get_mock_forecast(lat, lon)


async def get_weather_by_city(city: str) -> Optional[WeatherCondition]:
    """Get weather by city name (for Maharashtra locations)"""
    city_lower = city.lower().replace(" ", "").replace(",", "")
    
    # Check if it's a known location
    for loc_name, coords in MAHARASHTRA_LOCATIONS.items():
        if loc_name in city_lower or city_lower in loc_name:
            return await get_current_weather(coords["lat"], coords["lon"])
    
    # Default to Pune if city not found
    print(f"⚠️ City '{city}' not found, defaulting to Pune")
    return await get_current_weather(18.5204, 73.8567)


async def get_forecast_by_city(city: str) -> Optional[WeatherForecast]:
    """Get forecast by city name"""
    city_lower = city.lower().replace(" ", "").replace(",", "")
    
    for loc_name, coords in MAHARASHTRA_LOCATIONS.items():
        if loc_name in city_lower or city_lower in loc_name:
            return await get_weather_forecast(coords["lat"], coords["lon"])
    
    return await get_weather_forecast(18.5204, 73.8567)


# ============================================================================
# MOCK DATA (When API key not available)
# ============================================================================

def get_mock_current_weather(lat: float, lon: float) -> WeatherCondition:
    """Return mock weather data for testing"""
    import random
    
    conditions = [
        ("Clear", "clear sky"),
        ("Clouds", "scattered clouds"),
        ("Rain", "light rain"),
        ("Thunderstorm", "thunderstorm with rain"),
    ]
    
    weather = random.choice(conditions)
    
    return WeatherCondition(
        temperature=round(random.uniform(22, 35), 1),
        feels_like=round(random.uniform(24, 38), 1),
        humidity=random.randint(45, 85),
        pressure=random.randint(1008, 1020),
        wind_speed=round(random.uniform(2, 15), 1),
        wind_direction=random.randint(0, 360),
        clouds=random.randint(10, 90),
        visibility=random.randint(5000, 10000),
        weather_main=weather[0],
        weather_description=weather[1],
        weather_icon="01d",
        rain_1h=round(random.uniform(0, 5), 1) if weather[0] in ["Rain", "Thunderstorm"] else None,
        timestamp=datetime.utcnow().isoformat()
    )


def get_mock_forecast(lat: float, lon: float) -> WeatherForecast:
    """Return mock forecast data for testing"""
    import random
    from datetime import timedelta
    
    forecasts = []
    base_time = datetime.utcnow()
    
    for i in range(40):  # 5 days * 8 periods per day
        period_time = base_time + timedelta(hours=i * 3)
        
        # Simulate weather patterns
        is_rainy = random.random() < 0.3
        
        forecasts.append(ForecastItem(
            datetime=period_time.strftime("%Y-%m-%d %H:%M:%S"),
            temperature=round(random.uniform(22, 35), 1),
            feels_like=round(random.uniform(24, 38), 1),
            humidity=random.randint(50, 90) if is_rainy else random.randint(40, 70),
            wind_speed=round(random.uniform(2, 12), 1),
            weather_main="Rain" if is_rainy else random.choice(["Clear", "Clouds"]),
            weather_description="light rain" if is_rainy else "partly cloudy",
            rain_probability=round(random.uniform(0.5, 0.9), 2) if is_rainy else round(random.uniform(0, 0.3), 2),
            rain_volume=round(random.uniform(1, 10), 1) if is_rainy else None
        ))
    
    return WeatherForecast(
        location="Pune",
        country="IN",
        lat=lat,
        lon=lon,
        forecasts=forecasts,
        fetched_at=datetime.utcnow().isoformat()
    )


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "WeatherCondition",
    "ForecastItem", 
    "WeatherForecast",
    "get_current_weather",
    "get_weather_forecast",
    "get_weather_by_city",
    "get_forecast_by_city",
    "MAHARASHTRA_LOCATIONS"
]
