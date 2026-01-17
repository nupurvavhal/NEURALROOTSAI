/**
 * Backend-Compatible Type Definitions
 * Aligns with FastAPI backend structure + IoT sensor integration
 */

// ============================================================================
// BACKEND API RESPONSE TYPES
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
  };
}

// ============================================================================
// IOT SENSOR DATA TYPES
// ============================================================================

export interface IoTSensorReading {
  id: string;
  deviceId: string;
  entityType: 'farmer' | 'booking' | 'storage';
  entityId: string;
  
  // Environmental sensors (DHT11/DHT22)
  temperature: number;        // Celsius
  humidity: number;           // Percentage 0-100
  
  // Visual AI (ESP32-CAM)
  imageUrl?: string;
  imageTimestamp: string;
  
  // AI-powered analysis
  aiAnalysis: {
    freshnessScore: number;   // 0-100
    healthStatus: 'excellent' | 'good' | 'warning' | 'critical';
    detectedIssues: string[]; // e.g., ['browning', 'moisture_spots']
    shelfLifeHours: number;   // Predicted remaining shelf life
    confidence: number;       // AI confidence 0-1
    recommendations?: string[];
  };
  
  // Alert system
  alertGenerated: boolean;
  alertType?: 'temperature_high' | 'temperature_low' | 'humidity_high' | 
              'humidity_low' | 'spoilage_detected' | 'quality_degrading';
  alertMessage?: string;
  alertSeverity?: 'info' | 'warning' | 'critical';
  
  // Metadata
  timestamp: string;
  location?: {
    lat: number;
    lng: number;
  };
  batteryLevel?: number;      // 0-100
  signalStrength?: number;    // 0-100
}

export interface IoTDevice {
  id: string;
  deviceType: 'ESP32-CAM' | 'DHT22' | 'Combined';
  status: 'online' | 'offline' | 'error';
  lastSeen: string;
  firmwareVersion: string;
  batteryLevel: number;
  location?: {
    lat: number;
    lng: number;
  };
  assignedTo?: {
    entityType: 'farmer' | 'booking';
    entityId: string;
  };
}

// ============================================================================
// MARKET PRICE TYPES (Backend Compatible)
// ============================================================================

export interface BackendMarketData {
  mandi: number;              // Price at market
  village: number;            // Local village price
  unit: string;               // 'kg', 'quintal', etc.
  profit_margin?: number;     // Percentage profit
  trend?: 'up' | 'down';
  spoilage_risk?: 'Low' | 'Medium' | 'Critical';
  region?: string;
  
  // IoT integration
  iot_data?: {
    freshness_score: number;
    temperature: number;
    humidity: number;
    shelf_life_hours: number;
    health_status: 'excellent' | 'good' | 'warning' | 'critical';
    last_image_url: string;
  };
}

export interface EnhancedMarketItem {
  id: string;
  cropName: string;
  mandiName: string;
  
  // Price comparison (Backend: MARKET_DATA)
  mandiPrice: number;         // Backend: mandi
  villagePrice: number;       // Backend: village
  unit: string;               // Backend: unit
  profitGap: number;          // Calculated: ((mandi - village) / village) * 100
  
  // Market intelligence
  trend: 'up' | 'down';
  spoilageRisk: 'Low' | 'Medium' | 'Critical';
  
  // IoT freshness monitoring (NEW)
  freshnessScore?: number;    // 0-100 from IoT sensors
  temperature?: number;        // Current temp in Celsius
  humidity?: number;           // Current humidity percentage
  shelfLifeHours?: number;     // AI-predicted remaining time
  lastImageUrl?: string;       // ESP32-CAM snapshot
  aiHealthStatus?: 'excellent' | 'good' | 'warning' | 'critical';
  
  // Metadata
  lastUpdated: string;
  region?: string;
  demandLevel?: 'low' | 'medium' | 'high';
  seasonalFactor?: number;     // Multiplier 0.5-2.0
}

// ============================================================================
// DRIVER/LOGISTICS TYPES (Backend Compatible)
// ============================================================================

export interface BackendDriver {
  id: string;
  name: string;
  vehicle: string;            // Backend: vehicle
  route: string;              // Backend: route (e.g., "Village-to-City")
  available: boolean;         // Backend: available
  current_location: {
    lat: number;
    lng: number;
  };
  phone: string;
  rating?: number;
  eta_to_you?: string;
  current_load?: string;
}

export interface EnhancedDriver {
  id: string;
  name: string;
  
  // Vehicle details
  vehicleType: string;        // Maps to backend: vehicle
  vehicleNumber?: string;
  vehicleCapacity?: number;   // kg
  
  // Location tracking
  lat: number;
  lng: number;
  route: string;              // Backend: route
  
  // Availability
  available: boolean;         // Backend: available
  status: 'Available' | 'Busy' | 'Offline';
  currentLoad: string;
  loadPercentage?: number;    // 0-100
  
  // Contact
  phone: string;
  whatsappNumber?: string;
  
  // Real-time GPS tracking
  lastSeen?: string;
  currentSpeed?: number;      // km/h
  heading?: number;           // Degrees 0-360
  eta?: string;               // "2h 20m"
  distanceToPickup?: number;  // km
  
  // Performance metrics
  rating?: number;            // 0-5
  completedTrips?: number;
  onTimePercentage?: number;  // 0-100
  totalDistanceTraveled?: number; // km
  
  // Current assignment
  currentBookingId?: string;
  estimatedArrival?: string;
}

export interface RouteDetails {
  routeName: string;
  distance: string;           // Backend: distance
  eta: string;                // Backend: eta
  dropOff: string;            // Backend: drop_off
  cost: string;               // Backend: cost
  tollCharges?: number;
  fuelCost?: number;
}

// ============================================================================
// FARMER TYPES (Backend Compatible)
// ============================================================================

export interface EnhancedFarmer {
  id: string;                 // Backend: UUID
  name: string;
  village: string;
  photoUrl: string;
  
  // Contact info
  phone: string;              // Backend: phone (primary identifier)
  whatsappNumber?: string;
  email?: string;
  language?: 'en' | 'hi' | 'mr'; // English/Hindi/Marathi
  
  // Farmer classification (NEW for urban agriculture)
  farmerType: 'rural' | 'urban_terrace' | 'urban_vertical' | 'community_garden';
  landSize?: string;          // "5 acres" or "terrace 500 sqft"
  specialization?: string[];  // ['organic', 'leafy_greens', 'tomatoes']
  
  // Performance metrics
  rating: number;             // 0-5
  totalEarnings: number;      // In INR
  status: 'Connected' | 'Pending' | 'Verified' | 'Inactive';
  verificationLevel?: 'basic' | 'kyc_verified' | 'iot_certified';
  
  // Transaction history
  history: Transaction[];
  totalTransactions?: number;
  averageTransactionValue?: number;
  
  // IoT integration (NEW)
  iotDeviceId?: string;       // ESP32 device ID
  hasIoTKit?: boolean;        // Has "Freshness Guard" device
  iotStatus?: 'active' | 'inactive' | 'error';
  currentConditions?: {
    temperature: number;
    humidity: number;
    freshnessScore: number;
  };
  
  // Banking/Payment
  bankAccount?: {
    accountNumber: string;
    ifsc: string;
    upiId?: string;
  };
  
  // Metadata
  createdAt?: string;
  lastActive?: string;
  preferredMarkets?: string[]; // ['Pune APMC', 'Vashi Market']
}

export interface Transaction {
  id?: string;
  date: string;
  crop: string;
  amount: string;             // e.g., "150kg"
  quantity?: number;          // Parsed number
  unit?: string;              // Parsed unit
  soldTo: string;
  revenue: number;            // In INR
  
  // Backend tracking (NEW)
  bookingId?: string;         // Links to bookings table
  driverId?: string;
  driverName?: string;
  transportCost?: number;
  grossProfit?: number;       // revenue - transportCost
  profitMargin?: number;      // Percentage
  paymentMethod?: 'cash' | 'upi' | 'bank_transfer';
  paymentStatus?: 'pending' | 'completed' | 'failed';
}

// ============================================================================
// BOOKING/ORDER TYPES (NEW - Core Backend Integration)
// ============================================================================

export interface Booking {
  id: string;
  
  // Participants
  farmerId: string;
  farmerName: string;
  farmerPhone: string;
  driverId?: string;
  driverName?: string;
  driverPhone?: string;
  
  // Crop details
  crop: string;
  quantity: number;           // in kg
  unit: string;
  cropImageUrl?: string;
  
  // Pricing breakdown
  villagePrice: number;       // Local price per unit
  mandiPrice: number;         // Market price per unit
  villageTotalValue: number;  // villagePrice * quantity
  mandiTotalValue: number;    // mandiPrice * quantity
  transportCost: number;
  netProfit: number;          // (mandiPrice - villagePrice) * quantity - transportCost
  profitMargin: number;       // Percentage
  commission?: number;        // Platform commission
  
  // Locations
  pickupLocation: string;
  pickupLat: number;
  pickupLng: number;
  pickupAddress?: string;
  dropoffLocation: string;
  dropoffLat: number;
  dropoffLng: number;
  dropoffAddress?: string;
  
  // Route information
  distance: number;           // km
  estimatedDuration: number;  // minutes
  routePolyline?: string;     // Encoded polyline for map
  
  // Timing
  pickupTime: string;         // ISO timestamp
  estimatedDelivery: string;
  actualPickupTime?: string;
  actualDeliveryTime?: string;
  
  // Status workflow
  status: 'pending' | 'confirmed' | 'driver_assigned' | 'driver_enroute' |
          'picked_up' | 'in_transit' | 'delivered' | 'completed' | 
          'cancelled' | 'failed';
  statusHistory?: Array<{
    status: string;
    timestamp: string;
    note?: string;
  }>;
  
  // Payment
  paymentStatus: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
  paymentMethod?: 'upi' | 'cash' | 'bank_transfer' | 'wallet';
  paymentLink?: string;       // Razorpay/UPI payment link
  paymentTransactionId?: string;
  paymentCompletedAt?: string;
  
  // IoT monitoring during transit (NEW)
  iotMonitoring: {
    enabled: boolean;
    deviceId?: string;
    currentTemp?: number;
    currentHumidity?: number;
    freshnessScore?: number;
    lastReading?: string;
    alerts: Array<{
      id: string;
      time: string;
      type: 'temperature' | 'humidity' | 'spoilage' | 'delay' | 'route_deviation';
      message: string;
      severity: 'info' | 'warning' | 'critical';
      resolved: boolean;
    }>;
  };
  
  // Real-time tracking
  trackingLink?: string;
  trackingEnabled: boolean;
  currentDriverLocation?: {
    lat: number;
    lng: number;
    speed?: number;
    heading?: number;
    timestamp: string;
  };
  
  // AI-generated content (LangGraph)
  aiNegotiationText?: string; // Initial offer message
  aiRecommendations?: string[];
  aiPredictedSuccess?: number; // 0-1 probability
  
  // Metadata
  createdAt: string;
  updatedAt: string;
  cancelledAt?: string;
  cancellationReason?: string;
  notes?: string;
  tags?: string[];            // ['urgent', 'organic', 'premium']
}

export interface BookingQuote {
  crop: string;
  quantity: number;
  pickupLocation: string;
  
  // Price analysis
  villageTotal: number;
  mandiTotal: number;
  transportCost: number;
  netProfit: number;
  profitPercentage: number;
  
  // Available driver
  driver?: {
    id: string;
    name: string;
    vehicle: string;
    eta: string;
    rating: number;
  };
  
  // AI-generated message
  aiMessage: string;
  
  // Recommendations
  bestTimeToSell?: string;
  alternativeCrops?: string[];
  marketDemandLevel: 'low' | 'medium' | 'high';
}

// ============================================================================
// WHOLESALER TYPES
// ============================================================================

export interface WholesalerPurchase {
  date: string;
  crop: string;
  quantity: string;
  boughtFrom: string;
  cost: number;
  soldTo?: string;
  revenue?: number;
  status: 'In Stock' | 'Sold' | 'In Transit';
  
  // Backend integration (NEW)
  bookingId?: string;
  profitMargin?: number;
  freshnessAtPurchase?: number;
  freshnessNow?: number;
}

export interface Wholesaler {
  id: string;
  name: string;
  businessName: string;
  location: string;
  photoUrl: string;
  rating: number;
  totalVolume: number;        // Total volume traded (in INR)
  activeOrders: number;
  creditLimit: number;
  status: 'Active' | 'Inactive' | 'Pending Verification';
  specialization: string[];
  purchases: WholesalerPurchase[];
  phone: string;
  gstNumber: string;
  
  // Backend integration (NEW)
  email?: string;
  bankDetails?: {
    accountNumber: string;
    ifsc: string;
  };
  preferredPaymentMethod?: 'upi' | 'bank_transfer' | 'cash';
  creditBalance?: number;
  outstandingPayments?: number;
}

// ============================================================================
// WEBSOCKET/REAL-TIME EVENT TYPES
// ============================================================================

export interface WebSocketMessage {
  type: 'price_update' | 'driver_location' | 'iot_alert' | 'booking_update' | 
        'notification' | 'system_alert';
  data: any;
  timestamp: string;
}

export interface PriceUpdateEvent {
  type: 'price_update';
  data: {
    crop: string;
    oldPrice: number;
    newPrice: number;
    priceType: 'mandi' | 'village';
    percentageChange: number;
  };
}

export interface DriverLocationEvent {
  type: 'driver_location';
  data: {
    driverId: string;
    lat: number;
    lng: number;
    speed: number;
    heading: number;
    bookingId?: string;
  };
}

export interface IoTAlertEvent {
  type: 'iot_alert';
  data: {
    deviceId: string;
    bookingId?: string;
    farmerId?: string;
    alertType: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
    currentConditions: {
      temperature: number;
      humidity: number;
      freshnessScore: number;
    };
    recommendedAction?: string;
  };
}

export interface BookingUpdateEvent {
  type: 'booking_update';
  data: {
    bookingId: string;
    oldStatus: string;
    newStatus: string;
    message: string;
  };
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface TimeRange {
  start: string;
  end: string;
}

export interface PriceHistory {
  date: string;
  price: number;
  volume?: number;
}

export interface AnalyticsData {
  totalRevenue: number;
  totalTrips: number;
  avgProfitMargin: number;
  topCrops: Array<{
    crop: string;
    volume: number;
    revenue: number;
  }>;
  timeSeriesData: Array<{
    date: string;
    revenue: number;
    trips: number;
  }>;
}

// ============================================================================
// WHATSAPP INTEGRATION TYPES
// ============================================================================

export interface WhatsAppMessage {
  from: string;               // Phone number with country code
  body: string;               // Message text
  timestamp: string;
  messageId: string;
}

export interface WhatsAppConversation {
  id: string;
  farmerId: string;
  messages: Array<{
    direction: 'incoming' | 'outgoing';
    text: string;
    timestamp: string;
    status?: 'sent' | 'delivered' | 'read' | 'failed';
  }>;
  bookingId?: string;
  status: 'active' | 'completed';
  createdAt: string;
}

// ============================================================================
// EXPORT ALL TYPES
// ============================================================================

export type FarmerType = 'rural' | 'urban_terrace' | 'urban_vertical' | 'community_garden';
export type BookingStatus = Booking['status'];
export type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
export type AlertSeverity = 'info' | 'warning' | 'critical';
export type HealthStatus = 'excellent' | 'good' | 'warning' | 'critical';
