# API Test Examples - Agentic Workflow

## Overview
This file contains example curl requests and Python code to test the complete agentic workflow system.

---

## 1. HEALTH CHECK

### Quick Health Status
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
    "workflows_executed": 0
}
```

---

## 2. QUICK ASSESSMENT (Query Parameters)

### Tomato - Short Distance
```bash
curl -X POST "http://localhost:8000/api/workflow/quick-assessment?\
crop_name=tomato&\
temperature=24.5&\
humidity=72.0&\
age_hours=12.5&\
quantity=150&\
distance_km=100"
```

### Mango - Long Distance
```bash
curl -X POST "http://localhost:8000/api/workflow/quick-assessment?\
crop_name=mango&\
temperature=18.0&\
humidity=85.0&\
age_hours=36.0&\
quantity=300&\
distance_km=800"
```

### Onion - High Temperature
```bash
curl -X POST "http://localhost:8000/api/workflow/quick-assessment?\
crop_name=onion&\
temperature=32.0&\
humidity=45.0&\
age_hours=120.0&\
quantity=500&\
distance_km=200"
```

---

## 3. FULL WORKFLOW ASSESSMENT (JSON Body)

### Example 1: Fresh Tomatoes - Local Delivery

**Request**:
```bash
curl -X POST "http://localhost:8000/api/workflow/assess-freshness" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_data": {
        "crop_name": "tomato",
        "temperature": 22.0,
        "humidity": 85.0,
        "age_hours": 8.0,
        "quantity": 200.0,
        "iot_data": {
            "device_id": "sensor_001",
            "sensor_type": "temperature_humidity"
        }
    },
    "logistics_params": {
        "location": "Pune",
        "destination": "Mumbai",
        "distance_km": 150.0
    },
    "market_params": {
        "target_location": "Mumbai APMC",
        "urgency": "MEDIUM"
    }
}'
```

**Expected Output Highlights**:
- Freshness Score: 75-85 (EXCELLENT/GOOD)
- Price Multiplier: 1.10-1.20
- Delivery Mode: refrigerated/standard
- Cost: ~500-600 Rs
- Weather Risk: LOW

---

### Example 2: Aging Mangoes - Long Distance

**Request**:
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
    },
    "market_params": {
        "target_location": "Delhi Mandi",
        "urgency": "HIGH"
    }
}'
```

**Expected Output Highlights**:
- Freshness Score: 45-55 (FAIR)
- Price Multiplier: 0.90-1.00
- Delivery Mode: cold_chain
- Cost: ~2500-3000 Rs
- Weather Risk: MEDIUM
- Action: URGENT - Immediate dispatch required

---

### Example 3: Resilient Onions - Bulk Order

**Request**:
```bash
curl -X POST "http://localhost:8000/api/workflow/assess-freshness" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_data": {
        "crop_name": "onion",
        "temperature": 35.0,
        "humidity": 40.0,
        "age_hours": 120.0,
        "quantity": 1000.0
    },
    "logistics_params": {
        "location": "Nashik",
        "destination": "Bangalore",
        "distance_km": 600.0
    },
    "market_params": {
        "target_location": "Bangalore Mandi",
        "urgency": "LOW"
    }
}'
```

**Expected Output Highlights**:
- Freshness Score: 70-80 (GOOD)
- Price Multiplier: 0.98-1.02
- Delivery Mode: standard
- Cost: ~1500-2000 Rs
- Bulk Discount: 5% applied
- Weather Risk: LOW

---

### Example 4: Leafy Greens - Express Delivery

**Request**:
```bash
curl -X POST "http://localhost:8000/api/workflow/assess-freshness" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_data": {
        "crop_name": "spinach",
        "temperature": 4.0,
        "humidity": 92.0,
        "age_hours": 6.0,
        "quantity": 50.0
    },
    "logistics_params": {
        "location": "Himachal Pradesh",
        "destination": "Delhi",
        "distance_km": 350.0
    },
    "market_params": {
        "target_location": "Delhi Farm Market",
        "urgency": "CRITICAL"
    }
}'
```

**Expected Output Highlights**:
- Freshness Score: 85-95 (EXCELLENT)
- Price Multiplier: 1.15-1.25
- Delivery Mode: cold_chain
- Cost: ~800-1000 Rs
- Action: Express delivery recommended (same day)

---

## 4. DETAILED ANALYSIS (Complete Breakdown)

### Request:
```bash
curl -X POST "http://localhost:8000/api/workflow/detailed-analysis" \
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
        "location": "Pune",
        "destination": "Mumbai",
        "distance_km": 180.0
    },
    "market_params": {
        "target_location": "Mumbai Mandi",
        "urgency": "MEDIUM"
    }
}'
```

### Response (Partial - Shows All Stages):
```json
{
    "workflow_id": "2024-01-18T10:35:00.123456",
    "timestamp": "2024-01-18T10:35:02.789012",
    "crop_data": {
        "crop_name": "tomato",
        "temperature": 24.5,
        "humidity": 72.0,
        "age_hours": 12.5,
        "quantity": 150.0
    },
    "stages": {
        "freshness": {
            "status": "success",
            "data": {
                "freshness_score": 68.5,
                "freshness_level": "GOOD",
                "temperature": 24.5,
                "humidity": 72.0,
                "age_hours": 12.5,
                "temp_score": 85.0,
                "humidity_score": 92.0,
                "age_score": 65.0,
                "crop_type": "tomato",
                "recommendations": [
                    "Suitable for distribution",
                    "Monitor storage conditions closely",
                    "Prioritize sales within 2-3 days"
                ]
            }
        },
        "market": {
            "status": "success",
            "market_data": {
                "status": "success",
                "crop_name": "tomato",
                "market_data": {
                    "average_price": 150.0,
                    "median_price": 150.0,
                    "min_price": 120.0,
                    "max_price": 180.0,
                    "price_volatility": 25.0,
                    "sample_size": 5
                },
                "market_trend": "normal_demand",
                "demand_distribution": {
                    "high": 1,
                    "medium": 3,
                    "low": 1,
                    "total_wholesalers": 5
                }
            },
            "price_recommendation": {
                "status": "success",
                "crop_name": "tomato",
                "recommended_price": 172.5,
                "base_price": 150.0,
                "price_multiplier": 1.15,
                "freshness_multiplier": 1.1,
                "demand_multiplier": 1.0,
                "pricing_strategy": "MARKET_RATE_PLUS - Good freshness compensates"
            }
        },
        "logistics": {
            "status": "success",
            "delivery_recommendation": {
                "status": "success",
                "recommended_delivery_mode": "refrigerated",
                "urgency": "NORMAL",
                "feasible": true,
                "delivery_details": {
                    "distance_km": 180.0,
                    "estimated_delivery_hours": 2.57,
                    "estimated_cost": 450.75,
                    "temperature_controlled": true
                }
            },
            "available_drivers": {
                "status": "success",
                "drivers_count": 2,
                "drivers": [
                    {
                        "_id": "driver_001",
                        "name": "Rajesh Kumar",
                        "vehicle_type": "refrigerated",
                        "capacity": 500,
                        "rating": 4.8,
                        "status": "available",
                        "location": "Pune",
                        "available_hours": 12
                    }
                ]
            },
            "route_optimization": {
                "status": "success",
                "delivery_location": "Mumbai",
                "recommended_drivers": [
                    {
                        "rank": 1,
                        "driver_id": "driver_001",
                        "driver_name": "Rajesh Kumar",
                        "vehicle": "refrigerated",
                        "rating": 4.8,
                        "suitability_score": 92.5,
                        "estimated_pickup_time": "Immediate (0-1 hour)"
                    }
                ]
            }
        },
        "weather": {
            "status": "success",
            "data": {
                "status": "success",
                "location": "Pune",
                "crop_type": "tomato",
                "transportation_duration_hours": 3.6,
                "weather_forecast": [
                    {
                        "timestamp": "2024-01-18T10:35:00",
                        "temperature": 25.5,
                        "humidity": 70.0,
                        "precipitation": 0.0,
                        "wind_speed": 6.5,
                        "condition": "partly_cloudy"
                    }
                ],
                "impact_analysis": {
                    "avg_temperature": 25.2,
                    "avg_humidity": 71.0,
                    "max_precipitation": 0.0,
                    "max_wind_speed": 6.8,
                    "risk_score": 20,
                    "risk_level": "LOW"
                },
                "freshness_degradation_rate": 0.78,
                "recommendations": [
                    "Weather conditions favorable for transport"
                ]
            }
        }
    },
    "synthesis": {
        "final_freshness_score": 65.2,
        "final_freshness_level": "GOOD",
        "base_freshness_score": 68.5,
        "weather_impact": {
            "degradation_rate": 0.78,
            "estimated_loss": 2.81,
            "risk_level": "LOW"
        },
        "logistics_impact": {
            "delivery_mode": "refrigerated",
            "preservation_bonus": 3,
            "feasible": true
        },
        "market_recommendation": {
            "recommended_price": 172.5,
            "pricing_strategy": "MARKET_RATE_PLUS - Good freshness compensates",
            "market_trend": "normal_demand"
        },
        "comprehensive_recommendations": [
            "Current Status: GOOD (Score: 65/100)",
            "💰 Recommended Price: Rs. 172.50 (MARKET_RATE_PLUS - Good freshness compensates)",
            "🚚 Use refrigerated delivery",
            "Weather conditions favorable for transport"
        ],
        "action_items": [
            {
                "priority": "🟢 NORMAL",
                "action": "Confirm delivery arrangements",
                "details": "Recommended mode: refrigerated"
            },
            {
                "priority": "📊 IMPORTANT",
                "action": "Set market price",
                "details": "Rs. 172.50 based on market analysis"
            }
        ]
    },
    "status": "completed"
}
```

---

## 5. WORKFLOW HISTORY

### Get Last 5 Workflows:
```bash
curl -X GET "http://localhost:8000/api/workflow/workflow-history?limit=5"
```

### Get Last 20 Workflows:
```bash
curl -X GET "http://localhost:8000/api/workflow/workflow-history?limit=20"
```

**Response**:
```json
{
    "status": "success",
    "total_workflows": 5,
    "workflows": [
        {
            "workflow_id": "2024-01-18T10:35:00.123456",
            "timestamp": "2024-01-18T10:35:02.789012",
            "status": "completed",
            "synthesis": {
                "final_freshness_score": 65.2,
                "final_freshness_level": "GOOD",
                "market_recommendation": {...},
                "action_items": [...]
            }
        }
    ]
}
```

---

## 6. PYTHON CLIENT EXAMPLES

### Using `httpx` (Async):
```python
import httpx
import asyncio
import json

async def assess_crop_freshness():
    """Test full workflow assessment"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/workflow/assess-freshness",
            json={
                "crop_data": {
                    "crop_name": "tomato",
                    "temperature": 24.5,
                    "humidity": 72.0,
                    "age_hours": 12.5,
                    "quantity": 150.0
                },
                "logistics_params": {
                    "location": "Pune",
                    "destination": "Mumbai",
                    "distance_km": 180.0
                },
                "market_params": {
                    "target_location": "Mumbai Mandi",
                    "urgency": "MEDIUM"
                }
            }
        )
        
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Freshness: {result['synthesis']['final_freshness_level']}")
        print(f"Price: Rs. {result['synthesis']['market_recommendation']['recommended_price']}")
        return result

# Run the test
asyncio.run(assess_crop_freshness())
```

### Using `requests` (Sync):
```python
import requests
import json

def quick_assessment():
    """Quick freshness check"""
    params = {
        "crop_name": "mango",
        "temperature": 18.0,
        "humidity": 85.0,
        "age_hours": 36.0,
        "quantity": 300,
        "distance_km": 800
    }
    
    response = requests.post(
        "http://localhost:8000/api/workflow/quick-assessment",
        params=params
    )
    
    data = response.json()
    print(f"\nCrop: {data['crop_name']}")
    print(f"Freshness: {data['freshness_level']} ({data['freshness_score']}/100)")
    print(f"Recommended Price: Rs. {data['recommended_price']}")
    print(f"Delivery Mode: {data['delivery_mode']}")
    print(f"Weather Risk: {data['weather_risk']}")
    
    return data

# Run the test
quick_assessment()
```

---

## 7. INTEGRATION WITH FRONTEND

### React Component Example:
```typescript
import React, { useState } from 'react';

interface FreshnessAssessment {
    final_freshness_score: number;
    final_freshness_level: string;
    recommended_price: number;
    delivery_mode: string;
}

export const FreshnessAssessmentComponent = () => {
    const [result, setResult] = useState<FreshnessAssessment | null>(null);
    const [loading, setLoading] = useState(false);

    const assessFreshness = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/workflow/assess-freshness', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    crop_data: {
                        crop_name: 'tomato',
                        temperature: 24.5,
                        humidity: 72.0,
                        age_hours: 12.5,
                        quantity: 150
                    },
                    logistics_params: {
                        location: 'Pune',
                        destination: 'Mumbai',
                        distance_km: 180
                    }
                })
            });

            const data = await response.json();
            setResult(data.synthesis);
        } catch (error) {
            console.error('Assessment failed:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="assessment-panel">
            <button onClick={assessFreshness} disabled={loading}>
                {loading ? 'Assessing...' : 'Assess Freshness'}
            </button>

            {result && (
                <div className="results">
                    <div className={`status status-${result.final_freshness_level.toLowerCase()}`}>
                        <span>{result.final_freshness_level}</span>
                        <span>{result.final_freshness_score}/100</span>
                    </div>
                    <div className="pricing">
                        <span>Recommended Price: Rs. {result.recommended_price}</span>
                    </div>
                    <div className="logistics">
                        <span>Delivery Mode: {result.delivery_mode}</span>
                    </div>
                </div>
            )}
        </div>
    );
};
```

---

## 8. BATCH PROCESSING

### Process Multiple Crops:
```bash
#!/bin/bash

# Array of crop data
crops=(
    '{"crop_name":"tomato","temperature":24.5,"humidity":72.0,"age_hours":12.5,"quantity":150}'
    '{"crop_name":"mango","temperature":18.0,"humidity":85.0,"age_hours":36.0,"quantity":300}'
    '{"crop_name":"onion","temperature":35.0,"humidity":40.0,"age_hours":120.0,"quantity":500}'
)

# Process each crop
for crop in "${crops[@]}"; do
    echo "Processing: $crop"
    curl -X POST "http://localhost:8000/api/workflow/quick-assessment" \
      -H "Content-Type: application/json" \
      -d "$(cat <<EOF
{
    "crop_data": $crop
}
EOF
)" | jq '.freshness_level, .recommended_price'
done
```

---

## 9. RESPONSE TIME MONITORING

```bash
# Measure API response time
time curl -X POST "http://localhost:8000/api/workflow/quick-assessment?\
crop_name=tomato&temperature=24.5&humidity=72.0&age_hours=12.5&quantity=150&distance_km=100"

# Expected: 200-800ms total time
```

---

## 10. ERROR HANDLING

### Missing Required Fields:
```bash
curl -X POST "http://localhost:8000/api/workflow/assess-freshness" \
  -H "Content-Type: application/json" \
  -d '{"crop_data": {}}'
```

**Expected Error**:
```json
{
    "detail": [
        {
            "loc": ["body", "crop_data", "crop_name"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

### Database Connection Error:
```json
{
    "status": "error",
    "error": "Cannot connect to MongoDB. Ensure MONGODB_URL is set in .env"
}
```

---

## Notes

- All timestamps are in ISO 8601 format
- Prices are in Indian Rupees (Rs.)
- Distances are in kilometers
- Temperatures are in Celsius
- Humidity is in percentage
- Age is in hours since harvest
