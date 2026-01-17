# Neural Roots🌱 - System Architecture

## Overview
Neural Roots is an AI-powered agricultural logistics management platform built with Next.js 15, providing real-time monitoring and management of farmers, drivers, market prices, and transportation logistics with intelligent analytics.

---

## Technology Stack

### Core Framework
- **Next.js 15.5.9** - App Router with React Server Components
- **React 18.3.1** - Client-side interactivity
- **TypeScript 5.7.2** - Type-safe development

### Styling & UI
- **Tailwind CSS 3.4.17** - Utility-first styling
- **Shadcn UI** - Pre-built accessible components
- **Dark Theme** - Zinc-950 background with emerald-500 accents

### Mapping
- **Leaflet 1.9.4** - Interactive map rendering
- **Manual Leaflet Integration** - Direct DOM manipulation for stability
- **CartoDB Dark Matter** - Dark-themed map tiles

### State Management
- **React Hooks** - useState, useEffect, useRef
- **Custom useLocalStorage Hook** - Persistent state across sessions
- **Prop Drilling** - Centralized state in page.tsx

---

## Application Architecture

### Directory Structure
```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with Leaflet CSS
│   ├── page.tsx            # Main application router
│   └── globals.css         # Global styles with Tailwind
├── components/
│   ├── CommandCenter.tsx   # Dashboard with live stats
│   ├── FleetModule.tsx     # Driver list with map integration
│   ├── LeafletMap.tsx      # Raw Leaflet map implementation
│   ├── FarmersModule.tsx   # Farmer network with drill-down
│   ├── WholesalersModule.tsx # Wholesaler/trader management
│   ├── MarketTerminal.tsx  # Editable market prices
│   ├── TransportAnalytics.tsx  # Delivery tracking & fleet overview
│   ├── AnalyticsDashboard.tsx  # Revenue & performance analytics
│   ├── Sidebar.tsx         # Fixed navigation
│   └── SimulationOverlay.tsx   # Live notification system
├── data/
│   └── mockData.ts         # Realistic mock data with types
├── hooks/
│   └── use-local-storage.ts    # Persistent storage hook
└── components/ui/          # Shadcn UI components

```

---

## Component Architecture

### 1. Page-Level State Management
**Location:** `app/page.tsx`

```typescript
- activeTab: 'command' | 'fleet' | 'transport' | 'farmers' | 'wholesalers' | 'market' | 'analytics'
- farmers: Farmer[] (10 farmers with transaction history)
- wholesalers: Wholesaler[] (11 wholesalers with purchase/sales history)
- drivers: Driver[] (8 drivers with real-time positions)
- marketItems: MarketItem[] (12 crops with prices and spoilage risk)
```

**State Flow:**
```
page.tsx (central state)
    ↓
Sidebar (tab selection)
    ↓
Conditional Rendering (7 modules)
    ↓
SimulationOverlay (periodic updates)
```

### 2. Module Components

#### CommandCenter
- **Purpose:** Executive dashboard with KPI monitoring
- **Features:**
  - 4 animated stat cards (Revenue, Farmers, Drivers, Critical Items)
  - Pulsing live indicators (2-second intervals)
  - Recent activity feed (7 activities)
  - Top 5 performers with male farmer icons
- **State:** Read-only, receives props from parent

#### FleetModule
- **Purpose:** Real-time driver tracking
- **Features:**
  - Left panel: Driver list (30% width)
  - Right panel: Interactive Leaflet map (70% width)
  - Click driver → map flies to location
  - 2-second position simulation updates
- **State:** selectedDriver (local), drivers (prop)
- **Map Integration:** Dynamic import with SSR disabled

#### LeafletMap
- **Purpose:** Pure Leaflet implementation (no react-leaflet)
- **Implementation:**
  - useRef to maintain single map instance
  - Manual marker management
  - FlyTo animation on driver selection
  - Custom truck icons (green=Available, red=Busy)
- **Why Not react-leaflet?** Avoids "Map container already initialized" errors

#### FarmersModule
- **Purpose:** Farmer network management
- **Features:**
  - Table with 10 farmers
  - Click row → Sheet opens with drill-down
  - Performance stats (Revenue, Crops Sold, Rating, Status)
  - Transaction history (3-4 per farmer)
  - Professional male icons (bottts-neutral style)
  - "Assign Logistics" button with toast notifications
- **State:** selectedFarmer, isSheetOpen

#### WholesalersModule
- **Purpose:** Wholesaler/trader management (Middleman functionality)
- **Features:**
  - Table with 11 wholesalers
  - Business profiles with GST verification
  - Click row → Sheet opens with complete business details
  - Purchase history tracking (bought from farmers)
  - Sales records (sold to markets/retailers)
  - Credit limit monitoring (₹5L to ₹50L)
  - Active order counts
  - Total volume traded (50-500 tons)
  - Specialization badges (vegetables, fruits, grains)
  - Profit margin calculations
  - Stock status indicators (In Stock/Sold/In Transit)
  - Professional male business icons
- **State:** selectedWholesaler, isSheetOpen

#### MarketTerminal
- **Purpose:** Real-time market price management
- **Features:**
  - 12 market items with editable prices
  - Click price → inline edit with input field
  - Auto-calculate trend (up/down arrows)
  - Spoilage risk badges (Low/Medium/Critical)
  - Broadcast notifications on price update
- **State:** editingId, editValue

#### TransportAnalytics
- **Purpose:** Logistics operations monitoring
- **Features:**
  - 4 metric cards (Active: 12, Completed: 28, Avg Time: 45min, On-Time: 94%)
  - 5 recent deliveries with progress bars
  - Fleet overview by vehicle type (Tata Ace: 3, Mahindra: 2, etc.)
  - Performance metrics with icons
- **State:** Read-only, static data

#### AnalyticsDashboard
- **Purpose:** Business intelligence & reporting
- **Features:**
  - Revenue overview (₹26.4L total, 23.5% growth)
  - Top 5 crops with growth indicators
  - Regional performance (6 regions across Maharashtra)
  - 6-month revenue trend chart
- **State:** Read-only, static data

#### Sidebar
- **Purpose:** Navigation
- **Features:**
  - Fixed 250px width
  - 6 navigation items with icons
  - Active state highlighting (emerald-500)
  - Professional branding ("Neural Roots🌱")
- **State:** activeTab (controlled by parent)

#### SimulationOverlay
- **Purpose:** Live notification system
- **Features:**
  - 15-second interval updates
  - Toast notifications for random events
  - Status badge (System Online)
- **State:** isRunning (toggle simulation)

---

## Data Architecture

### Type Definitions (mockData.ts)

```typescript
interface Transaction {
  date: string;
  crop: string;
  amount: string;
  soldTo: string;
  revenue: number;
}

interface Farmer {
  id: string;
  name: string;
  village: string;
  photoUrl: string;
  rating: number;
  totalEarnings: number;
  status: 'Connected' | 'Pending';
  history: Transaction[];
}

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

interface MarketItem {
  id: string;
  cropName: string;
  mandiName: string;
  price: number;
  trend: 'up' | 'down';
  spoilageRisk: 'Low' | 'Medium' | 'Critical';
}
```

### Mock Data Scale
- **10 Farmers** - Each with 3-4 transaction history entries
- **8 Drivers** - Distributed across Maharashtra (18.5°N-19.5°N, 72.5°E-75°E)
- **12 Market Items** - Covering major crops (Tomatoes, Onions, Potatoes, etc.)

---

## Design Patterns

### 1. Component Composition
- **Container/Presentational Pattern:** page.tsx manages state, components render
- **Prop Drilling:** Deliberate choice for simplicity (no Redux/Context needed)
- **Controlled Components:** All form inputs managed by React state

### 2. Performance Optimizations
- **Dynamic Imports:** Leaflet map loaded client-side only
- **useRef for Map Instance:** Prevents re-initialization
- **Memoization Ready:** Components structured for React.memo if needed

### 3. Error Prevention
- **Type Safety:** Full TypeScript coverage
- **Null Checks:** Optional chaining throughout (selectedDriver?.lat)
- **Controlled Intervals:** Cleanup functions in all useEffect hooks

### 4. State Persistence
- **useLocalStorage Hook:** Market prices and driver positions persist
- **Session Recovery:** Users can refresh without losing changes

---

## Styling Architecture

### Theme System
```css
Background: zinc-950 (#09090b)
Primary: emerald-500 (#10b981)
Secondary: blue-500, purple-500, red-500
Text: white, zinc-400, zinc-500
Borders: zinc-800
```

### Responsive Design
- **Grid Layouts:** Auto-adjust from 1 to 4 columns
- **Flexible Tables:** Horizontal scroll on mobile
- **Map Split:** 30/70 driver list/map ratio

### Glassmorphism Effects
```css
bg-zinc-800/50
bg-emerald-500/20
border-emerald-500/30
```

---

## Security Considerations

### Current Implementation (Development)
- Mock data only (no real farmer/driver PII)
- Client-side state (no authentication)
- Public API endpoints (no rate limiting)

### Production Requirements
1. **Authentication:** JWT/OAuth for admin access
2. **Authorization:** Role-based access control (RBAC)
3. **Data Encryption:** HTTPS + encrypted database fields
4. **API Security:** Rate limiting, CORS policies
5. **Input Validation:** Zod/Yup schema validation
6. **Audit Logs:** Track all price changes and logistics assignments

---

## Scalability Considerations

### Current Limitations
- In-memory state (resets on page refresh except localStorage items)
- No backend API
- Static mock data

### Production Migration Path
1. **Backend:** Node.js/Express or Next.js API routes
2. **Database:** PostgreSQL with PostGIS for geospatial data
3. **Real-time:** WebSockets for live driver positions
4. **Caching:** Redis for market prices and session data
5. **CDN:** Cloudflare/AWS CloudFront for static assets
6. **Monitoring:** Sentry for error tracking, DataDog for metrics

---

## Browser Compatibility

### Tested On
- Chrome 120+ ✅
- Safari 17+ ✅
- Firefox 121+ ✅
- Edge 120+ ✅

### Known Issues
- IE11: Not supported (uses ES6+ features)
- Mobile Safari: Map touch gestures may require tuning

---

## Development Workflow

### Local Development
```bash
npm run dev     # Start dev server on :3000
npm run build   # Production build
npm run start   # Start production server
```

### Environment Variables
```env
# None required currently
# Future: DATABASE_URL, NEXT_PUBLIC_MAPBOX_TOKEN, etc.
```

---

## Future Enhancements

### Phase 2 Features
1. **Weather Integration:** Real-time weather alerts for deliveries
2. **Route Optimization:** Dijkstra/A* algorithms for driver routing
3. **Predictive Analytics:** ML models for price forecasting
4. **Mobile App:** React Native companion app for farmers
5. **IoT Integration:** Sensor data for cold chain monitoring
6. **Multi-language:** i18n for regional language support

### Technical Debt
- [ ] Add unit tests (Jest + React Testing Library)
- [ ] Add E2E tests (Playwright)
- [ ] Implement error boundaries
- [ ] Add loading skeletons
- [ ] Optimize bundle size (currently ~1.2MB)
- [ ] Add service worker for offline support

---

## Contributing Guidelines

### Code Style
- TypeScript strict mode enabled
- Prettier for formatting (2-space indents)
- ESLint with Next.js recommended rules

### Component Creation
1. Use functional components with hooks
2. Export default at bottom of file
3. PropTypes via TypeScript interfaces
4. Colocate styles with Tailwind classes

### Git Workflow
```bash
main (production)
  ↓
develop (staging)
  ↓
feature/* (individual features)
```

---

## License
MIT License - See LICENSE file for details

## Contact
For questions or support, contact the development team.

---

**Last Updated:** January 14, 2026  
**Version:** 1.0.0  
**Architecture Revision:** 3
