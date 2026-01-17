"""
Test script for Freshness Agent
Tests the Gemini AI integration with sample sensor data
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.agents.freshness_agent import analyze_freshness, SensorInput
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_freshness_agent():
    print("🧪 Testing Freshness Agent with Gemini AI")
    print("=" * 60)
    
    # Test Case 1: Fresh tomatoes with good conditions
    print("\n📊 Test 1: Fresh Tomatoes (Good Conditions)")
    print("-" * 60)
    sensor_data_1 = SensorInput(
        farmer_id="F001",
        device_id="ESP32-001",
        crop_type="Tomatoes",
        temperature=18.0,
        humidity=90.0,
        crop_classification="fresh"
    )
    
    result_1 = await analyze_freshness(sensor_data_1)
    print(f"   Freshness Score: {result_1.freshness_score}/100")
    print(f"   Health Status: {result_1.health_status}")
    print(f"   Shelf Life: {result_1.shelf_life_hours} hours")
    print(f"   Alert: {result_1.alert_generated}")
    if result_1.alert_generated:
        print(f"   Alert Message: {result_1.alert_message}")
    print(f"   Recommendations:")
    for rec in result_1.recommendations:
        print(f"      - {rec}")
    print(f"   Confidence: {result_1.confidence:.2f}")
    
    # Test Case 2: Rotten onions
    print("\n📊 Test 2: Rotten Onions")
    print("-" * 60)
    sensor_data_2 = SensorInput(
        farmer_id="F006",
        device_id="ESP32-006",
        crop_type="Onions",
        temperature=31.0,
        humidity=85.0,
        crop_classification="rotten"
    )
    
    result_2 = await analyze_freshness(sensor_data_2)
    print(f"   Freshness Score: {result_2.freshness_score}/100")
    print(f"   Health Status: {result_2.health_status}")
    print(f"   Shelf Life: {result_2.shelf_life_hours} hours")
    print(f"   Alert: {result_2.alert_generated}")
    if result_2.alert_generated:
        print(f"   Alert Type: {result_2.alert_type}")
        print(f"   Alert Message: {result_2.alert_message}")
    print(f"   Recommendations:")
    for rec in result_2.recommendations:
        print(f"      - {rec}")
    
    # Test Case 3: Fresh grapes with high temperature
    print("\n📊 Test 3: Fresh Grapes (High Temperature)")
    print("-" * 60)
    sensor_data_3 = SensorInput(
        farmer_id="F002",
        device_id="ESP32-002",
        crop_type="Grapes",
        temperature=38.0,
        humidity=55.0,
        crop_classification="fresh"
    )
    
    result_3 = await analyze_freshness(sensor_data_3)
    print(f"   Freshness Score: {result_3.freshness_score}/100")
    print(f"   Health Status: {result_3.health_status}")
    print(f"   Shelf Life: {result_3.shelf_life_hours} hours")
    print(f"   Alert: {result_3.alert_generated}")
    if result_3.alert_generated:
        print(f"   Alert Type: {result_3.alert_type}")
        print(f"   Alert Message: {result_3.alert_message}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_freshness_agent())
