# AGENTIC AI WORKFLOW - Complete Documentation

## Overview

The Agentic AI Workflow is a sophisticated multi-agent system that orchestrates four specialized AI agents to provide comprehensive crop freshness assessment, optimal pricing strategies, logistics optimization, and weather impact analysis.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                  WORKFLOW ORCHESTRATOR                           │
│              (Central Coordination Hub)                           │
└───────┬───────────────────────────────────────────────────┬───────┘
        │                                                   │
    ┌───▼────────────┐  ┌──────────────────┐  ┌──────────┐▼──┐
    │  FRESHNESS     │  │  MARKET AGENT    │  │LOGISTICS │ W │
    │     AGENT      │  │                  │  │  AGENT   │ E │
    │                │  │ - Fetch MongoDB  │  │          │ A │
    │ - IoT Analysis │  │   wholesalers    │  │ - Driver │ T │
    │ - Score (0-100)│  │ - Price Analysis │  │   Data   │ H │
    │ - Degradation  │  │ - Pricing        │  │ - Route  │ E │
    │   Prediction   │  │   Strategy       │  │ Optimize │ R │
    └────────────────┘  └──────────────────┘  └─────────┬┘   │
                                                         │     │
                                                    ┌────▼─────┘
                                                    │
                                              - Forecast
                                              - Impact
                                                Analysis
                                              - Degradation
                                                Rate
        
        ↓         ↓              ↓                  ↓
    
    ┌──────────────────────────────────────────────────┐
    │          SYNTHESIS & FINAL ASSESSMENT            │
    │  - Combine all agent outputs                     │
    │  - Calculate adjusted freshness score            │
    │  - Generate recommendations                      │
    │  - Prioritize action items                       │
    └──────────────────────────────────────────────────┘
```

## Agents

### 1. Freshness Agent (`freshness_agent.py`)

**Purpose**: Predicts and scores crop freshness based on environmental conditions

**Inputs**:
- `crop_name`: Name of the crop
- `temperature`: Current temperature (°C)
- `humidity`: Current humidity (%)
- `age_hours`: Hours since harvest/storage
- `iot_data`: Raw sensor data

**Outputs**:
```python
{
    "freshness_score": 75.5,          # 0-100 score
    "freshness_level": "GOOD",         # EXCELLENT, GOOD, FAIR, POOR, CRITICAL
    "temperature": 24.5,
    "humidity": 72.0,
    "age_hours": 12.5,
    "temp_score": 85.0,                # Individual scores
    "humidity_score": 90.0,
    "age_score": 70.0,
    "crop_type": "tomato",
    "recommendations": [...]           # Action items
}
```

**Scoring Formula**:
```
Freshness Score = (Temp Score × 0.30) + (Humidity Score × 0.40) + (Age Score × 0.30)
```

**Freshness Levels**:
- **EXCELLENT** (80-100): Ready for premium market, excellent shelf life
- **GOOD** (60-79): Suitable for distribution, monitor conditions
- **FAIR** (40-59): Use priority shipping, increase urgency
- **POOR** (20-39): Immediate distribution required, high spoilage risk
- **CRITICAL** (0-19): Do not distribute, prevent losses

### 2. Market Agent (`market_agent.py`)

**Purpose**: Fetches wholesale market data and determines optimal pricing strategy

**Inputs**:
- `db`: MongoDB instance
- `crop_name`: Crop to analyze
- `freshness_score`: From Freshness Agent
- `quantity`: Available quantity
- `market_location`: Target market location

**Key Features**:
- Fetches data from `wholesalers` MongoDB collection
- Analyzes demand/supply trends
- Calculates price multipliers based on:
  - Freshness (±20% premium/discount)
  - Market demand (±15% adjustment)
  - Urgency level (±15% adjustment)
  - Quantity available (bulk discounts)

**Output Example**:
```python
{
    "recommended_price": 185.50,
    "base_price": 150.00,
    "price_multiplier": 1.237,
    "pricing_strategy": "PREMIUM_PRICING - High demand + Excellent freshness",
    "price_range": {"min": 127.50, "max": 172.50},
    "market_trend": "high_demand"
}
```

### 3. Logistics Agent (`logistics_agent.py`)

**Purpose**: Recommends delivery modes and optimizes driver allocation

**Inputs**:
- `db`: MongoDB instance
- `freshness_level`: From Freshness Agent
- `distance_km`: Distance to delivery location
- `quantity`: Shipment quantity
- `location`: Current location

**Delivery Modes**:

| Mode | Use Case | Temperature Control | Cost Multiplier |
|------|----------|-------------------|-----------------|
| **Cold Chain** | Critical/Poor freshness | Yes (rigid) | 1.5x |
| **Refrigerated** | Good/Fair freshness | Yes (dynamic) | 1.3x |
| **Standard** | Excellent freshness | No | 1.0x |

**Driver Scoring (0-100)**:
- Capacity match (30 points)
- Rating/Reviews (20 points)
- Vehicle type suitability (20 points)
- Availability hours (10 points)

**Output Example**:
```python
{
    "recommended_delivery_mode": "refrigerated",
    "urgency": "HIGH",
    "feasible": true,
    "delivery_details": {
        "distance_km": 150.0,
        "estimated_delivery_hours": 2.5,
        "estimated_cost": 450.75,
        "temperature_controlled": true
    },
    "recommended_drivers": [
        {
            "rank": 1,
            "driver_id": "D001",
            "driver_name": "Rajesh Kumar",
            "suitability_score": 92.5,
            "estimated_pickup_time": "Immediate (0-1 hour)"
        }
    ]
}
```

### 4. Weather Agent (`weather_agent.py`)

**Purpose**: Analyzes weather conditions and their impact on freshness

**Inputs**:
- `db`: MongoDB instance
- `location`: Location for forecast
- `crop_type`: Crop type (for sensitivity analysis)
- `transportation_duration_hours`: Expected transport time

**Features**:
- Fetches weather forecasts from `weather` collection
- Simulates realistic weather patterns if no data available
- Calculates degradation rate based on:
  - Temperature extremes
  - Humidity levels
  - Precipitation
  - Wind speed
- Crop-specific sensitivity analysis

**Degradation Rates by Risk Level**:
| Risk Level | Rate | Per Hour Impact |
|-----------|------|-----------------|
| LOW | 0.5% | Minimal |
| MEDIUM | 1.0% | ~1% per hour |
| HIGH | 2.0% | ~2% per hour |
| CRITICAL | 4.0% | ~4% per hour |

**Crop Sensitivity**:
```python
{
    "leafy_greens": 1.5,    # Most sensitive (high degradation)
    "tomato": 1.2,
    "cucumber": 1.0,
    "mango": 0.8,
    "onion": 0.4,           # Very resistant
    "potato": 0.5
}
```

**Output Example**:
```python
{
    "risk_level": "MEDIUM",
    "avg_temperature": 28.5,
    "avg_humidity": 68.0,
    "freshness_degradation_rate": 1.2,
    "forecast_points": [...],
    "recommendations": [
        "Use refrigerated transport recommended",
        "Temperature high - keep in shade/cool environment"
    ]
}
```

## Workflow Orchestrator

The `WorkflowOrchestrator` class coordinates all agents and synthesizes their outputs.

### Execution Flow

```
1. INPUT: Crop data with environmental conditions
   ↓
2. STAGE 1: Freshness Analysis
   - Analyze current freshness
   - Predict degradation
   ↓
3. STAGE 2: Market Analysis
   - Fetch wholesale data
   - Determine optimal pricing
   ↓
4. STAGE 3: Logistics Analysis
   - Select delivery mode
   - Find optimal drivers
   ↓
5. STAGE 4: Weather Analysis
   - Forecast conditions
   - Calculate weather impact
   ↓
6. SYNTHESIS: Combine all factors
   - Adjust freshness score for weather/transport
   - Calculate final freshness level
   - Generate comprehensive recommendations
   ↓
7. OUTPUT: Complete assessment with action items
```

### Final Freshness Score Calculation

```
Final Score = Base Freshness - Weather Degradation + Logistics Preservation Bonus

Weather Impact = Degradation Rate × Transport Hours × Crop Sensitivity
Logistics Bonus = 5 pts (cold_chain) | 3 pts (refrigerated) | 0 pts (standard)
```

## API Endpoints

All endpoints are prefixed with `/api/workflow`

### 1. POST `/assess-freshness` - Full Workflow Assessment

**Request**:
```json
{
    "crop_data": {
        "crop_name": "tomato",
        "temperature": 24.5,
        "humidity": 72.0,
        "age_hours": 12.5,
        "quantity": 150.0,
        "iot_data": {
            "device_id": "sensor_001",
            "timestamp": "2024-01-18T10:30:00"
        }
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
}
```

**Response**:
```json
{
    "workflow_id": "2024-01-18T10:30:00.123456",
    "timestamp": "2024-01-18T10:30:02.456789",
    "status": "completed",
    "stages": {
        "freshness": {...},
        "market": {...},
        "logistics": {...},
        "weather": {...}
    },
    "synthesis": {
        "final_freshness_score": 68.5,
        "final_freshness_level": "GOOD",
        "weather_impact": {
            "degradation_rate": 1.2,
            "estimated_loss": 3.6,
            "risk_level": "MEDIUM"
        },
        "market_recommendation": {
            "recommended_price": 185.50,
            "pricing_strategy": "MARKET_RATE_PLUS"
        },
        "logistics_impact": {
            "delivery_mode": "refrigerated",
            "preservation_bonus": 3
        },
        "comprehensive_recommendations": [...],
        "action_items": [...]
    }
}
```

### 2. POST `/quick-assessment` - Rapid Freshness Check

Query parameters:
```
?crop_name=tomato&temperature=24.5&humidity=72.0&age_hours=12.5&quantity=150&distance_km=180
```

**Response** (simplified):
```json
{
    "crop_name": "tomato",
    "freshness_score": 68.5,
    "freshness_level": "GOOD",
    "recommended_price": 185.50,
    "delivery_mode": "refrigerated",
    "weather_risk": "MEDIUM",
    "recommendations": [...]
}
```

### 3. POST `/detailed-analysis` - Full Data Breakdown

Returns complete analysis with all stage details, useful for debugging or detailed reports.

### 4. GET `/workflow-history` - Recent Assessments

**Query**: `?limit=10`

**Response**:
```json
{
    "status": "success",
    "total_workflows": 10,
    "workflows": [...]
}
```

### 5. GET `/health` - Service Status

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

## MongoDB Collections Required

### 1. **wholesalers**
```javascript
{
    "_id": ObjectId,
    "crop_name": "tomato",
    "location": "Mumbai Mandi",
    "price": 150.00,
    "demand": "HIGH",      // HIGH, MEDIUM, LOW
    "supply": "MEDIUM",
    "timestamp": ISODate,
    "wholesaler_id": "W001",
    "warehouse_capacity": 1000
}
```

### 2. **drivers**
```javascript
{
    "_id": ObjectId,
    "name": "Rajesh Kumar",
    "vehicle_type": "refrigerated",  // cold_chain, refrigerated, standard
    "capacity": 500,                 // kg
    "rating": 4.8,                   // 0-5
    "status": "available",           // available, busy, offline
    "location": "Nashik",
    "available_hours": 12,
    "capabilities": ["cold_chain", "refrigerated"],
    "phone": "+91...",
    "vehicle_id": "MH-01-AB-1234"
}
```

### 3. **weather**
```javascript
{
    "_id": ObjectId,
    "location": "Nashik",
    "timestamp": ISODate,
    "temperature": 24.5,
    "humidity": 72.0,
    "precipitation": 0.0,
    "wind_speed": 5.5,
    "condition": "partly_cloudy"
}
```

## Integration Examples

### Example 1: Quick Tomato Assessment
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/workflow/assess-freshness",
        json={
            "crop_data": {
                "crop_name": "tomato",
                "temperature": 24.5,
                "humidity": 72.0,
                "age_hours": 12.5,
                "quantity": 150
            }
        }
    )
    print(response.json())
```

### Example 2: Complete Assessment Flow
```bash
curl -X POST http://localhost:8000/api/workflow/assess-freshness \
  -H "Content-Type: application/json" \
  -d '{
    "crop_data": {
        "crop_name": "mango",
        "temperature": 18.0,
        "humidity": 85.0,
        "age_hours": 24.0,
        "quantity": 500
    },
    "logistics_params": {
        "location": "Ratnagiri",
        "destination": "Delhi",
        "distance_km": 1200
    },
    "market_params": {
        "target_location": "Delhi Mandi",
        "urgency": "HIGH"
    }
}'
```

## Configuration & Setup

### 1. Ensure MongoDB Collections
```javascript
// Create wholesalers collection with sample data
db.wholesalers.insertOne({
    crop_name: "tomato",
    location: "Mumbai Mandi",
    price: 150.00,
    demand: "HIGH",
    supply: "MEDIUM"
})

// Create drivers collection
db.drivers.insertOne({
    name: "Rajesh Kumar",
    vehicle_type: "refrigerated",
    capacity: 500,
    rating: 4.8,
    status: "available",
    location: "Nashik"
})
```

### 2. Update `.env`
```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true
DB_NAME=neural_roots
```

### 3. Register Router in `main.py` (already done)
```python
from app.routers import workflow_assessment
app.include_router(workflow_assessment.router, prefix="/api/workflow", tags=["Workflow Assessment"])
```

## Performance & Optimization

- **Agents run in parallel** through orchestrator
- **MongoDB queries** are optimized with indexes
- **Workflow results** are cached in history (last 1000 executions)
- **Simulated weather** fallback for demo purposes
- **Average response time**: 500-800ms

## Future Enhancements

- [ ] Integration with ML model predictions
- [ ] Real-time IoT streaming data
- [ ] Integration with real weather APIs (OpenWeatherMap, WeatherAPI)
- [ ] Historical trend analysis
- [ ] Predictive alerting system
- [ ] Multi-crop batch optimization
- [ ] Supply chain risk assessment
- [ ] Carbon footprint calculation
