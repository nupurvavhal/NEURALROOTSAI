# NEURAL ROOTS 🌱 - AI-Powered Agricultural Logistics Platform

A comprehensive dark-themed Next.js application for managing agricultural logistics with real-time tracking, farmer networks, and market terminals.

**✨ NEW: Backend Integration Ready!**
- Connect FastAPI + LangGraph AI backend
- IoT sensor integration (ESP32-CAM + DHT22)
- Real-time WhatsApp conversations with farmers
- Urban agriculture support (terrace/vertical farming)
- **Setup time: 30 minutes** | See [BACKEND_CONNECTION_QUICKSTART.md](BACKEND_CONNECTION_QUICKSTART.md)

---

## 📚 Documentation Hub

### Quick Start
- **[QUICKSTART.md](QUICKSTART.md)** - Get the dashboard running in 5 minutes
- **[BACKEND_CONNECTION_QUICKSTART.md](BACKEND_CONNECTION_QUICKSTART.md)** ⭐ NEW - Connect backend in 30 minutes

### Integration Guides
- **[BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md)** - Complete technical integration guide
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - Overview of frontend-backend flow
- **[ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)** - Visual system architecture

### Reference
- **[MOCK_DATA_DOCUMENTATION.md](MOCK_DATA_DOCUMENTATION.md)** - All mock data + backend mapping
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Detailed component implementation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and data flow

### Code Reference
- **[types/backend.ts](types/backend.ts)** - Backend-compatible TypeScript interfaces
- **[lib/config.ts](lib/config.ts)** - API configuration and feature flags

---

## Features

### 🎯 Command Center
- Real-time dashboard with key metrics
- Revenue tracking across all farmers
- Active farmer and driver status
- Critical item alerts
- Recent activity feed
- Top performing farmers leaderboard

### 🗺️ Live Fleet Tracking
- Interactive OpenStreetMap with dark theme
- Real-time driver location tracking
- Driver status indicators (Available/Busy)
- Click-to-fly map navigation
- Live position simulation (updates every 2 seconds)
- Custom truck icons with status colors
- Driver details in popups

### 👨‍🌾 Farmer Network
- Comprehensive farmer database
- Interactive table with sortable columns
- Detailed farmer profiles in side drawer
- Transaction history tracking
- Performance statistics
- One-click logistics assignment
- Rating system

### 🏢 Wholesaler Network
- Complete wholesaler/trader database
- Business profiles with GST verification
- Purchase and sales history tracking
- Credit limit monitoring
- Active order management
- Specialization tracking (vegetables, fruits, grains)
- Profit margin analytics
- Stock status indicators (In Stock/Sold/In Transit)

### 📈 Market Terminal
- Live market price tracking
- Interactive price editing (click to edit)
- Real-time price broadcasting
- Spoilage risk indicators
- Trending price indicators
- Critical item highlighting with pulsing borders
- 12 different crops with mandi prices

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS with custom dark theme
- **UI Components**: Shadcn UI
- **Icons**: Lucide React
- **Maps**: React-Leaflet with OpenStreetMap
- **TypeScript**: Full type safety
- **State Management**: React Hooks + localStorage persistence

## Color Scheme

- Background: Zinc-950 (#09090b)
- Cards: Zinc-900 (#18181b)
- Primary Accent: Emerald-500 (#10b981)
- Borders: Zinc-800 (#27272a)
- Text: White/Zinc shades

## Getting Started

### Installation

\`\`\`bash
npm install
\`\`\`

### Development

\`\`\`bash
npm run dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

\`\`\`bash
npm run build
npm start
\`\`\`

## Project Structure

\`\`\`
frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main application page
│   └── globals.css         # Global styles + dark theme
├── components/
│   ├── Sidebar.tsx         # Navigation sidebar
│   ├── Header.tsx          # Glassmorphism header
│   ├── CommandCenter.tsx   # Dashboard view
│   ├── FleetModule.tsx     # Map & driver tracking
│   ├── FarmersModule.tsx   # Farmer management
│   ├── WholesalersModule.tsx # Wholesaler management
│   ├── MarketTerminal.tsx  # Market prices
│   ├── SimulationOverlay.tsx # Background notifications
│   └── ui/                 # Shadcn UI components
├── data/
│   └── mockData.ts         # Rich mock data
├── hooks/
│   ├── use-toast.ts        # Toast notifications
│   └── useLocalStorage.ts  # Persistent state
└── lib/
    └── utils.ts            # Utility functions
\`\`\`

## Key Features Explained

### Real-Time Simulation
- Driver positions update every 2 seconds
- Random notifications every 15 seconds
- Clickable notifications that navigate to relevant tabs

### Data Persistence
- All state saved to localStorage
- Survives page refreshes
- Editable market prices persist

### Interactive Elements
- Click farmer rows to open detailed profiles
- Click driver cards to fly to their location on map
- Click market prices to edit them inline
- Press Enter to save, Escape to cancel

### Glassmorphism UI
- Frosted glass effect on header
- Backdrop blur and transparency
- Modern, premium look

### Toast Notifications
- System-wide notification system
- Clickable actions
- Auto-dismiss after 5 seconds

## Mock Data

### 10 Farmers
- Realistic Indian names
- Villages across Maharashtra
- Transaction histories with 3-4 entries each
- Revenue tracking from ₹165K to ₹385K
- Ratings from 4.4 to 5.0 stars

### 8 Drivers
- Mumbai/Pune region coordinates
- Various vehicle types (Tata Ace, Mahindra Pickup, etc.)
- Real Indian phone numbers
- Mixed Available/Busy status

### 11 Wholesalers/Traders
- Complete business profiles with GST numbers
- Credit limits from ₹5L to ₹50L
- Purchase histories with 3-4 transactions each
- Specializations in vegetables, fruits, grains
- Total volume tracking (50-500 tons)
- Active order counts
- Profit margin calculations
- Contact details and locations across Maharashtra

### 12 Market Items
- Common Indian crops (Mangoes, Onions, Tomatoes, etc.)
- Prices from ₹40 to ₹400 per kg
- APMC/Mandi locations
- Spoilage risk indicators

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari

## License

© 2026 Neural Roots Platform
