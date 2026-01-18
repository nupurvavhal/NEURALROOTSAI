# WORKFLOW QUICK START GUIDE

## 🚀 Getting Started

### 1. **Verify Setup**
Ensure all agent files are in place:
```
backend/app/agents/
├── __init__.py
├── freshness_agent.py      ✅
├── market_agent.py         ✅
├── logistics_agent.py      ✅
├── weather_agent.py        ✅
└── workflow_orchestrator.py ✅
```

### 2. **API Router Registered**
Confirmed in `backend/app/main.py`:
```python
from app.routers import workflow_assessment
app.include_router(workflow_assessment.router, prefix="/api/workflow")
```

### 3. **MongoDB Collections Setup**
Create the following collections in your `neural_roots` database:

#### **wholesalers** collection
```javascript
db.wholesalers.insertMany([
    {
        "crop_name": "tomato",
        "location": "Mumbai",
        "price": 150.00,
        "demand": "HIGH",
        "supply": "MEDIUM",
        "timestamp": new Date()
    },
    {
        "crop_name": "mango",
        "location": "Ratnagiri",
        "price": 400.00,
        "demand": "HIGH",
        "supply": "LOW",
        "timestamp": new Date()
    },
    {
        "crop_name": "onion",
        "location": "Nashik",
        "price": 90.00,
        "demand": "MEDIUM",
        "supply": "HIGH",
        "timestamp": new Date()
    }
])
```

#### **drivers** collection
```javascript
db.drivers.insertMany([
    {
        "name": "Rajesh Kumar",
        "vehicle_type": "refrigerated",
        "capacity": 500,
        "rating": 4.8,
        "status": "available",
        "location": "Nashik",
        "available_hours": 12,
        "capabilities": ["cold_chain", "refrigerated"],
        "phone": "+919876543210"
    },
    {
        "name": "Vikram Singh",
        "vehicle_type": "cold_chain",
        "capacity": 800,
        "rating": 4.9,
        "status": "available",
        "location": "Mumbai",
        "available_hours": 16,
        "capabilities": ["cold_chain"],
        "phone": "+919876543211"
    },
    {
        "name": "Ashok Patel",
        "vehicle_type": "standard",
        "capacity": 300,
        "rating": 4.5,
        "status": "available",
        "location": "Pune",
        "available_hours": 10,
        "capabilities": [],
        "phone": "+919876543212"
    }
])
```

#### **weather** collection (optional - system simulates if empty)
```javascript
db.weather.insertMany([
    {
        "location": "Nashik",
        "timestamp": new Date(),
        "temperature": 24.5,
        "humidity": 72.0,
        "precipitation": 0.0,
        "wind_speed": 5.5,
        "condition": "partly_cloudy"
    }
])
```

---

## 📡 API Usage Examples

### **1. Quick Freshness Check**
```bash
curl -X POST "http://localhost:8000/api/workflow/quick-assessment?crop_name=tomato&temperature=24.5&humidity=72.0&age_hours=12.5&quantity=150&distance_km=180"
```

**Response**:
```json
{
    "crop_name": "tomato",
    "freshness_score": 68.5,
    "freshness_level": "GOOD",
    "recommended_price": 185.50,
    "delivery_mode": "refrigerated",
    "weather_risk": "MEDIUM",
    "recommendations": [
        "Suitable for distribution",
        "Monitor storage conditions closely",
        "Use refrigerated transport recommended"
    ]
}
```

---

### **2. Full Workflow Assessment**
```bash
curl -X POST "http://localhost:8000/api/workflow/assess-freshness" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_data": {
        "crop_name": "tomato",
        "temperature": 24.5,
        "humidity": 72.0,
        "age_hours": 12.5,
        "quantity": 150.0
    },
    "logistics_params": {
        "location": "Nashik",
        "destination": "Mumbai",
        "distance_km": 180.0
    },
    "market_params": {
        "target_location": "Mumbai Mandi",
        "urgency": "MEDIUM"
    }
}'
```

**Response Structure**:
```json
{
    "workflow_id": "2024-01-18T10:30:00.123456",
    "status": "completed",
    "stages": {
        "freshness": {
            "status": "success",
            "data": {
                "freshness_score": 68.5,
                "freshness_level": "GOOD",
                "temperature": 24.5,
                "humidity": 72.0,
                "age_hours": 12.5,
                "temp_score": 90.0,
                "humidity_score": 92.0,
                "age_score": 65.0,
                "recommendations": [...]
            }
        },
        "market": {
            "status": "success",
            "market_data": {...},
            "price_recommendation": {
                "recommended_price": 185.50,
                "base_price": 150.00,
                "pricing_strategy": "MARKET_RATE_PLUS"
            }
        },
        "logistics": {
            "status": "success",
            "delivery_recommendation": {
                "recommended_delivery_mode": "refrigerated",
                "urgency": "HIGH",
                "estimated_delivery_hours": 3.6,
                "estimated_cost": 450.75
            },
            "route_optimization": {
                "recommended_drivers": [
                    {
                        "rank": 1,
                        "driver_name": "Rajesh Kumar",
                        "vehicle": "refrigerated",
                        "suitability_score": 92.5
                    }
                ]
            }
        },
        "weather": {
            "status": "success",
            "data": {
                "risk_level": "MEDIUM",
                "freshness_degradation_rate": 1.2,
                "recommendations": [...]
            }
        }
    },
    "synthesis": {
        "final_freshness_score": 65.2,
        "final_freshness_level": "GOOD",
        "weather_impact": {
            "degradation_rate": 1.2,
            "estimated_loss": 4.32,
            "risk_level": "MEDIUM"
        },
        "market_recommendation": {
            "recommended_price": 185.50,
            "pricing_strategy": "MARKET_RATE_PLUS"
        },
        "comprehensive_recommendations": [
            "⏱️ HIGH PRIORITY: Schedule delivery within 24 hours",
            "💰 Recommended Price: Rs. 185.50",
            "🚚 Use refrigerated delivery",
            "Use refrigerated transport recommended"
        ],
        "action_items": [
            {
                "priority": "🟡 HIGH",
                "action": "Confirm delivery arrangements",
                "details": "Recommended mode: refrigerated"
            },
            {
                "priority": "📊 IMPORTANT",
                "action": "Set market price",
                "details": "Rs. 185.50 based on market analysis"
            }
        ]
    }
}
```

---

### **3. Get Workflow History**
```bash
curl -X GET "http://localhost:8000/api/workflow/workflow-history?limit=5"
```

**Response**:
```json
{
    "status": "success",
    "total_workflows": 5,
    "workflows": [
        {
            "workflow_id": "2024-01-18T10:30:00.123456",
            "timestamp": "2024-01-18T10:30:02.456789",
            "status": "completed",
            "synthesis": {...}
        }
    ]
}
```

---

### **4. Service Health Check**
```bash
curl -X GET "http://localhost:8000/api/workflow/health"
```

**Response**:
```json
{
    "status": "healthy",
    "service": "Agentic AI Workflow",
    "agents": [
        "Freshness Agent",
        "Market Agent",
        "Logistics Agent",
        "Weather Agent"
    ],
    "workflows_executed": 42
}
```

---

## 📊 Understanding Output

### Freshness Score Interpretation
| Score | Level | Action |
|-------|-------|--------|
| 80-100 | 🟢 EXCELLENT | Premium pricing, can wait 3-5 days |
| 60-79 | 🟢 GOOD | Standard pricing, ship within 24-48 hours |
| 40-59 | 🟡 FAIR | Competitive pricing, ship within 12-24 hours |
| 20-39 | 🔴 POOR | Discount pricing, immediate distribution |
| 0-19 | 🔴 CRITICAL | Do not distribute, prevent loss |

### Pricing Strategy
- **PREMIUM_PRICING**: High demand + Excellent freshness (20% markup)
- **ABOVE_MARKET**: Excellent freshness compensates (10% markup)
- **MARKET_RATE_PLUS**: High demand or good freshness (5% markup)
- **MARKET_RATE**: Neutral conditions (no markup)
- **COMPETITIVE_DISCOUNT**: Low demand (5-15% discount)
- **CLEARANCE_PRICING**: Poor freshness (25-50% discount)

### Delivery Modes
| Mode | Best For | Cost | Temperature Control |
|------|----------|------|-------------------|
| 🧊 Cold Chain | POOR/CRITICAL | 1.5x | Rigid (-18 to 4°C) |
| ❄️ Refrigerated | FAIR/GOOD | 1.3x | Dynamic (4-15°C) |
| 🚚 Standard | EXCELLENT | 1.0x | Ambient |

---

## 🔄 Agent Workflow Details

### Stage 1: Freshness Analysis
**Evaluates**: Temperature, humidity, time since harvest
**Calculates**: Base freshness score (0-100)
**Output**: Freshness level, environmental scores, recommendations

### Stage 2: Market Analysis  
**Fetches**: MongoDB wholesalers collection
**Analyzes**: Demand, supply, pricing trends
**Calculates**: Optimal price based on freshness and market conditions
**Output**: Recommended price, pricing strategy, market trend

### Stage 3: Logistics Analysis
**Fetches**: MongoDB drivers collection
**Recommends**: Delivery mode, driver selection, route optimization
**Calculates**: Suitability score for each driver
**Output**: Driver recommendations, estimated delivery time and cost

### Stage 4: Weather Analysis
**Fetches**: MongoDB weather collection (or simulates)
**Analyzes**: Temperature, humidity, precipitation impact
**Calculates**: Freshness degradation during transport
**Output**: Weather risk level, degradation rate, recommendations

### Stage 5: Synthesis
**Combines**: All agent outputs
**Adjusts**: Freshness score for weather impact + logistics preservation
**Generates**: Final assessment, recommendations, action items
**Output**: Complete freshness assessment with strategy

---

## 🛠️ Testing the Workflow

### Test Case 1: Fresh Tomatoes
```bash
curl -X POST "http://localhost:8000/api/workflow/assess-freshness" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_data": {
        "crop_name": "tomato",
        "temperature": 22.0,
        "humidity": 85.0,
        "age_hours": 8.0,
        "quantity": 200.0
    },
    "logistics_params": {
        "location": "Pune",
        "destination": "Mumbai",
        "distance_km": 150.0
    }
}'
```
**Expected**: High freshness score (75+), premium pricing, standard/refrigerated delivery

### Test Case 2: Aging Mangoes
```bash
curl -X POST "http://localhost:8000/api/workflow/assess-freshness" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_data": {
        "crop_name": "mango",
        "temperature": 28.0,
        "humidity": 55.0,
        "age_hours": 72.0,
        "quantity": 100.0
    },
    "logistics_params": {
        "location": "Ratnagiri",
        "destination": "Delhi",
        "distance_km": 1200.0
    }
}'
```
**Expected**: Lower freshness score (40-50), discount pricing, cold_chain delivery recommended

### Test Case 3: Onions (Resilient)
```bash
curl -X POST "http://localhost:8000/api/workflow/assess-freshness" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_data": {
        "crop_name": "onion",
        "temperature": 35.0,
        "humidity": 40.0,
        "age_hours": 120.0,
        "quantity": 500.0
    },
    "logistics_params": {
        "location": "Nashik",
        "destination": "Bangalore",
        "distance_km": 600.0
    }
}'
```
**Expected**: Moderate freshness score (70+), standard pricing, standard delivery sufficient

---

## 📝 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| 503 "No database connection" | Ensure MongoDB is running and MONGODB_URL is set in .env |
| Empty driver/wholesaler results | Populate collections with sample data (see setup section) |
| Slow response times | Check MongoDB query indexes, ensure fresh Python environment |
| Missing weather data | System auto-simulates if collection is empty |
| CORS errors in frontend | Verify frontend origin is in allowed_origins in main.py |

---

## 🚀 Next Steps

1. ✅ **Agents Implemented**: All 4 agents ready
2. ✅ **Orchestrator Created**: Workflow coordination complete
3. ✅ **API Routes Added**: 5 endpoints available
4. **Frontend Integration**: Call `/api/workflow/assess-freshness` from React components
5. **Real Data**: Populate MongoDB with actual wholesaler, driver, weather data
6. **ML Integration**: Add ML model predictions for enhanced freshness scoring
7. **Real-time IoT**: Stream live sensor data to update freshness continuously

---

## 📚 Full Documentation

See [AGENTIC_WORKFLOW.md](./AGENTIC_WORKFLOW.md) for complete technical documentation including:
- Architecture diagrams
- MongoDB schema details
- Algorithm explanations
- Performance optimization tips
- Future enhancement ideas
