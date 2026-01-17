# backend/app/core/setup_database.py
"""
Database Setup Script for Neural Roots AI
Creates 5 collections with sample data and geospatial indexes:
1. farmers - Farmer profiles with location
2. sensor_data - Time series IoT data
3. batches - Crop batches with AI analysis
4. wholesalers - Mandi/wholesaler data with prices
5. drivers - Driver profiles with live location
"""

import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import GEOSPHERE
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.core.config import settings


async def setup_database():
    """Main setup function to create collections and insert sample data."""
    
    print("🚀 Starting Neural Roots AI Database Setup...")
    print(f"📡 Connecting to MongoDB...")
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DB_NAME]
    
    # Drop existing collections for fresh start (remove this in production!)
    existing_collections = await db.list_collection_names()
    for coll in ['farmers', 'sensor_data', 'batches', 'wholesalers', 'drivers']:
        if coll in existing_collections:
            await db.drop_collection(coll)
            print(f"🗑️  Dropped existing collection: {coll}")
    
    # =========================================================================
    # 1. FARMERS COLLECTION
    # =========================================================================
    print("\n📋 Creating 'farmers' collection...")
    
    farmers_data = [
        {
            "_id": "farmer_001",
            "name": "Ramesh Kumar",
            "phone": "+919876543210",
            "location": {
                "type": "Point",
                "coordinates": [72.8777, 19.0760]  # Mumbai area [Longitude, Latitude]
            },
            "current_device_id": "ESP32_A1",
            "crops": ["Tomato", "Onion"],
            "created_at": datetime.utcnow()
        },
        {
            "_id": "farmer_002",
            "name": "Sunil Patil",
            "phone": "+919988776655",
            "location": {
                "type": "Point",
                "coordinates": [73.8567, 18.5204]  # Pune area
            },
            "current_device_id": "ESP32_B2",
            "crops": ["Potato", "Cauliflower"],
            "created_at": datetime.utcnow()
        },
        {
            "_id": "farmer_003",
            "name": "Lakshmi Devi",
            "phone": "+919123456789",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]  # Bangalore area
            },
            "current_device_id": "ESP32_C3",
            "crops": ["Mango", "Banana"],
            "created_at": datetime.utcnow()
        },
        {
            "_id": "farmer_004",
            "name": "Arjun Singh",
            "phone": "+919999999999",
            "location": {
                "type": "Point",
                "coordinates": [75.7873, 26.9124]  # Jaipur area
            },
            "current_device_id": "ESP32_D4",
            "crops": ["Tomato", "Chili"],
            "created_at": datetime.utcnow()
        },
        {
            "_id": "farmer_005",
            "name": "Priya Sharma",
            "phone": "+918877665544",
            "location": {
                "type": "Point",
                "coordinates": [80.9462, 26.8467]  # Lucknow area
            },
            "current_device_id": "ESP32_E5",
            "crops": ["Wheat", "Rice"],
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.farmers.insert_many(farmers_data)
    await db.farmers.create_index([("location", GEOSPHERE)])
    print(f"   ✅ Inserted {len(farmers_data)} farmers")
    print("   ✅ Created 2dsphere index on 'location'")
    
    # =========================================================================
    # 2. SENSOR_DATA COLLECTION (Time Series)
    # =========================================================================
    print("\n📋 Creating 'sensor_data' collection...")
    
    # Create time series collection
    try:
        await db.create_collection(
            "sensor_data",
            timeseries={
                "timeField": "timestamp",
                "metaField": "metadata",
                "granularity": "minutes"
            }
        )
        print("   ✅ Created as Time Series collection")
    except Exception as e:
        print(f"   ⚠️  Time series creation note: {e}")
    
    # Generate sample sensor readings for the past 24 hours
    sensor_data = []
    base_time = datetime.utcnow() - timedelta(hours=24)
    
    devices = [
        ("ESP32_A1", "farmer_001"),
        ("ESP32_B2", "farmer_002"),
        ("ESP32_C3", "farmer_003"),
        ("ESP32_D4", "farmer_004"),
        ("ESP32_E5", "farmer_005")
    ]
    
    for device_id, farmer_id in devices:
        for hour in range(24):
            sensor_data.append({
                "timestamp": base_time + timedelta(hours=hour),
                "metadata": {
                    "device_id": device_id,
                    "farmer_id": farmer_id
                },
                "temperature": round(25 + (hour % 12) * 0.5 + (hash(device_id) % 5), 1),
                "humidity": round(60 + (hour % 8) * 2 - (hash(device_id) % 10), 1),
                "camera_image_url": f"https://storage.googleapis.com/neural-roots/{farmer_id}/img_{hour}.jpg"
            })
    
    await db.sensor_data.insert_many(sensor_data)
    print(f"   ✅ Inserted {len(sensor_data)} sensor readings (24 hrs × 5 devices)")
    
    # =========================================================================
    # 3. BATCHES COLLECTION (Crop Batches with AI Analysis)
    # =========================================================================
    print("\n📋 Creating 'batches' collection...")
    
    batches_data = [
        {
            "_id": "batch_101",
            "farmer_id": "farmer_001",
            "crop_type": "Tomato",
            "quantity_kg": 500,
            "status": "MONITORING",
            "harvest_date": datetime.utcnow() - timedelta(days=2),
            "ai_analysis": {
                "freshness_score": 85,
                "predicted_spoilage_date": datetime.utcnow() + timedelta(days=3),
                "confidence": 0.92,
                "recommendations": ["Sell within 3 days", "Store at 10-15°C"],
                "last_updated": datetime.utcnow()
            },
            "created_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "_id": "batch_102",
            "farmer_id": "farmer_001",
            "crop_type": "Onion",
            "quantity_kg": 300,
            "status": "READY_TO_SELL",
            "harvest_date": datetime.utcnow() - timedelta(days=5),
            "ai_analysis": {
                "freshness_score": 72,
                "predicted_spoilage_date": datetime.utcnow() + timedelta(days=1),
                "confidence": 0.88,
                "recommendations": ["Sell immediately", "City mandi recommended"],
                "last_updated": datetime.utcnow()
            },
            "created_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "_id": "batch_103",
            "farmer_id": "farmer_002",
            "crop_type": "Potato",
            "quantity_kg": 1000,
            "status": "MONITORING",
            "harvest_date": datetime.utcnow() - timedelta(days=1),
            "ai_analysis": {
                "freshness_score": 95,
                "predicted_spoilage_date": datetime.utcnow() + timedelta(days=14),
                "confidence": 0.95,
                "recommendations": ["Can store for 2 weeks", "Monitor humidity"],
                "last_updated": datetime.utcnow()
            },
            "created_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "_id": "batch_104",
            "farmer_id": "farmer_003",
            "crop_type": "Mango",
            "quantity_kg": 200,
            "status": "SOLD",
            "harvest_date": datetime.utcnow() - timedelta(days=7),
            "ai_analysis": {
                "freshness_score": 60,
                "predicted_spoilage_date": datetime.utcnow() - timedelta(days=1),
                "confidence": 0.85,
                "recommendations": ["Sold successfully"],
                "last_updated": datetime.utcnow() - timedelta(days=2)
            },
            "sale_info": {
                "sold_to": "mandi_bangalore_01",
                "price_per_kg": 55,
                "total_amount": 11000,
                "sold_at": datetime.utcnow() - timedelta(days=2)
            },
            "created_at": datetime.utcnow() - timedelta(days=7)
        },
        {
            "_id": "batch_105",
            "farmer_id": "farmer_004",
            "crop_type": "Tomato",
            "quantity_kg": 750,
            "status": "MONITORING",
            "harvest_date": datetime.utcnow(),
            "ai_analysis": {
                "freshness_score": 98,
                "predicted_spoilage_date": datetime.utcnow() + timedelta(days=5),
                "confidence": 0.97,
                "recommendations": ["Excellent condition", "Can wait for better prices"],
                "last_updated": datetime.utcnow()
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.batches.insert_many(batches_data)
    await db.batches.create_index("farmer_id")
    await db.batches.create_index("status")
    print(f"   ✅ Inserted {len(batches_data)} crop batches")
    print("   ✅ Created indexes on 'farmer_id' and 'status'")
    
    # =========================================================================
    # 4. WHOLESALERS COLLECTION
    # =========================================================================
    print("\n📋 Creating 'wholesalers' collection...")
    
    wholesalers_data = [
        {
            "_id": "mandi_mumbai_01",
            "name": "APMC Vashi",
            "type": "City Mandi",
            "city": "Mumbai",
            "location": {
                "type": "Point",
                "coordinates": [72.99, 19.05]
            },
            "contact_phone": "+912227654321",
            "operating_hours": "4:00 AM - 2:00 PM",
            "live_rates": [
                {"fruit": "Tomato", "price_per_kg": 45, "updated_at": datetime.utcnow()},
                {"fruit": "Onion", "price_per_kg": 30, "updated_at": datetime.utcnow()},
                {"fruit": "Potato", "price_per_kg": 25, "updated_at": datetime.utcnow()},
                {"fruit": "Mango", "price_per_kg": 60, "updated_at": datetime.utcnow()}
            ],
            "rating": 4.5,
            "total_transactions": 1250
        },
        {
            "_id": "mandi_mumbai_02",
            "name": "Crawford Market",
            "type": "City Mandi",
            "city": "Mumbai",
            "location": {
                "type": "Point",
                "coordinates": [72.8347, 18.9477]
            },
            "contact_phone": "+912223456789",
            "operating_hours": "5:00 AM - 3:00 PM",
            "live_rates": [
                {"fruit": "Tomato", "price_per_kg": 50, "updated_at": datetime.utcnow()},
                {"fruit": "Onion", "price_per_kg": 32, "updated_at": datetime.utcnow()},
                {"fruit": "Potato", "price_per_kg": 28, "updated_at": datetime.utcnow()},
                {"fruit": "Mango", "price_per_kg": 65, "updated_at": datetime.utcnow()}
            ],
            "rating": 4.2,
            "total_transactions": 980
        },
        {
            "_id": "mandi_village_01",
            "name": "Nashik Village Mandi",
            "type": "Village Mandi",
            "city": "Nashik",
            "location": {
                "type": "Point",
                "coordinates": [73.7898, 19.9975]
            },
            "contact_phone": "+912532567890",
            "operating_hours": "6:00 AM - 12:00 PM",
            "live_rates": [
                {"fruit": "Tomato", "price_per_kg": 35, "updated_at": datetime.utcnow()},
                {"fruit": "Onion", "price_per_kg": 22, "updated_at": datetime.utcnow()},
                {"fruit": "Potato", "price_per_kg": 18, "updated_at": datetime.utcnow()},
                {"fruit": "Mango", "price_per_kg": 45, "updated_at": datetime.utcnow()}
            ],
            "rating": 4.0,
            "total_transactions": 450
        },
        {
            "_id": "mandi_pune_01",
            "name": "Market Yard Pune",
            "type": "City Mandi",
            "city": "Pune",
            "location": {
                "type": "Point",
                "coordinates": [73.8478, 18.4973]
            },
            "contact_phone": "+912025678901",
            "operating_hours": "4:30 AM - 1:00 PM",
            "live_rates": [
                {"fruit": "Tomato", "price_per_kg": 42, "updated_at": datetime.utcnow()},
                {"fruit": "Onion", "price_per_kg": 28, "updated_at": datetime.utcnow()},
                {"fruit": "Potato", "price_per_kg": 22, "updated_at": datetime.utcnow()},
                {"fruit": "Cauliflower", "price_per_kg": 35, "updated_at": datetime.utcnow()}
            ],
            "rating": 4.3,
            "total_transactions": 870
        },
        {
            "_id": "mandi_bangalore_01",
            "name": "Yeshwanthpur APMC",
            "type": "City Mandi",
            "city": "Bangalore",
            "location": {
                "type": "Point",
                "coordinates": [77.5440, 13.0206]
            },
            "contact_phone": "+918023456789",
            "operating_hours": "3:00 AM - 12:00 PM",
            "live_rates": [
                {"fruit": "Tomato", "price_per_kg": 48, "updated_at": datetime.utcnow()},
                {"fruit": "Onion", "price_per_kg": 35, "updated_at": datetime.utcnow()},
                {"fruit": "Mango", "price_per_kg": 70, "updated_at": datetime.utcnow()},
                {"fruit": "Banana", "price_per_kg": 40, "updated_at": datetime.utcnow()}
            ],
            "rating": 4.6,
            "total_transactions": 1520
        }
    ]
    
    await db.wholesalers.insert_many(wholesalers_data)
    await db.wholesalers.create_index([("location", GEOSPHERE)])
    await db.wholesalers.create_index("type")
    print(f"   ✅ Inserted {len(wholesalers_data)} wholesalers/mandis")
    print("   ✅ Created 2dsphere index on 'location'")
    
    # =========================================================================
    # 5. DRIVERS COLLECTION
    # =========================================================================
    print("\n📋 Creating 'drivers' collection...")
    
    drivers_data = [
        {
            "_id": "driver_001",
            "name": "Suresh Yadav",
            "phone": "+919876501234",
            "vehicle": "Mini Truck",
            "vehicle_number": "MH12AB1234",
            "capacity_kg": 1000,
            "status": "AVAILABLE",
            "current_location": {
                "type": "Point",
                "coordinates": [72.90, 19.10]  # Near Mumbai
            },
            "rating": 4.7,
            "total_trips": 156,
            "price_per_km": 15,
            "last_active": datetime.utcnow()
        },
        {
            "_id": "driver_002",
            "name": "Rajesh Patil",
            "phone": "+919876502345",
            "vehicle": "Tata Ace",
            "vehicle_number": "MH14CD5678",
            "capacity_kg": 750,
            "status": "AVAILABLE",
            "current_location": {
                "type": "Point",
                "coordinates": [72.85, 19.02]  # Mumbai suburbs
            },
            "rating": 4.5,
            "total_trips": 89,
            "price_per_km": 12,
            "last_active": datetime.utcnow()
        },
        {
            "_id": "driver_003",
            "name": "Mohan Singh",
            "phone": "+919876503456",
            "vehicle": "Mahindra Bolero Pickup",
            "vehicle_number": "MH20EF9012",
            "capacity_kg": 1500,
            "status": "BUSY",
            "current_location": {
                "type": "Point",
                "coordinates": [73.80, 18.55]  # Near Pune
            },
            "rating": 4.8,
            "total_trips": 234,
            "price_per_km": 18,
            "current_trip": {
                "from_farmer": "farmer_002",
                "to_mandi": "mandi_pune_01",
                "started_at": datetime.utcnow() - timedelta(hours=1)
            },
            "last_active": datetime.utcnow()
        },
        {
            "_id": "driver_004",
            "name": "Vikram Reddy",
            "phone": "+919876504567",
            "vehicle": "Tata 407",
            "vehicle_number": "KA01GH3456",
            "capacity_kg": 2500,
            "status": "AVAILABLE",
            "current_location": {
                "type": "Point",
                "coordinates": [77.55, 12.95]  # Near Bangalore
            },
            "rating": 4.6,
            "total_trips": 312,
            "price_per_km": 20,
            "last_active": datetime.utcnow()
        },
        {
            "_id": "driver_005",
            "name": "Anil Kumar",
            "phone": "+919876505678",
            "vehicle": "Ashok Leyland Dost",
            "vehicle_number": "MH12IJ7890",
            "capacity_kg": 1250,
            "status": "AVAILABLE",
            "current_location": {
                "type": "Point",
                "coordinates": [73.75, 19.95]  # Near Nashik
            },
            "rating": 4.4,
            "total_trips": 67,
            "price_per_km": 14,
            "last_active": datetime.utcnow()
        },
        {
            "_id": "driver_006",
            "name": "Deepak Sharma",
            "phone": "+919876506789",
            "vehicle": "Eicher Pro",
            "vehicle_number": "RJ14KL2345",
            "capacity_kg": 3000,
            "status": "OFFLINE",
            "current_location": {
                "type": "Point",
                "coordinates": [75.80, 26.90]  # Near Jaipur
            },
            "rating": 4.3,
            "total_trips": 198,
            "price_per_km": 22,
            "last_active": datetime.utcnow() - timedelta(hours=5)
        }
    ]
    
    await db.drivers.insert_many(drivers_data)
    await db.drivers.create_index([("current_location", GEOSPHERE)])
    await db.drivers.create_index("status")
    await db.drivers.create_index("capacity_kg")
    print(f"   ✅ Inserted {len(drivers_data)} drivers")
    print("   ✅ Created 2dsphere index on 'current_location'")
    print("   ✅ Created indexes on 'status' and 'capacity_kg'")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*60)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"\n📦 Database: {settings.DB_NAME}")
    print("\n📋 Collections Created:")
    print("   1. farmers       - 5 farmers with geospatial locations")
    print("   2. sensor_data   - 120 sensor readings (Time Series)")
    print("   3. batches       - 5 crop batches with AI analysis")
    print("   4. wholesalers   - 5 mandis with live prices")
    print("   5. drivers       - 6 drivers with live locations")
    print("\n🗺️  Geospatial Indexes (2dsphere):")
    print("   - farmers.location")
    print("   - wholesalers.location")
    print("   - drivers.current_location")
    print("\n✅ Ready for Neural Roots AI operations!")
    print("="*60)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(setup_database())
