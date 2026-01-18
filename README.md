# 🌾 Neural Roots AI

> **AI-Powered Agricultural Platform for Indian Farmers**

An intelligent agricultural ecosystem that empowers farmers with real-time market prices, weather alerts, crop selling assistance, and logistics management through WhatsApp integration.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)
![Twilio](https://img.shields.io/badge/Twilio-WhatsApp-red?logo=twilio)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [WhatsApp Bot Commands](#-whatsapp-bot-commands)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## ✨ Features

### 🌾 For Farmers (WhatsApp Bot)
- **Crop Selling** - Sell crops at best mandi prices
- **Live Weather Updates** - Real-time weather with crop-specific precautions
- **Market Prices** - Compare prices across multiple mandis
- **Transport Booking** - Book vehicles for crop transportation
- **Multilingual Support** - Hindi keywords supported

### 📊 Admin Dashboard (Web)
- **Market Terminal** - Real-time price monitoring
- **Fleet Management** - Track transport vehicles
- **Farmer Analytics** - Registered farmer insights
- **Weather Monitoring** - Location-based forecasts
- **Live Activity Feed** - Real-time transaction logs

### 🤖 AI Agents
- **Market Agent** - Price analysis and mandi recommendations
- **Weather Agent** - Forecast analysis and crop risk assessment
- **Freshness Agent** - Crop quality prediction
- **Logistics Agent** - Route optimization

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NEURAL ROOTS AI                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│   │   WhatsApp   │      │   Frontend   │      │   IoT Data   │ │
│   │   (Twilio)   │      │   (Next.js)  │      │   Ingestion  │ │
│   └──────┬───────┘      └──────┬───────┘      └──────┬───────┘ │
│          │                     │                     │         │
│          └─────────────────────┼─────────────────────┘         │
│                                │                               │
│                    ┌───────────▼───────────┐                   │
│                    │   FastAPI Backend     │                   │
│                    │   ┌───────────────┐   │                   │
│                    │   │  AI Agents    │   │                   │
│                    │   │ ┌───────────┐ │   │                   │
│                    │   │ │ Market    │ │   │                   │
│                    │   │ │ Weather   │ │   │                   │
│                    │   │ │ Freshness │ │   │                   │
│                    │   │ │ Logistics │ │   │                   │
│                    │   │ └───────────┘ │   │                   │
│                    │   └───────────────┘   │                   │
│                    └───────────┬───────────┘                   │
│                                │                               │
│          ┌─────────────────────┼─────────────────────┐         │
│          │                     │                     │         │
│   ┌──────▼───────┐     ┌───────▼──────┐     ┌───────▼──────┐  │
│   │   MongoDB    │     │ OpenWeather  │     │   Gemini AI  │  │
│   │   Atlas      │     │     API      │     │              │  │
│   └──────────────┘     └──────────────┘     └──────────────┘  │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API Framework |
| **Python 3.10+** | Backend Language |
| **MongoDB Atlas** | Database |
| **Motor** | Async MongoDB Driver |
| **Twilio** | WhatsApp Integration |
| **Google Gemini** | AI/LLM for Insights |
| **OpenWeatherMap** | Weather Data |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 15** | React Framework |
| **TypeScript** | Type Safety |
| **Tailwind CSS** | Styling |
| **Leaflet** | Maps |
| **Radix UI** | Component Library |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB Atlas Account
- Twilio Account (for WhatsApp)
- OpenWeatherMap API Key
- Ngrok (for local webhook testing)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/neural-roots-ai.git
cd neural-roots-ai
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (optional)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 4. Start the Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Ngrok (for WhatsApp):**
```bash
ngrok http 8000
```

### 5. Configure Twilio Webhook
1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to **Messaging → Settings → WhatsApp Sandbox**
3. Set webhook URL: `https://YOUR-NGROK-URL.ngrok.io/api/whatsapp/webhook`
4. Method: `POST`

---

## 📁 Project Structure

```
neural-roots-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── agents/              # AI Agents
│   │   │   ├── market_agent.py
│   │   │   ├── weather_agent.py
│   │   │   ├── freshness_agent.py
│   │   │   └── logistics_agent.py
│   │   ├── core/                # Core configurations
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── graph.py
│   │   ├── models/              # Data models
│   │   │   └── schemas.py
│   │   ├── routers/             # API routes
│   │   │   ├── whatsapp_webhook.py
│   │   │   ├── weather.py
│   │   │   ├── market.py
│   │   │   └── iot_ingest.py
│   │   └── services/            # External services
│   │       ├── twilio_client.py
│   │       └── weather_api.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/              # React Components
│   │   ├── AnalyticsDashboard.tsx
│   │   ├── CommandCenter.tsx
│   │   ├── FarmersModule.tsx
│   │   ├── FleetModule.tsx
│   │   ├── MarketTerminal.tsx
│   │   └── ...
│   ├── hooks/                   # Custom Hooks
│   ├── lib/                     # Utilities
│   └── package.json
│
├── data/                        # Data files
├── iot/                         # IoT integration
├── docker-compose.yml
└── README.md
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Health Check
```http
GET /
GET /api/v1/health
```

### WhatsApp Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/whatsapp/webhook` | POST | Twilio webhook (incoming messages) |
| `/api/whatsapp/send` | POST | Send WhatsApp message |
| `/api/whatsapp/weather/{location}` | GET | Preview weather message |
| `/api/whatsapp/weather-alert` | POST | Send weather alert to farmer |
| `/api/whatsapp/broadcast-weather-alerts` | POST | Broadcast to all farmers |

### Weather Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/weather/current/{city}` | GET | Current weather |
| `/api/weather/forecast/{city}` | GET | 5-day forecast |
| `/api/weather/predict/{farmer_id}` | GET | Farmer-specific prediction |
| `/api/weather/locations` | GET | Supported locations |

### Market Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/prices` | GET | All market prices |
| `/api/v1/farmers` | GET | Registered farmers |

---

## 💬 WhatsApp Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `hi` / `hello` / `start` | Start conversation | "Hi" |
| `sell` | Start selling crops | "sell" |
| `weather` | Quick weather update | "weather" |
| `weather details` | Full forecast with precautions | "weather details" |
| `weather {city}` | Weather for specific city | "weather nashik" |
| `mausam` / `barish` | Hindi weather keywords | "mausam" |
| `price` / `market` | Check mandi prices | "price" |

### Conversation Flow
```
Farmer: "sell"
Bot: "Which crop do you want to sell?"
Farmer: "Tomatoes"
Bot: "How many kilograms?"
Farmer: "100"
Bot: [Shows mandi options with prices]
Farmer: "1"
Bot: "Confirm booking? Reply YES/NO"
Farmer: "YES"
Bot: [Booking confirmed with driver details]
```

---

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# MongoDB
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=neural_roots

# Weather API
OPENWEATHER_API_KEY=your_openweather_api_key

# Google Gemini AI
GOOGLE_API_KEY=your_gemini_api_key

# ML Model (optional)
MODEL_PATH=backend/app/models/fruit_model.keras
```

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individually
docker build -t neural-roots-backend ./backend
docker build -t neural-roots-frontend ./frontend
```

---

## 📊 Supported Locations (Maharashtra)

| City | Coordinates |
|------|-------------|
| Pune | 18.52°N, 73.86°E |
| Mumbai | 19.08°N, 72.88°E |
| Nashik | 20.00°N, 73.79°E |
| Kolhapur | 16.71°N, 74.24°E |
| Satara | 17.68°N, 74.02°E |
| Nagpur | 21.15°N, 79.09°E |
| Aurangabad | 19.88°N, 75.34°E |
| Solapur | 17.66°N, 75.91°E |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Neural Roots AI** - Empowering Indian Farmers with Technology

---

## 🙏 Acknowledgments

- [Twilio](https://twilio.com) for WhatsApp API
- [OpenWeatherMap](https://openweathermap.org) for Weather Data
- [Google Gemini](https://ai.google.dev) for AI capabilities
- [FastAPI](https://fastapi.tiangolo.com) for the amazing framework

---

<p align="center">
  Made with ❤️ for Indian Farmers
</p>
