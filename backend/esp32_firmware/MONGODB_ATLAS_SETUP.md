# MongoDB Atlas REST API Setup Guide for ESP32

## Step-by-Step Setup

### 1. Create MongoDB Atlas Account
- Go to https://www.mongodb.com/cloud/atlas
- Sign up (free tier available)
- Create a new project

### 2. Create a Cluster
- Click "Build a Cluster"
- Choose **M0 Sandbox** (free tier)
- Select region closest to you
- Wait for cluster to deploy (5-10 mins)

### 3. Enable Data API
- In your cluster, go to **Data API** (left sidebar)
- Click **Enable Data API**
- Copy your **App ID** (looks like: `data-xxxxx`)

### 4. Create API Key
- Go to **App Services** → Your App
- Click **API Keys** section
- Create new API Key
- Copy the **API Key** (keep it secret!)

### 5. Get Your Endpoint
- In Data API section, find the endpoint URL
- Format: `https://data.mongodb-api.com/app/{APP_ID}/endpoint/data/v1/action/insertOne`

### 6. Update ESP32 Code
In `esp32_cam_iot.ino`, lines ~60-65, update:

```cpp
const char* MONGODB_APP_ID = "YOUR_APP_ID_HERE";       // Replace with App ID
const char* MONGODB_API_KEY = "YOUR_API_KEY_HERE";     // Replace with API Key
const char* MONGODB_DATABASE = "neural_roots";         // Database name
const char* MONGODB_COLLECTION = "iot_logs";           // Collection name
const char* MONGODB_API_URL = "https://data.mongodb-api.com/app/YOUR_APP_ID_HERE/endpoint/data/v1/action/insertOne";
```

### 7. Flash ESP32
- Copy the updated code to Arduino IDE
- Select Board: **ESP32 Wrover Module** or your variant
- Upload sketch

### 8. Verify in MongoDB
- Go to MongoDB Atlas Dashboard
- Click "Browse Collections"
- You should see documents appearing in `neural_roots.iot_logs`

## Data Format Sent to MongoDB

Each document looks like:
```json
{
  "device_id": "esp32cam_01",
  "farmer_id": "esp32cam_01",
  "temperature": 26.50,
  "humidity": 65.20,
  "timestamp": "1234567890",
  "image_url": "",
  "status": "online"
}
```

## Troubleshooting

### "403 Forbidden" Error
- ❌ API Key is invalid
- ✅ Check you copied it correctly
- ✅ Verify it in MongoDB Atlas

### "401 Unauthorized"
- ❌ API Key not in request header
- ✅ Code automatically includes it

### No data appearing
- ✅ Check ESP32 serial output
- ✅ Verify WiFi is connected
- ✅ Ensure database/collection names match

### Cannot find Data API option
- ❌ You may have old tier cluster
- ✅ Create new M0 Sandbox cluster

## API Rate Limits
- Free tier: 1,000 requests/day
- Paid tier: Higher limits

## Security Note
- 🔒 Keep API Key private (not in Git)
- 🔒 Don't share publicly
- 🔒 Use environment variables in production

## Next Steps
1. Verify data appears in MongoDB
2. Query data from backend/frontend
3. Add front-end dashboard to visualize
