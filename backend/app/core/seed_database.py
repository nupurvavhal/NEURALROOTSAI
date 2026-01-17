# backend/app/core/seed_database.py
"""
Database Seeder - Populates MongoDB with initial data from frontend mock data
Run this once to initialize the centralized database
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# MongoDB connection from environment
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "neural_roots")

# ============================================================================
# FARMERS DATA (10 farmers)
# ============================================================================
FARMERS_DATA = [
    {
        "id": "F001",
        "name": "Ramesh Patil",
        "village": "Pune, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Ramesh",
        "rating": 4.8,
        "totalEarnings": 245000,
        "status": "Connected",
        "phone": "+91 98765 00001",
        "history": [
            {"date": "2026-01-10", "crop": "Tomatoes", "amount": "150kg", "soldTo": "Reliance Fresh", "revenue": 22500},
            {"date": "2026-01-05", "crop": "Onions", "amount": "200kg", "soldTo": "BigBasket", "revenue": 18000},
            {"date": "2025-12-28", "crop": "Potatoes", "amount": "300kg", "soldTo": "Local Mandi", "revenue": 12000},
            {"date": "2025-12-20", "crop": "Cabbage", "amount": "100kg", "soldTo": "DMart", "revenue": 8500},
        ],
    },
    {
        "id": "F002",
        "name": "Vikram Deshmukh",
        "village": "Nashik, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Vikram",
        "rating": 4.9,
        "totalEarnings": 320000,
        "status": "Connected",
        "phone": "+91 98765 00002",
        "history": [
            {"date": "2026-01-12", "crop": "Grapes", "amount": "250kg", "soldTo": "BigBasket", "revenue": 62500},
            {"date": "2026-01-08", "crop": "Onions", "amount": "400kg", "soldTo": "Reliance Fresh", "revenue": 36000},
            {"date": "2026-01-02", "crop": "Pomegranate", "amount": "180kg", "soldTo": "Export House", "revenue": 72000},
        ],
    },
    {
        "id": "F003",
        "name": "Suresh Kumar",
        "village": "Satara, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Suresh",
        "rating": 4.5,
        "totalEarnings": 180000,
        "status": "Connected",
        "phone": "+91 98765 00003",
        "history": [
            {"date": "2026-01-11", "crop": "Mangoes", "amount": "120kg", "soldTo": "BigBasket", "revenue": 24000},
            {"date": "2026-01-06", "crop": "Bananas", "amount": "250kg", "soldTo": "Local Mandi", "revenue": 15000},
        ],
    },
    {
        "id": "F004",
        "name": "Mahesh Jadhav",
        "village": "Kolhapur, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Mahesh",
        "rating": 4.7,
        "totalEarnings": 290000,
        "status": "Pending",
        "phone": "+91 98765 00004",
        "history": [
            {"date": "2026-01-09", "crop": "Sugarcane", "amount": "500kg", "soldTo": "Sugar Mill", "revenue": 15000},
            {"date": "2026-01-03", "crop": "Jaggery", "amount": "200kg", "soldTo": "Local Trader", "revenue": 40000},
        ],
    },
    {
        "id": "F005",
        "name": "Vijay Singh Thakur",
        "village": "Ahmednagar, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Vijay",
        "rating": 4.6,
        "totalEarnings": 210000,
        "status": "Connected",
        "phone": "+91 98765 00005",
        "history": [
            {"date": "2026-01-13", "crop": "Wheat", "amount": "400kg", "soldTo": "Grain Market", "revenue": 16000},
            {"date": "2026-01-07", "crop": "Chickpeas", "amount": "200kg", "soldTo": "BigBasket", "revenue": 24000},
        ],
    },
    {
        "id": "F006",
        "name": "Rajendra Shinde",
        "village": "Solapur, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Rajendra",
        "rating": 5.0,
        "totalEarnings": 385000,
        "status": "Connected",
        "phone": "+91 98765 00006",
        "history": [
            {"date": "2026-01-12", "crop": "Cotton", "amount": "300kg", "soldTo": "Textile Mill", "revenue": 90000},
            {"date": "2026-01-05", "crop": "Groundnuts", "amount": "250kg", "soldTo": "Oil Mill", "revenue": 50000},
        ],
    },
    {
        "id": "F007",
        "name": "Anil Yadav",
        "village": "Aurangabad, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Anil",
        "rating": 4.4,
        "totalEarnings": 165000,
        "status": "Connected",
        "phone": "+91 98765 00007",
        "history": [
            {"date": "2026-01-10", "crop": "Cauliflower", "amount": "150kg", "soldTo": "Reliance Fresh", "revenue": 15000},
            {"date": "2026-01-04", "crop": "Carrots", "amount": "200kg", "soldTo": "Local Mandi", "revenue": 12000},
        ],
    },
    {
        "id": "F008",
        "name": "Prakash Desai",
        "village": "Sangli, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Prakash",
        "rating": 4.8,
        "totalEarnings": 275000,
        "status": "Pending",
        "phone": "+91 98765 00008",
        "history": [
            {"date": "2026-01-11", "crop": "Turmeric", "amount": "180kg", "soldTo": "Spice Market", "revenue": 54000},
            {"date": "2026-01-06", "crop": "Chili", "amount": "120kg", "soldTo": "Export House", "revenue": 36000},
        ],
    },
    {
        "id": "F009",
        "name": "Ashok Joshi",
        "village": "Jalgaon, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Ashok",
        "rating": 4.6,
        "totalEarnings": 230000,
        "status": "Connected",
        "phone": "+91 98765 00009",
        "history": [
            {"date": "2026-01-13", "crop": "Bananas", "amount": "350kg", "soldTo": "BigBasket", "revenue": 21000},
            {"date": "2026-01-08", "crop": "Guavas", "amount": "200kg", "soldTo": "Reliance Fresh", "revenue": 16000},
        ],
    },
    {
        "id": "F010",
        "name": "Ganesh Pawar",
        "village": "Ratnagiri, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Ganesh",
        "rating": 4.9,
        "totalEarnings": 340000,
        "status": "Connected",
        "phone": "+91 98765 00010",
        "history": [
            {"date": "2026-01-12", "crop": "Alphonso Mangoes", "amount": "200kg", "soldTo": "Export House", "revenue": 80000},
            {"date": "2026-01-07", "crop": "Cashews", "amount": "100kg", "soldTo": "Processing Unit", "revenue": 50000},
        ],
    },
]

# ============================================================================
# DRIVERS DATA (8 drivers)
# ============================================================================
DRIVERS_DATA = [
    {"id": "D001", "name": "Amit Deshmukh", "vehicleType": "Tata Ace", "lat": 18.5204, "lng": 73.8567, "status": "Available", "currentLoad": "Empty", "phone": "+91 98765 43210"},
    {"id": "D002", "name": "Sunil Jadhav", "vehicleType": "Mahindra Pickup", "lat": 19.0760, "lng": 72.8777, "status": "Busy", "currentLoad": "300kg Tomatoes", "phone": "+91 98765 43211"},
    {"id": "D003", "name": "Rahul More", "vehicleType": "Tata 407", "lat": 18.5642, "lng": 73.9132, "status": "Available", "currentLoad": "Empty", "phone": "+91 98765 43212"},
    {"id": "D004", "name": "Prakash Bhosale", "vehicleType": "Ashok Leyland Dost", "lat": 19.2183, "lng": 72.9781, "status": "Busy", "currentLoad": "250kg Onions", "phone": "+91 98765 43213"},
    {"id": "D005", "name": "Santosh Kulkarni", "vehicleType": "Tata Ace", "lat": 18.4574, "lng": 73.8544, "status": "Available", "currentLoad": "Empty", "phone": "+91 98765 43214"},
    {"id": "D006", "name": "Mahesh Patil", "vehicleType": "Eicher Pro 1049", "lat": 19.1136, "lng": 72.8697, "status": "Busy", "currentLoad": "500kg Potatoes", "phone": "+91 98765 43215"},
    {"id": "D007", "name": "Ganesh Shinde", "vehicleType": "Mahindra Bolero Pickup", "lat": 18.6298, "lng": 73.7997, "status": "Available", "currentLoad": "Empty", "phone": "+91 98765 43216"},
    {"id": "D008", "name": "Ravi Kamble", "vehicleType": "Tata 709", "lat": 18.9894, "lng": 72.8358, "status": "Available", "currentLoad": "Empty", "phone": "+91 98765 43217"},
]

# ============================================================================
# MARKET ITEMS DATA (12 items)
# ============================================================================
MARKET_ITEMS_DATA = [
    {"id": "M001", "cropName": "Alphonso Mangoes", "mandiName": "Ratnagiri APMC", "price": 400, "trend": "up", "spoilageRisk": "Critical"},
    {"id": "M002", "cropName": "Onions", "mandiName": "Nashik Mandi", "price": 90, "trend": "down", "spoilageRisk": "Low"},
    {"id": "M003", "cropName": "Tomatoes", "mandiName": "Pune APMC", "price": 150, "trend": "up", "spoilageRisk": "Critical"},
    {"id": "M004", "cropName": "Potatoes", "mandiName": "Kolhapur Market", "price": 40, "trend": "down", "spoilageRisk": "Low"},
    {"id": "M005", "cropName": "Bananas", "mandiName": "Jalgaon APMC", "price": 60, "trend": "up", "spoilageRisk": "Medium"},
    {"id": "M006", "cropName": "Grapes", "mandiName": "Nashik Grape Market", "price": 250, "trend": "up", "spoilageRisk": "Critical"},
    {"id": "M007", "cropName": "Cauliflower", "mandiName": "Pune Vegetable Market", "price": 100, "trend": "down", "spoilageRisk": "Medium"},
    {"id": "M008", "cropName": "Cabbage", "mandiName": "Satara Mandi", "price": 85, "trend": "up", "spoilageRisk": "Low"},
    {"id": "M009", "cropName": "Pomegranate", "mandiName": "Solapur APMC", "price": 400, "trend": "up", "spoilageRisk": "Medium"},
    {"id": "M010", "cropName": "Green Chili", "mandiName": "Sangli Spice Market", "price": 300, "trend": "down", "spoilageRisk": "Critical"},
    {"id": "M011", "cropName": "Carrots", "mandiName": "Aurangabad Market", "price": 60, "trend": "up", "spoilageRisk": "Low"},
    {"id": "M012", "cropName": "Spinach", "mandiName": "Mumbai Wholesale", "price": 45, "trend": "down", "spoilageRisk": "Critical"},
]

# ============================================================================
# WHOLESALERS DATA (12 wholesalers)
# ============================================================================
WHOLESALERS_DATA = [
    {
        "id": "W001",
        "name": "Rajesh Mehta",
        "businessName": "Mehta Fresh Traders",
        "address": "Vashi APMC, Navi Mumbai",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=RajeshM",
        "rating": 4.8,
        "totalVolume": 850000,
        "activeOrders": 12,
        "creditLimit": 500000,
        "status": "Active",
        "specialization": ["Vegetables", "Fruits", "Exotic Produce"],
        "phone": "+91 98234 56789",
        "gstNumber": "27AABCU9603R1ZP",
        "purchases": [
            {"date": "2026-01-14", "crop": "Tomatoes", "quantity": "500kg", "boughtFrom": "Ramesh Patil", "cost": 75000, "soldTo": "Reliance Fresh", "revenue": 95000, "status": "Sold"},
            {"date": "2026-01-13", "crop": "Onions", "quantity": "800kg", "boughtFrom": "Vikram Deshmukh", "cost": 72000, "soldTo": "BigBasket", "revenue": 88000, "status": "Sold"},
        ],
    },
    {
        "id": "W002",
        "name": "Sanjay Gupta",
        "businessName": "Gupta Agro Commodities",
        "address": "Pune APMC, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=SanjayG",
        "rating": 4.9,
        "totalVolume": 1250000,
        "activeOrders": 18,
        "creditLimit": 750000,
        "status": "Active",
        "specialization": ["Grains", "Pulses", "Oilseeds"],
        "phone": "+91 98765 12345",
        "gstNumber": "27AABCU9604R1ZQ",
        "purchases": [
            {"date": "2026-01-15", "crop": "Wheat", "quantity": "2000kg", "boughtFrom": "Vijay Singh", "cost": 80000, "soldTo": "Grain Mills", "revenue": 96000, "status": "Sold"},
        ],
    },
    {
        "id": "W003",
        "name": "Dinesh Patil",
        "businessName": "Maharashtra Fruit Merchants",
        "address": "Nashik Mandi, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=DineshP",
        "rating": 4.7,
        "totalVolume": 680000,
        "activeOrders": 9,
        "creditLimit": 400000,
        "status": "Active",
        "specialization": ["Grapes", "Pomegranate", "Citrus Fruits"],
        "phone": "+91 98876 54321",
        "gstNumber": "27AABCU9605R1ZR",
        "purchases": [],
    },
    {
        "id": "W004",
        "name": "Arun Kumar",
        "businessName": "Kumar Vegetable Hub",
        "address": "Mumbai Wholesale Market",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=ArunK",
        "rating": 4.6,
        "totalVolume": 920000,
        "activeOrders": 15,
        "creditLimit": 600000,
        "status": "Active",
        "specialization": ["Leafy Vegetables", "Root Vegetables", "Exotic Veggies"],
        "phone": "+91 98234 67890",
        "gstNumber": "27AABCU9606R1ZS",
        "purchases": [],
    },
    {
        "id": "W005",
        "name": "Pradeep Shah",
        "businessName": "Shah Mango Exports",
        "address": "Ratnagiri, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=PradeepS",
        "rating": 5.0,
        "totalVolume": 1500000,
        "activeOrders": 8,
        "creditLimit": 1000000,
        "status": "Active",
        "specialization": ["Alphonso Mangoes", "Tropical Fruits", "Export Quality"],
        "phone": "+91 98765 43219",
        "gstNumber": "27AABCU9607R1ZT",
        "purchases": [],
    },
    {
        "id": "W006",
        "name": "Mohan Joshi",
        "businessName": "Joshi Spice Traders",
        "address": "Sangli Market, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=MohanJ",
        "rating": 4.8,
        "totalVolume": 720000,
        "activeOrders": 11,
        "creditLimit": 450000,
        "status": "Active",
        "specialization": ["Turmeric", "Chili", "Spices"],
        "phone": "+91 98876 12345",
        "gstNumber": "27AABCU9608R1ZU",
        "purchases": [],
    },
    {
        "id": "W007",
        "name": "Suresh Reddy",
        "businessName": "Reddy Cotton & Grains",
        "address": "Solapur APMC, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=SureshR",
        "rating": 4.5,
        "totalVolume": 980000,
        "activeOrders": 14,
        "creditLimit": 550000,
        "status": "Active",
        "specialization": ["Cotton", "Sorghum", "Millets"],
        "phone": "+91 98234 11111",
        "gstNumber": "27AABCU9609R1ZV",
        "purchases": [],
    },
    {
        "id": "W008",
        "name": "Kiran Deshmukh",
        "businessName": "Deshmukh Banana Traders",
        "address": "Jalgaon, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=KiranD",
        "rating": 4.7,
        "totalVolume": 560000,
        "activeOrders": 10,
        "creditLimit": 350000,
        "status": "Active",
        "specialization": ["Bananas", "Tropical Fruits", "Local Distribution"],
        "phone": "+91 98765 22222",
        "gstNumber": "27AABCU9610R1ZW",
        "purchases": [],
    },
    {
        "id": "W009",
        "name": "Vijay Kulkarni",
        "businessName": "Kulkarni Organic Traders",
        "address": "Satara Mandi, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=VijayK",
        "rating": 4.9,
        "totalVolume": 420000,
        "activeOrders": 7,
        "creditLimit": 300000,
        "status": "Active",
        "specialization": ["Organic Produce", "Premium Quality", "Health Foods"],
        "phone": "+91 98876 33333",
        "gstNumber": "27AABCU9611R1ZX",
        "purchases": [],
    },
    {
        "id": "W010",
        "name": "Ramesh Sawant",
        "businessName": "Sawant Sugar & Jaggery",
        "address": "Kolhapur, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=RameshS",
        "rating": 4.6,
        "totalVolume": 1100000,
        "activeOrders": 16,
        "creditLimit": 700000,
        "status": "Active",
        "specialization": ["Sugarcane", "Jaggery", "Sugar Products"],
        "phone": "+91 98234 44444",
        "gstNumber": "27AABCU9612R1ZY",
        "purchases": [],
    },
    {
        "id": "W011",
        "name": "Ashok Bhosale",
        "businessName": "Bhosale Fresh Produce",
        "address": "Aurangabad Market, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=AshokB",
        "rating": 4.4,
        "totalVolume": 380000,
        "activeOrders": 6,
        "creditLimit": 250000,
        "status": "Pending Verification",
        "specialization": ["Mixed Vegetables", "Local Market", "Bulk Supply"],
        "phone": "+91 98765 55555",
        "gstNumber": "27AABCU9613R1ZZ",
        "purchases": [],
    },
    {
        "id": "W012",
        "name": "Prakash Jadhav",
        "businessName": "Jadhav Multi-Commodity Exchange",
        "address": "Ahmednagar APMC, Maharashtra",
        "photoUrl": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=PrakashJ",
        "rating": 4.8,
        "totalVolume": 1350000,
        "activeOrders": 20,
        "creditLimit": 900000,
        "status": "Active",
        "specialization": ["All Commodities", "Bulk Trading", "B2B Supply"],
        "phone": "+91 98876 66666",
        "gstNumber": "27AABCU9614R1AA",
        "purchases": [],
    },
]


async def seed_database():
    """Seed the MongoDB database with initial data"""
    print("🌱 Neural Roots Database Seeder")
    print("=" * 50)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    try:
        # Clear existing data
        print("\n🗑️  Clearing existing collections...")
        await db.farmers.delete_many({})
        await db.drivers.delete_many({})
        await db.market_items.delete_many({})
        await db.wholesalers.delete_many({})
        print("   ✓ Collections cleared")
        
        # Insert farmers
        print("\n👨‍🌾 Seeding farmers...")
        for farmer in FARMERS_DATA:
            farmer["createdAt"] = datetime.utcnow().isoformat()
            farmer["updatedAt"] = datetime.utcnow().isoformat()
        result = await db.farmers.insert_many(FARMERS_DATA)
        print(f"   ✓ Inserted {len(result.inserted_ids)} farmers")
        
        # Insert drivers
        print("\n🚚 Seeding drivers...")
        for driver in DRIVERS_DATA:
            driver["createdAt"] = datetime.utcnow().isoformat()
            driver["updatedAt"] = datetime.utcnow().isoformat()
        result = await db.drivers.insert_many(DRIVERS_DATA)
        print(f"   ✓ Inserted {len(result.inserted_ids)} drivers")
        
        # Insert market items
        print("\n📊 Seeding market items...")
        for item in MARKET_ITEMS_DATA:
            item["createdAt"] = datetime.utcnow().isoformat()
            item["updatedAt"] = datetime.utcnow().isoformat()
        result = await db.market_items.insert_many(MARKET_ITEMS_DATA)
        print(f"   ✓ Inserted {len(result.inserted_ids)} market items")
        
        # Insert wholesalers
        print("\n🏪 Seeding wholesalers...")
        for wholesaler in WHOLESALERS_DATA:
            wholesaler["createdAt"] = datetime.utcnow().isoformat()
            wholesaler["updatedAt"] = datetime.utcnow().isoformat()
        result = await db.wholesalers.insert_many(WHOLESALERS_DATA)
        print(f"   ✓ Inserted {len(result.inserted_ids)} wholesalers")
        
        # Create indexes for faster queries
        print("\n📇 Creating indexes...")
        await db.farmers.create_index("id", unique=True)
        await db.drivers.create_index("id", unique=True)
        await db.market_items.create_index("id", unique=True)
        await db.wholesalers.create_index("id", unique=True)
        await db.iot_logs.create_index([("farmer_id", 1), ("timestamp", -1)])
        print("   ✓ Indexes created")
        
        # Print summary
        print("\n" + "=" * 50)
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
        print("=" * 50)
        print(f"\n📊 Summary:")
        print(f"   • Farmers:      {await db.farmers.count_documents({})}")
        print(f"   • Drivers:      {await db.drivers.count_documents({})}")
        print(f"   • Market Items: {await db.market_items.count_documents({})}")
        print(f"   • Wholesalers:  {await db.wholesalers.count_documents({})}")
        print(f"\n🔗 Database: {DB_NAME}")
        print(f"🔗 MongoDB URL: {MONGODB_URL}")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        raise e
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
