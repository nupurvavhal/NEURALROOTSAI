# Backend Integration Strategy
## Neural Roots 🌱 - Seamless Frontend-Backend Connection Guide

**Created:** January 16, 2026  
**Purpose:** Bridge frontend mock data with backend API structure for IoT-enabled agricultural logistics

---

## Table of Contents
1. [Integration Overview](#integration-overview)
2. [Data Structure Mapping](#data-structure-mapping)
3. [API Endpoint Implementation](#api-endpoint-implementation)
4. [IoT Integration Points](#iot-integration-points)
5. [Frontend Modifications Required](#frontend-modifications-required)
6. [API Service Layer](#api-service-layer)
7. [Environment Configuration](#environment-configuration)
8. [Migration Strategy](#migration-strategy)

---

## Integration Overview

### Current State (Mock Data)
- **Frontend:** TypeScript interfaces with mock data arrays
- **Storage:** localStorage for persistence
- **Updates:** Client-side only

### Target State (Backend Connected)
- **Frontend:** Same TypeScript interfaces + Backend API fields
- **Storage:** Supabase PostgreSQL via FastAPI
- **Updates:** Real-time from IoT sensors + AI agents
- **Communication:** REST API + WebSocket for live tracking

### Backend Architecture Components
```
┌─────────────────┐
│   FRONTEND      │
│   (Next.js)     │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐      ┌──────────────┐
│   FASTAPI       │◄────►│  LangGraph   │
│   Backend       │      │  AI Agents   │
└────────┬────────┘      └──────────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
┌────────┐ ┌─────────┐ ┌──────────┐
│Supabase│ │IoT      │ │Twilio    │
│Database│ │Sensors  │ │WhatsApp  │
└────────┘ └─────────┘ └──────────┘
```

---

## Data Structure Mapping

### 1. Market Prices (Crops)

#### Backend Structure
```python
MARKET_DATA = {
    "potatoes": {"mandi": 45.0, "village": 25.0, "unit": "kg"},
    "jowar": {"mandi": 32.0, "village": 18.0, "unit": "kg"},
    "tomatoes": {"mandi": 60.0, "village": 20.0, "unit": "kg"},
    "onions": {"mandi": 40.0, "village": 22.0, "unit": "kg"}
}
```

#### Frontend Interface (Current)
```typescript
interface MarketItem {
  id: string;
  cropName: string;
  mandiName: string;
  price: number;              // Backend: mandi price
  trend: 'up' | 'down';
  spoilageRisk: 'Low' | 'Medium' | 'Critical';
}
```

#### Enhanced Frontend Interface (Backend-Compatible)
```typescript
interface MarketItem {
  id: string;
  cropName: string;
  mandiName: string;
  
  // Price Data (from backend MARKET_DATA)
  mandiPrice: number;         // Backend: mandi
  villagePrice: number;       // Backend: village
  unit: string;               // Backend: unit
  profitGap: number;          // Calculated: ((mandi - village) / village) * 100
  
  // Market Intelligence
  trend: 'up' | 'down';
  spoilageRisk: 'Low' | 'Medium' | 'Critical';
  
  // IoT Data (NEW)
  freshnessScore?: number;    // 0-100 from IoT sensors
  temperature?: number;        // Celsius (from DHT11/DHT22)
  humidity?: number;           // Percentage (from DHT11/DHT22)
  shelfLifeHours?: number;     // AI prediction from sensors
  lastImageUrl?: string;       // ESP32-CAM snapshot
  aiHealthStatus?: 'excellent' | 'good' | 'warning' | 'critical';
  
  // Metadata
  lastUpdated: string;         // ISO timestamp
  region?: string;             // Maharashtra region
}
```

### 2. Drivers/Transport

#### Backend Structure
```python
DRIVERS = [
    {"id": "D1", "name": "Rajesh", "vehicle": "Mini Truck", 
     "route": "Village-to-City", "available": True}
]
```

#### Frontend Interface (Current)
```typescript
interface Driver {
  id: string;
  name: string;
  vehicleType: string;
  lat: number;
  lng: number;
  status: 'Available' | 'Busy';
  currentLoad: string;
  phone: string;
}
```

#### Enhanced Frontend Interface (Backend-Compatible)
```typescript
interface Driver {
  id: string;
  name: string;
  
  // Vehicle Info (Backend compatible)
  vehicleType: string;        // Backend: vehicle
  vehicleNumber?: string;     // NEW: Registration number
  
  // Location (Real-time GPS)
  lat: number;
  lng: number;
  route: string;              // Backend: route (e.g., "Village-to-City")
  
  // Availability
  available: boolean;         // Backend: available
  status: 'Available' | 'Busy' | 'Offline';
  currentLoad: string;
  
  // Contact
  phone: string;
  whatsappNumber?: string;    // For WhatsApp integration
  
  // IoT Tracking (NEW)
  lastSeen?: string;          // ISO timestamp
  currentSpeed?: number;      // km/h from GPS
  eta?: string;               // "2h 20m"
  distanceToPickup?: number;  // km
  
  // Performance Metrics
  rating?: number;            // 0-5
  completedTrips?: number;
  onTimePercentage?: number;
}
```

### 3. Farmers

#### Backend Integration (Supabase Schema)
```sql
CREATE TABLE farmers (
    id UUID PRIMARY KEY,
    phone VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(100),
    village VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en'
);
```

#### Enhanced Frontend Interface (Backend-Compatible)
```typescript
interface Transaction {
  date: string;
  crop: string;
  amount: string;
  soldTo: string;
  revenue: number;
  
  // NEW: Backend tracking
  bookingId?: string;         // Links to bookings table
  driverId?: string;
  transportCost?: number;
  netProfit?: number;
}

interface Farmer {
  id: string;                 // Backend: UUID
  name: string;
  village: string;
  photoUrl: string;
  
  // Contact (Backend)
  phone: string;              // Backend: phone (primary identifier)
  whatsappNumber?: string;
  language?: 'en' | 'hi' | 'mr';  // English/Hindi/Marathi
  
  // Farmer Type (NEW for Urban Agriculture)
  farmerType: 'rural' | 'urban_terrace' | 'urban_vertical';
  landSize?: string;          // "5 acres" or "terrace 500 sqft"
  
  // Performance
  rating: number;
  totalEarnings: number;
  status: 'Connected' | 'Pending' | 'Verified';
  
  // Transaction History
  history: Transaction[];
  
  // IoT Integration (NEW)
  iotDeviceId?: string;       // ESP32 device ID
  hasIoTKit?: boolean;        // Has Freshness Guard device
  
  // Metadata
  createdAt?: string;
  lastActive?: string;
}
```

### 4. Bookings/Orders (NEW Entity)

#### Backend Schema (Supabase)
```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY,
    farmer_id UUID REFERENCES farmers(id),
    driver_id UUID REFERENCES drivers(id),
    crop VARCHAR(50),
    quantity DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending'
);
```

#### Frontend Interface (NEW)
```typescript
interface Booking {
  id: string;
  
  // Participants
  farmerId: string;
  farmerName: string;
  driverId: string;
  driverName: string;
  
  // Crop Details
  crop: string;
  quantity: number;           // in kg
  unit: string;
  
  // Pricing
  villagePrice: number;       // Price farmer would get locally
  mandiPrice: number;         // Price at market
  transportCost: number;
  netProfit: number;          // (mandiPrice - villagePrice - transportCost) * quantity
  profitMargin: number;       // Percentage
  
  // Locations
  pickupLocation: string;
  pickupLat: number;
  pickupLng: number;
  dropoffLocation: string;
  dropoffLat: number;
  dropoffLng: number;
  
  // Timing
  pickupTime: string;         // ISO timestamp
  estimatedDelivery: string;
  actualDelivery?: string;
  
  // Status Flow
  status: 'pending' | 'confirmed' | 'driver_assigned' | 
          'in_transit' | 'delivered' | 'completed' | 'cancelled';
  
  // Payment
  paymentStatus: 'pending' | 'paid' | 'failed';
  paymentLink?: string;       // Razorpay/UPI link
  paymentMethod?: 'upi' | 'cash' | 'bank_transfer';
  
  // IoT Monitoring (NEW)
  currentTemp?: number;
  currentHumidity?: number;
  freshnessScore?: number;
  alerts?: Array<{
    time: string;
    type: 'temperature' | 'humidity' | 'spoilage' | 'delay';
    message: string;
    severity: 'info' | 'warning' | 'critical';
  }>;
  
  // Tracking
  trackingLink?: string;
  driverLocation?: { lat: number; lng: number; timestamp: string };
  
  // Metadata
  createdAt: string;
  updatedAt: string;
  aiNegotiationText?: string; // Message from LangGraph agent
}
```

### 5. IoT Sensor Data (NEW Entity)

#### Frontend Interface (NEW)
```typescript
interface IoTSensorReading {
  id: string;
  deviceId: string;           // ESP32 device identifier
  
  // Linked Entity
  entityType: 'farmer' | 'booking' | 'storage';
  entityId: string;
  
  // Environmental Data (DHT11/DHT22)
  temperature: number;        // Celsius
  humidity: number;           // Percentage
  
  // Visual AI (ESP32-CAM)
  imageUrl?: string;          // S3/cloud storage URL
  imageTimestamp: string;
  
  // AI Analysis
  aiAnalysis: {
    freshnessScore: number;   // 0-100
    healthStatus: 'excellent' | 'good' | 'warning' | 'critical';
    detectedIssues: string[]; // ['browning_detected', 'moisture_spots']
    shelfLifeHours: number;   // Predicted remaining time
    confidence: number;       // AI confidence 0-1
  };
  
  // Alerts
  alertGenerated: boolean;
  alertType?: 'temperature_high' | 'humidity_high' | 'spoilage_detected';
  alertMessage?: string;
  
  // Metadata
  timestamp: string;
  location?: { lat: number; lng: number };
  batteryLevel?: number;      // Device battery percentage
}
```

---

## API Endpoint Implementation

### Base Configuration
```typescript
// lib/config.ts
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  WEBSOCKET_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
};
```

### Required Backend Endpoints

#### 1. Market/Price Endpoints

**GET /api/v1/prices**
```typescript
// Request
GET /api/v1/prices

// Response
{
  "success": true,
  "data": {
    "potatoes": {
      "mandi": 45.0,
      "village": 25.0,
      "unit": "kg",
      "profit_margin": 80.0,
      "trend": "up",
      "spoilage_risk": "low",
      "region": "Pune"
    }
  },
  "timestamp": "2026-01-16T10:30:00Z"
}
```

**GET /api/v1/prices/{crop_name}**
```typescript
// Request
GET /api/v1/prices/tomatoes?include_iot=true

// Response
{
  "success": true,
  "data": {
    "crop": "tomatoes",
    "mandi_price": 60.0,
    "village_price": 20.0,
    "unit": "kg",
    "profit_gap": 200.0,
    "iot_data": {
      "freshness_score": 85,
      "temperature": 8.5,
      "humidity": 75,
      "shelf_life_hours": 48,
      "health_status": "good",
      "last_image_url": "https://iot.harvest.in/img/12345.jpg"
    }
  }
}
```

#### 2. Driver/Logistics Endpoints

**GET /api/v1/drivers**
```typescript
// Request
GET /api/v1/drivers?available=true&route=Village-to-City

// Response
{
  "success": true,
  "data": [
    {
      "id": "D1",
      "name": "Rajesh",
      "vehicle": "Mini Truck",
      "route": "Village-to-City",
      "available": true,
      "current_location": {"lat": 18.5204, "lng": 73.8567},
      "phone": "+91-9876543210",
      "rating": 4.8,
      "eta_to_you": "15 mins"
    }
  ]
}
```

**GET /api/v1/drivers/{driver_id}/location**
```typescript
// Real-time tracking
GET /api/v1/drivers/D1/location

// Response
{
  "success": true,
  "data": {
    "driver_id": "D1",
    "lat": 18.5214,
    "lng": 73.8577,
    "speed": 45,
    "heading": 135,
    "timestamp": "2026-01-16T10:32:15Z",
    "status": "in_transit",
    "current_booking_id": "B456"
  }
}
```

#### 3. Farmer Endpoints

**GET /api/v1/farmers**
```typescript
GET /api/v1/farmers?type=urban_terrace

Response: Array of Farmer objects
```

**POST /api/v1/farmers**
```typescript
// Register new farmer
POST /api/v1/farmers

Body:
{
  "name": "Amit Sharma",
  "phone": "+919876543210",
  "village": "Terrace Garden, Bandra",
  "farmer_type": "urban_terrace",
  "language": "en",
  "has_iot_kit": true
}
```

**GET /api/v1/farmers/{farmer_id}/iot-status**
```typescript
// Check IoT device health
GET /api/v1/farmers/F001/iot-status

Response:
{
  "device_id": "ESP32_001",
  "online": true,
  "battery": 85,
  "last_reading": "2026-01-16T10:30:00Z",
  "current_conditions": {
    "temperature": 12.5,
    "humidity": 65,
    "freshness_score": 92
  }
}
```

#### 4. Booking/Order Endpoints

**POST /api/v1/bookings**
```typescript
// Create new booking
POST /api/v1/bookings

Body:
{
  "farmer_id": "F123",
  "crop": "tomatoes",
  "quantity": 50,
  "pickup_location": "Terrace Garden, Bandra",
  "pickup_lat": 19.0596,
  "pickup_lng": 72.8295,
  "preferred_time": "2026-01-17T08:00:00Z"
}

Response:
{
  "success": true,
  "booking": {
    "id": "B789",
    "status": "pending",
    "ai_message": "🌾 Hi Amit! I found that tomatoes sell for ₹60/kg at mandi vs ₹20/kg locally. You can earn ₹2000 profit on 50kg! Driver Rajesh is available. Reply YES to confirm.",
    "profit_analysis": {
      "village_total": 1000,
      "mandi_total": 3000,
      "transport_cost": 800,
      "net_profit": 1200
    }
  }
}
```

**GET /api/v1/bookings/{booking_id}**
```typescript
GET /api/v1/bookings/B789

Response: Full Booking object with real-time updates
```

**GET /api/v1/bookings/{booking_id}/track**
```typescript
// Live tracking
GET /api/v1/bookings/B789/track

Response:
{
  "booking_id": "B789",
  "status": "in_transit",
  "driver_location": {
    "lat": 19.0610,
    "lng": 72.8310,
    "timestamp": "2026-01-16T10:35:00Z"
  },
  "iot_data": {
    "temperature": 10.2,
    "humidity": 68,
    "freshness_score": 88,
    "alerts": []
  },
  "eta": "1h 15m",
  "distance_remaining": 25.3
}
```

#### 5. IoT Sensor Endpoints

**GET /api/v1/iot/readings/{device_id}**
```typescript
GET /api/v1/iot/readings/ESP32_001?limit=10

Response:
{
  "device_id": "ESP32_001",
  "readings": [
    {
      "timestamp": "2026-01-16T10:30:00Z",
      "temperature": 12.5,
      "humidity": 65,
      "image_url": "https://iot.harvest.in/img/12345.jpg",
      "ai_analysis": {
        "freshness_score": 92,
        "health_status": "excellent",
        "detected_issues": [],
        "shelf_life_hours": 72
      }
    }
  ]
}
```

**POST /api/v1/iot/alert**
```typescript
// Receive IoT alerts (webhook)
POST /api/v1/iot/alert

Body:
{
  "device_id": "ESP32_001",
  "booking_id": "B789",
  "alert_type": "temperature_high",
  "temperature": 18.5,
  "threshold": 15.0,
  "message": "Temperature rising! Leafy greens will spoil in 4 hours."
}
```

#### 6. WhatsApp Integration (Backend Webhook)

**POST /whatsapp**
```typescript
// Twilio webhook (already implemented in backend)
POST /whatsapp

Form Data:
- Body: "tomatoes"
- From: "whatsapp:+919876543210"

Response: TwiML with AI-generated message
```

---

## API Service Layer

Create a centralized API service for all backend calls:

```typescript
// lib/api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_CONFIG } from '../config';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor (add auth tokens)
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor (handle errors)
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        console.error('API Error:', error);
        throw error;
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.client.get(url, config);
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.client.post(url, data, config);
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.client.put(url, data, config);
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.client.delete(url, config);
  }
}

export const apiClient = new ApiClient();
```

```typescript
// lib/api/services/market.service.ts
import { apiClient } from '../client';
import { MarketItem } from '@/data/mockData';

export const marketService = {
  async getAllPrices(): Promise<{ success: boolean; data: Record<string, any> }> {
    return apiClient.get('/api/v1/prices');
  },

  async getCropPrice(cropName: string, includeIot = true): Promise<MarketItem> {
    const response = await apiClient.get(
      `/api/v1/prices/${cropName}?include_iot=${includeIot}`
    );
    
    // Transform backend response to frontend MarketItem interface
    return {
      id: `M_${cropName}`,
      cropName: response.data.crop,
      mandiName: response.data.region || 'Maharashtra',
      mandiPrice: response.data.mandi_price,
      villagePrice: response.data.village_price,
      unit: response.data.unit,
      profitGap: response.data.profit_gap,
      trend: response.data.trend || 'up',
      spoilageRisk: response.data.spoilage_risk || 'Low',
      freshnessScore: response.data.iot_data?.freshness_score,
      temperature: response.data.iot_data?.temperature,
      humidity: response.data.iot_data?.humidity,
      shelfLifeHours: response.data.iot_data?.shelf_life_hours,
      lastImageUrl: response.data.iot_data?.last_image_url,
      aiHealthStatus: response.data.iot_data?.health_status,
      lastUpdated: new Date().toISOString(),
    };
  },

  async updatePrice(cropName: string, mandiPrice: number, villagePrice: number) {
    return apiClient.put(`/api/v1/prices/${cropName}`, {
      mandi_price: mandiPrice,
      village_price: villagePrice,
    });
  },
};
```

```typescript
// lib/api/services/driver.service.ts
import { apiClient } from '../client';
import { Driver } from '@/data/mockData';

export const driverService = {
  async getAllDrivers(filters?: { available?: boolean; route?: string }): Promise<Driver[]> {
    const params = new URLSearchParams();
    if (filters?.available !== undefined) params.set('available', String(filters.available));
    if (filters?.route) params.set('route', filters.route);

    const response = await apiClient.get(`/api/v1/drivers?${params}`);
    
    // Transform backend data to frontend Driver interface
    return response.data.map((d: any) => ({
      id: d.id,
      name: d.name,
      vehicleType: d.vehicle,
      lat: d.current_location.lat,
      lng: d.current_location.lng,
      route: d.route,
      available: d.available,
      status: d.available ? 'Available' : 'Busy',
      currentLoad: d.current_load || 'Empty',
      phone: d.phone,
      rating: d.rating,
      eta: d.eta_to_you,
    }));
  },

  async getDriverLocation(driverId: string) {
    return apiClient.get(`/api/v1/drivers/${driverId}/location`);
  },

  async trackDriver(driverId: string, interval = 10000): EventSource {
    // Use Server-Sent Events for real-time tracking
    return new EventSource(`${API_CONFIG.BASE_URL}/api/v1/drivers/${driverId}/stream`);
  },
};
```

```typescript
// lib/api/services/booking.service.ts
import { apiClient } from '../client';
import { Booking } from '@/types/backend';

export const bookingService = {
  async createBooking(data: {
    farmerId: string;
    crop: string;
    quantity: number;
    pickupLocation: string;
    pickupLat: number;
    pickupLng: number;
    preferredTime: string;
  }): Promise<Booking> {
    return apiClient.post('/api/v1/bookings', {
      farmer_id: data.farmerId,
      crop: data.crop,
      quantity: data.quantity,
      pickup_location: data.pickupLocation,
      pickup_lat: data.pickupLat,
      pickup_lng: data.pickupLng,
      preferred_time: data.preferredTime,
    });
  },

  async getBooking(bookingId: string): Promise<Booking> {
    const response = await apiClient.get(`/api/v1/bookings/${bookingId}`);
    return response.data;
  },

  async trackBooking(bookingId: string) {
    return apiClient.get(`/api/v1/bookings/${bookingId}/track`);
  },

  async confirmBooking(bookingId: string) {
    return apiClient.post(`/api/v1/bookings/${bookingId}/confirm`);
  },

  async cancelBooking(bookingId: string, reason: string) {
    return apiClient.post(`/api/v1/bookings/${bookingId}/cancel`, { reason });
  },
};
```

```typescript
// lib/api/services/iot.service.ts
import { apiClient } from '../client';

export const iotService = {
  async getDeviceReadings(deviceId: string, limit = 10) {
    return apiClient.get(`/api/v1/iot/readings/${deviceId}?limit=${limit}`);
  },

  async getLatestReading(deviceId: string) {
    const response = await this.getDeviceReadings(deviceId, 1);
    return response.readings[0];
  },

  async subscribeToAlerts(callback: (alert: any) => void): WebSocket {
    const ws = new WebSocket(`${API_CONFIG.WEBSOCKET_URL}/iot/alerts`);
    
    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      callback(alert);
    };

    return ws;
  },
};
```

---

## Frontend Modifications Required

### 1. Update Type Definitions

**Create `/types/backend.ts`** for backend-specific types:
```typescript
// types/backend.ts
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

export interface BackendMarketData {
  mandi: number;
  village: number;
  unit: string;
  profit_margin?: number;
  trend?: string;
  spoilage_risk?: string;
  iot_data?: {
    freshness_score: number;
    temperature: number;
    humidity: number;
    shelf_life_hours: number;
    health_status: string;
    last_image_url: string;
  };
}

export interface BackendDriver {
  id: string;
  name: string;
  vehicle: string;
  route: string;
  available: boolean;
  current_location: { lat: number; lng: number };
  phone: string;
  rating?: number;
  eta_to_you?: string;
}

export interface Booking {
  // ... (full Booking interface from section above)
}
```

### 2. Add Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_BACKEND_ENV=development

# Production
# NEXT_PUBLIC_API_URL=https://api.neuralroots.com
# NEXT_PUBLIC_WS_URL=wss://api.neuralroots.com/ws
# NEXT_PUBLIC_BACKEND_ENV=production
```

### 3. Create Feature Flags

```typescript
// lib/featureFlags.ts
export const FEATURE_FLAGS = {
  USE_BACKEND_API: process.env.NEXT_PUBLIC_BACKEND_ENV === 'production',
  ENABLE_IOT_MONITORING: true,
  ENABLE_REAL_TIME_TRACKING: true,
  ENABLE_WHATSAPP_INTEGRATION: false, // Enable when backend is ready
  USE_MOCK_DATA: process.env.NEXT_PUBLIC_BACKEND_ENV !== 'production',
};
```

### 4. Create Data Adapter Layer

```typescript
// lib/adapters/dataAdapter.ts
import { FEATURE_FLAGS } from '../featureFlags';
import { marketService } from '../api/services/market.service';
import { driverService } from '../api/services/driver.service';
import { marketItemsData, driversData } from '@/data/mockData';
import type { MarketItem, Driver } from '@/data/mockData';

export const dataAdapter = {
  async getMarketItems(): Promise<MarketItem[]> {
    if (FEATURE_FLAGS.USE_BACKEND_API) {
      const response = await marketService.getAllPrices();
      // Transform backend data to MarketItem[]
      return Object.entries(response.data).map(([cropName, data]: [string, any]) => ({
        id: `M_${cropName}`,
        cropName,
        mandiName: data.region || 'Maharashtra',
        mandiPrice: data.mandi,
        villagePrice: data.village,
        unit: data.unit,
        profitGap: data.profit_margin,
        trend: data.trend || 'up',
        spoilageRisk: data.spoilage_risk || 'Low',
        lastUpdated: new Date().toISOString(),
      }));
    }
    return marketItemsData; // Fallback to mock data
  },

  async getDrivers(): Promise<Driver[]> {
    if (FEATURE_FLAGS.USE_BACKEND_API) {
      return driverService.getAllDrivers();
    }
    return driversData; // Fallback to mock data
  },

  // ... similar adapters for farmers, bookings, etc.
};
```

### 5. Update Main App Component

```typescript
// app/page.tsx (modified)
import { useEffect, useState } from 'react';
import { dataAdapter } from '@/lib/adapters/dataAdapter';
import { FEATURE_FLAGS } from '@/lib/featureFlags';

export default function Home() {
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [marketItems, setMarketItems] = useState<MarketItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [farmersData, driversData, marketData] = await Promise.all([
          dataAdapter.getFarmers(),
          dataAdapter.getDrivers(),
          dataAdapter.getMarketItems(),
        ]);

        setFarmers(farmersData);
        setDrivers(driversData);
        setMarketItems(marketData);
      } catch (error) {
        console.error('Failed to load data:', error);
        // Fallback to mock data
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) return <LoadingScreen />;

  return (
    <div>
      {/* Existing UI */}
    </div>
  );
}
```

---

## Migration Strategy

### Phase 1: Preparation (Week 1)
- [ ] Update all TypeScript interfaces with backend-compatible fields
- [ ] Create API service layer (`lib/api/`)
- [ ] Add environment variables and feature flags
- [ ] Create data adapter layer for seamless switching

### Phase 2: Parallel Testing (Week 2)
- [ ] Deploy backend on Railway/Render
- [ ] Configure Twilio webhook
- [ ] Test individual API endpoints with Postman
- [ ] Implement backend calls alongside mock data
- [ ] Use feature flag to switch between mock/real data

### Phase 3: IoT Integration (Week 3)
- [ ] Connect ESP32 devices to backend
- [ ] Implement WebSocket for real-time sensor data
- [ ] Add IoT monitoring UI components
- [ ] Test freshness alerts and shelf-life predictions

### Phase 4: Full Integration (Week 4)
- [ ] Enable `USE_BACKEND_API` flag in production
- [ ] Deploy frontend to Vercel
- [ ] Set up Supabase database
- [ ] Migrate from mock data to live database
- [ ] Enable WhatsApp integration

### Phase 5: Urban Agriculture Features (Week 5-6)
- [ ] Add terrace/vertical farmer registration
- [ ] Implement micro-delivery logistics
- [ ] Create quality certification UI with IoT data
- [ ] Add hyper-local marketplace

---

## Testing Checklist

### Backend API Tests
- [ ] `/api/v1/prices` returns correct format
- [ ] `/api/v1/drivers` filters work correctly
- [ ] `/api/v1/bookings` creates orders successfully
- [ ] WhatsApp webhook receives and processes messages
- [ ] IoT sensor data flows correctly

### Frontend Integration Tests
- [ ] Mock data ↔ Backend data switching works
- [ ] All UI components render with backend data
- [ ] Real-time updates display correctly
- [ ] Error handling works (offline mode)
- [ ] WebSocket connections stable

### End-to-End Tests
- [ ] Farmer creates booking → Driver assigned → IoT monitors → Delivery confirmed
- [ ] Price updates from backend reflect in UI instantly
- [ ] WhatsApp conversation → Booking creation → Payment link
- [ ] IoT alert → Frontend notification → User action

---

## Support & Documentation

### Helpful Commands

```bash
# Start backend (from backend repo)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (from frontend repo)
npm run dev

# Test API connection
curl http://localhost:8000/api/v1/prices

# Monitor WebSocket
wscat -c ws://localhost:8000/ws
```

### Environment Setup

1. **Backend**: Set up `.env` with API keys
2. **Frontend**: Set up `.env.local` with API URL
3. **Database**: Configure Supabase connection
4. **IoT**: Register ESP32 devices in backend

---

## Quick Integration Example

```typescript
// Example: Replace mock price fetch with backend call

// BEFORE (Mock Data)
const [marketItems, setMarketItems] = useState(marketItemsData);

// AFTER (Backend Connected)
const [marketItems, setMarketItems] = useState<MarketItem[]>([]);

useEffect(() => {
  async function fetchPrices() {
    try {
      const prices = await dataAdapter.getMarketItems();
      setMarketItems(prices);
    } catch (error) {
      console.error('Failed to fetch prices:', error);
      setMarketItems(marketItemsData); // Fallback
    }
  }

  fetchPrices();
  
  // Refresh every 30 seconds
  const interval = setInterval(fetchPrices, 30000);
  return () => clearInterval(interval);
}, []);
```

---

**Last Updated:** January 16, 2026  
**Status:** Ready for Implementation  
**Next Action:** Deploy backend → Test endpoints → Enable feature flags
