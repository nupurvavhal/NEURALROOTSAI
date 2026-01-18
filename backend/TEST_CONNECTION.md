# 🔗 ESP32 → Backend → MongoDB Connection Test

## ✅ Your Setup is Ready!

### Architecture:
```
ESP32-CAM (10.199.195.212)
    ↓ HTTP POST (multipart/form-data)
Backend Server (10.199.195.212:8000)
    ↓ MongoDB Driver (motor/pymongo)
MongoDB Atlas (mongodb+srv://user1:***@neuralnets.hfoano6.mongodb.net/)
```

---

## 📋 Step-by-Step Testing

### **STEP 1: Start Backend Server**

```powershell
cd F:\NEURALROOTSAI\backend
F:/NEURALROOTSAI/.venv/Scripts/uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Connected to MongoDB
INFO:     Application startup complete.
```

---

### **STEP 2: Test Backend (Before ESP32)**

Open PowerShell and test the endpoint:

```powershell
# Test ping endpoint
curl http://localhost:8000/api/iot/ping

# Test ESP32 endpoint info
curl http://localhost:8000/api/iot/esp32/data
```

**Expected Response:**
```json
{"status":"ok","message":"IoT API is running"}
```

---

### **STEP 3: Flash ESP32-CAM**

1. Open Arduino IDE
2. Open: `F:\NEURALROOTSAI\backend\esp32_firmware\esp32_cam_iot.ino`
3. Select Board: **ESP32 Wrover Module**
4. Select Port: Your ESP32 COM port
5. Click **Upload** ✅

---

### **STEP 4: Monitor ESP32 Serial Output**

Open Serial Monitor (115200 baud):

**Expected Output:**
```
========================================
  NEURAL ROOTS AI - ESP32 IOT DEVICE
========================================
📶 Connecting to WiFi: vivo
✅ WiFi connected! IP: 10.199.195.212

🔗 Backend ping: OK (HTTP 200)

========================================
  📡 Uploading to Backend → MongoDB Atlas
========================================
📤 Upload: HTTP 200 - SUCCESS
📥 Response: {"status":"success","image_saved":true}
✅ Upload SUCCESS
========================================
```

---

### **STEP 5: Verify Data in Backend Terminal**

Watch the backend terminal for incoming requests:

```
📡 ESP32 Data: esp32cam_01 | Temp: 26.5°C | Hum: 65.0%
📷 Image saved: esp32cam_01_a1b2c3d4_capture.jpg
INFO:     10.199.195.212:54321 - "POST /api/iot/esp32/data HTTP/1.1" 200 OK
```

---

### **STEP 6: Check MongoDB Atlas**

1. Go to https://cloud.mongodb.com/
2. Login to your account
3. Navigate to: **Databases** → **Browse Collections**
4. Select database: **neural_roots**
5. View collection: **iot_logs**

**You should see:**
```json
{
  "_id": ObjectId("..."),
  "device_id": "esp32cam_01",
  "farmer_id": "esp32cam_01",
  "temperature": 26.5,
  "humidity": 65.0,
  "image_url": "/uploads/esp32cam_01_a1b2c3d4_capture.jpg",
  "timestamp": "2026-01-18T12:34:56.789Z",
  "created_at": ISODate("2026-01-18T12:34:56.789Z")
}
```

---

## 🔧 Troubleshooting

### ❌ ESP32 shows "Upload FAILED"

**Check 1: WiFi Connected?**
- Serial should show: `✅ WiFi connected!`
- If not, check WiFi credentials in `.ino` file

**Check 2: Backend Running?**
- ESP32 should show: `🔗 Backend ping: OK (HTTP 200)`
- If FAIL, backend is not accessible

**Check 3: Correct IP?**
- ESP32 config: `SERVER_IP = "10.199.195.212"`
- Backend should be on same network

### ❌ Backend shows "Connection Refused"

**Solution:** Check MongoDB connection string in `.env`
```bash
# Verify .env file
cat backend/.env | findstr MONGODB
```

### ❌ MongoDB Atlas shows no data

**Solution:** Check database and collection names:
- Database: `neural_roots` ✅
- Collection: `iot_logs` ✅

---

## 🎯 Quick Test Command (Without ESP32)

Test the full backend pipeline using curl:

```powershell
# Create a test image
echo "fake image data" > test.jpg

# Send POST request
curl -X POST http://localhost:8000/api/iot/esp32/data `
  -F "device_id=test_device" `
  -F "temp=25.5" `
  -F "hum=60.0" `
  -F "image=@test.jpg"
```

**Expected Response:**
```json
{"status":"success","image_saved":true}
```

Then check MongoDB Atlas for the new entry! ✅

---

## 📊 Data Flow Summary

| Step | Component | Action |
|------|-----------|--------|
| 1️⃣ | ESP32-CAM | Captures image + reads DHT11 sensor |
| 2️⃣ | ESP32-CAM | Creates multipart form POST request |
| 3️⃣ | ESP32-CAM | Sends to `http://10.199.195.212:8000/api/iot/esp32/data` |
| 4️⃣ | Backend FastAPI | Receives POST, saves image to `/uploads/` |
| 5️⃣ | Backend FastAPI | Inserts data into MongoDB using connection string |
| 6️⃣ | MongoDB Atlas | Stores document in `neural_roots.iot_logs` |
| 7️⃣ | Backend AI | Triggers workflow analysis (temp alerts, etc.) |

---

## ✅ Success Indicators

- ✅ ESP32 Serial: `✅ Upload SUCCESS`
- ✅ Backend Terminal: `📡 ESP32 Data: esp32cam_01 | Temp: 26.5°C`
- ✅ MongoDB Atlas: New document appears in `iot_logs` collection
- ✅ File System: Image saved in `backend/app/uploads/`

---

## 🚀 Next Steps After Testing

1. **View uploaded images:** http://10.199.195.212:8000/uploads/esp32cam_01_*.jpg
2. **Check device list:** http://10.199.195.212:8000/api/iot/devices
3. **Get readings:** http://10.199.195.212:8000/api/iot/readings/esp32cam_01
4. **ESP32 Web UI:** http://10.199.195.212/ (ESP32's IP)

---

**Your connection is configured and ready to work!** 🎉
Just start the backend and flash the ESP32 code.
