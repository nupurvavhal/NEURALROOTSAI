# Backend Connection Quick Start Guide
## Get Your Dashboard Live in 30 Minutes

**Project:** Neural Roots 🌱  
**Last Updated:** January 16, 2026  
**For:** Frontend developers ready to connect the FastAPI backend

---

## Prerequisites Checklist

- [ ] Backend deployed and running (Railway/Render/Local)
- [ ] Backend API URL available (e.g., `https://yourapp.railway.app`)
- [ ] Twilio WhatsApp configured (optional for Phase 1)
- [ ] Supabase database set up (optional - can use mock_db.py)
- [ ] IoT devices registered (optional for Phase 1)

---

## 🚀 30-Minute Integration Path

### Step 1: Configure Environment (5 minutes)

Create `.env.local` in your frontend root:

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_BACKEND_ENV=development

# For Production
# NEXT_PUBLIC_API_URL=https://yourapp.railway.app
# NEXT_PUBLIC_BACKEND_ENV=production

# Optional: WhatsApp Integration
NEXT_PUBLIC_TWILIO_WHATSAPP=+14155238886
```

### Step 2: Test Backend Connection (5 minutes)

```bash
# Terminal 1: Start backend (if local)
cd ../backend
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Test API
curl http://localhost:8000/api/v1/prices
# Should return: {"success": true, "data": {...}}
```

### Step 3: Enable Backend in Frontend (2 minutes)

Edit `lib/config.ts`:

```typescript
export const FEATURE_FLAGS = {
  USE_BACKEND_API: true,        // ← Change this from false
  USE_MOCK_DATA: false,         // ← Change this from true
  
  // Optional features (enable when ready)
  ENABLE_IOT_MONITORING: false,
  ENABLE_WHATSAPP_INTEGRATION: false,
  ENABLE_REAL_TIME_TRACKING: true,
};
```

### Step 4: Install Dependencies (3 minutes)

```bash
npm install axios
# or
yarn add axios

# Optional: For WebSocket support
npm install socket.io-client
```

### Step 5: Create API Service Files (10 minutes)

Already created! Just verify these files exist:
- ✅ `types/backend.ts` - Type definitions
- ✅ `lib/config.ts` - Configuration
- ✅ `BACKEND_INTEGRATION.md` - Complete guide

Now create the API service:

```bash
mkdir -p lib/api/services
touch lib/api/client.ts
touch lib/api/services/market.service.ts
touch lib/api/services/driver.service.ts
```

Copy this minimal API client into `lib/api/client.ts`:

```typescript
import axios, { AxiosInstance } from 'axios';
import { API_CONFIG } from '../config';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.REQUEST_TIMEOUT,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  async get<T>(url: string): Promise<T> {
    const response = await this.client.get(url);
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post(url, data);
    return response.data;
  }
}

export const apiClient = new ApiClient();
```

### Step 6: Update Components (5 minutes)

Replace mock data loading in `app/page.tsx`:

```typescript
// BEFORE (Mock Data)
import { farmersData, driversData, marketItemsData } from '@/data/mockData';
const [farmers, setFarmers] = useState(farmersData);

// AFTER (Backend Connected)
import { apiClient } from '@/lib/api/client';
import { FEATURE_FLAGS } from '@/lib/config';
import { farmersData } from '@/data/mockData';  // Fallback

const [farmers, setFarmers] = useState<Farmer[]>([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  async function loadData() {
    try {
      if (FEATURE_FLAGS.USE_BACKEND_API) {
        // Fetch from backend
        const response = await apiClient.get('/api/v1/farmers');
        setFarmers(response.data || []);
      } else {
        // Use mock data
        setFarmers(farmersData);
      }
    } catch (error) {
      console.error('Failed to load farmers:', error);
      setFarmers(farmersData);  // Fallback to mock
    } finally {
      setLoading(false);
    }
  }
  
  loadData();
}, []);
```

### Step 7: Verify & Test (2 minutes)

```bash
# Start your frontend
npm run dev

# Open browser
http://localhost:3000

# Check browser console
# You should see API requests to http://localhost:8000
```

---

## 🔍 Troubleshooting

### Issue: "Network Error" or CORS

**Solution:** Backend must allow CORS from your frontend:

```python
# Backend: main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Backend returns wrong data format

**Solution:** Check backend endpoints match frontend expectations:

```bash
# Test backend price endpoint
curl http://localhost:8000/api/v1/prices

# Should return:
{
  "success": true,
  "data": {
    "potatoes": {"mandi": 45.0, "village": 25.0, "unit": "kg"}
  }
}
```

If not, you need to implement the endpoint first. See `BACKEND_INTEGRATION.md`.

### Issue: Mock data still showing

**Solution:** Check feature flag:

```typescript
// lib/config.ts
USE_BACKEND_API: true  // Must be true
USE_MOCK_DATA: false   // Must be false
```

---

## 📊 Backend Endpoints You Need

### Must Have (Phase 1)

```
GET  /api/v1/prices           - List all crop prices
GET  /api/v1/prices/{crop}    - Get specific crop
GET  /api/v1/drivers          - List all drivers
POST /whatsapp                - WhatsApp webhook (Twilio)
```

### Should Have (Phase 2)

```
GET  /api/v1/farmers          - List farmers
GET  /api/v1/bookings         - List bookings
POST /api/v1/bookings         - Create booking
GET  /api/v1/bookings/{id}/track - Track booking
```

### Nice to Have (Phase 3)

```
GET  /api/v1/iot/readings/{device_id} - IoT sensor data
WS   /ws/drivers              - Real-time driver tracking
WS   /ws/iot/alerts           - IoT alert stream
```

---

## 🎯 Feature Rollout Plan

### Week 1: Basic API Connection
- [x] Price data from backend
- [x] Driver list from backend
- [ ] Test with mock WhatsApp conversation
- [ ] Verify data displays correctly

### Week 2: Booking System
- [ ] Implement booking creation
- [ ] Connect to LangGraph agent
- [ ] Display AI-generated negotiation messages
- [ ] Add payment link generation

### Week 3: IoT Integration
- [ ] Show IoT device status
- [ ] Display real-time sensor readings
- [ ] Add freshness score badges
- [ ] Implement spoilage alerts

### Week 4: Real-time Features
- [ ] WebSocket for driver tracking
- [ ] Live price updates
- [ ] Push notifications
- [ ] Map tracking with live GPS

---

## 🧪 Testing Workflow

### 1. Test Backend Locally

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Test API
curl http://localhost:8000/api/v1/prices
```

### 2. Test Frontend with Backend

```bash
# Terminal 3: Frontend
cd frontend
npm run dev

# Browser: Check Network tab
# Should see requests to http://localhost:8000
```

### 3. Test WhatsApp Integration (Optional)

```bash
# Use Twilio WhatsApp Sandbox
# Send message: "tomatoes"
# Should get AI response about prices
```

---

## 🚀 Deployment

### Backend Deployment (Railway)

```bash
# From backend repo
git add .
git commit -m "Add API endpoints"
git push origin main

# Railway will auto-deploy
# Note the URL: https://yourapp.railway.app
```

### Frontend Deployment (Vercel)

```bash
# From frontend repo
# Update .env.production
NEXT_PUBLIC_API_URL=https://yourapp.railway.app
NEXT_PUBLIC_BACKEND_ENV=production

# Deploy
vercel --prod
```

### Update Twilio Webhook

```
Webhook URL: https://yourapp.railway.app/whatsapp
Method: POST
```

---

## 📝 Minimal Backend Implementation

If your backend is not ready, here's the bare minimum:

### `/api/v1/prices` endpoint

```python
# backend/main.py
from fastapi import FastAPI
from data.mock_db import MARKET_DATA

app = FastAPI()

@app.get("/api/v1/prices")
def get_prices():
    return {
        "success": True,
        "data": MARKET_DATA,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/prices/{crop_name}")
def get_crop_price(crop_name: str):
    crop_data = MARKET_DATA.get(crop_name.lower())
    if not crop_data:
        return {"success": False, "error": "Crop not found"}
    
    return {
        "success": True,
        "data": {
            "crop": crop_name,
            "mandi_price": crop_data["mandi"],
            "village_price": crop_data["village"],
            "unit": crop_data["unit"],
            "profit_gap": ((crop_data["mandi"] - crop_data["village"]) / crop_data["village"]) * 100
        }
    }
```

### `/api/v1/drivers` endpoint

```python
from data.mock_db import DRIVERS

@app.get("/api/v1/drivers")
def get_drivers(available: bool = None):
    drivers = DRIVERS
    if available is not None:
        drivers = [d for d in drivers if d["available"] == available]
    
    return {
        "success": True,
        "data": drivers
    }
```

---

## 🎉 Success Criteria

You know it's working when:

✅ Browser console shows API requests to backend  
✅ Price data displays in Market Terminal  
✅ Driver locations appear on map  
✅ No "mock data" warnings in console  
✅ Real-time updates work (if enabled)  
✅ WhatsApp conversation creates bookings (if enabled)

---

## 📚 Additional Resources

- **Full Integration Guide:** [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md)
- **Backend Types:** [types/backend.ts](types/backend.ts)
- **API Config:** [lib/config.ts](lib/config.ts)
- **Mock Data Mapping:** [MOCK_DATA_DOCUMENTATION.md](MOCK_DATA_DOCUMENTATION.md)

---

## 💡 Pro Tips

1. **Start Small:** Get prices working first, then add more endpoints
2. **Keep Mock Data:** Use as fallback if backend fails
3. **Feature Flags:** Toggle features on/off easily
4. **Error Handling:** Always have fallbacks to mock data
5. **Test Locally:** Run both frontend and backend locally first
6. **Incremental:** Deploy one feature at a time
7. **Monitor:** Check browser console and network tab constantly

---

## 🆘 Need Help?

**Common Issues:**
- CORS errors → Configure backend CORS middleware
- Wrong data format → Check endpoint response structure
- Connection refused → Verify backend is running
- Mock data still showing → Check FEATURE_FLAGS in config

**Debug Checklist:**
- [ ] Backend is running and accessible
- [ ] `.env.local` has correct API URL
- [ ] `FEATURE_FLAGS.USE_BACKEND_API = true`
- [ ] CORS is configured in backend
- [ ] Endpoints return correct JSON format
- [ ] Browser console shows no errors

---

**Last Updated:** January 16, 2026  
**Status:** Ready to Connect  
**Estimated Time:** 30 minutes for basic connection  
**Next Step:** Configure `.env.local` and test backend connection
