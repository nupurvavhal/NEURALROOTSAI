/************************************************************
  ESP32-CAM (AI Thinker) + DHT11 + OLED + Live Stream + Backend Upload
  
  CONNECTS TO: Neural Roots AI Backend (FastAPI/Uvicorn)
  
  ENDPOINTS USED:
  - POST http://SERVER_IP:8000/api/iot/esp32/data  (sensor + optional image)
  - GET  http://SERVER_IP:8000/api/iot/ping        (connectivity check)
  
  FEATURES:
  - Live stream: http://ESP32_IP/stream
  - Web UI:      http://ESP32_IP/
  - Sensor JSON: http://ESP32_IP/data
  - OLED shows Temp/Hum always
  - Upload sensor data + image to backend every 5 minutes
  
  CONNECTIONS:
  DHT11:
    VCC -> 3.3V
    GND -> GND
    DATA-> GPIO13 (10k pullup to 3.3V if using bare sensor)

  OLED SSD1306 (I2C):
    VCC -> 3.3V
    GND -> GND
    SDA -> GPIO14
    SCL -> GPIO15
************************************************************/

#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>

// -------- DHT11 --------
#include "DHT.h"
#define DHTPIN 13
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// -------- OLED --------
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define OLED_SDA 14
#define OLED_SCL 15
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ============================================================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================================================
const char* WIFI_SSID = "vivo";                 // Your WiFi network name
const char* WIFI_PASSWORD = "12345670";         // Your WiFi password

// === BACKEND SERVER (Recommended - Your PC runs the backend) ===
const char* SERVER_IP = "10.199.195.212";       // Your PC IP address
const int SERVER_PORT = 8000;                    // Backend port (uvicorn)
const char* DEVICE_ID = "esp32cam_01";          // Unique device identifier

// Backend handles MongoDB Atlas connection automatically
// No need for MongoDB credentials in ESP32 code (more secure!)

// Upload interval (milliseconds)
const unsigned long UPLOAD_INTERVAL_MS = 30UL * 1000UL; // 30 seconds (for testing - change to 5*60*1000 for production)

// ============================================================================
// AI THINKER CAMERA PINS
// ============================================================================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// -------- WEB SERVER --------
WebServer server(80);

// Sensor readings
float latestTemp = -1;
float latestHum = -1;
bool serverConnected = false;

unsigned long lastSensorRead = 0;
unsigned long lastUploadTime = 0;

// ============================================================================
// Read DHT11 + update OLED (every 2 seconds)
// ============================================================================
void updateSensorsAndOLED() {
  if (millis() - lastSensorRead < 2000) return;
  lastSensorRead = millis();

  float t = dht.readTemperature();
  float h = dht.readHumidity();

  if (!isnan(t) && !isnan(h)) {
    latestTemp = t;
    latestHum = h;
  }

  // OLED display
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  display.setCursor(0, 0);
  display.println("NEURAL ROOTS IOT");

  display.setCursor(0, 16);
  display.print("Temp: ");
  display.print(latestTemp, 1);
  display.println(" C");

  display.setCursor(0, 28);
  display.print("Hum : ");
  display.print(latestHum, 1);
  display.println(" %");

  display.setCursor(0, 42);
  display.print("WiFi: ");
  display.println(WiFi.status() == WL_CONNECTED ? "OK" : "FAIL");

  display.setCursor(0, 54);
  display.print("Server: ");
  display.println(serverConnected ? "OK" : "---");

  display.display();

  Serial.printf("Temp=%.1fC  Hum=%.1f%%\n", latestTemp, latestHum);
}

// ============================================================================
// Camera init
// ============================================================================
void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QQVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    while (true) delay(1000);
  }
  Serial.println("Camera init OK");
}

// ============================================================================
// Web page UI
// ============================================================================
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>Neural Roots IoT - ESP32-CAM</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; text-align: center; background: #1a1a2e; color: #eee; padding: 20px; }
    h2 { color: #4ade80; }
    .card { background: #16213e; padding: 20px; border-radius: 10px; margin: 10px auto; max-width: 400px; }
    .value { font-size: 2em; color: #4ade80; }
    img { width: 100%; max-width: 400px; border-radius: 10px; border: 2px solid #4ade80; }
  </style>
</head>
<body>
  <h2>🌱 Neural Roots IoT</h2>
  <div class="card">
    <h3>Live Camera Stream</h3>
    <img src="/stream">
  </div>
  <div class="card">
    <h3>Sensor Data (DHT11)</h3>
    <p>Temperature: <span class="value" id="temp">--</span> °C</p>
    <p>Humidity: <span class="value" id="hum">--</span> %</p>
  </div>
  <div class="card">
    <p>Device ID: <strong>)rawliteral" + String(DEVICE_ID) + R"rawliteral(</strong></p>
    <p>Server: <strong>)rawliteral" + String(SERVER_IP) + ":" + String(SERVER_PORT) + R"rawliteral(</strong></p>
  </div>
  <script>
    async function updateData(){
      try {
        const res = await fetch("/data");
        const j = await res.json();
        document.getElementById("temp").innerText = j.temp.toFixed(1);
        document.getElementById("hum").innerText = j.hum.toFixed(1);
      } catch(e){}
    }
    setInterval(updateData, 2000);
    updateData();
  </script>
</body>
</html>
)rawliteral";
  server.send(200, "text/html", html);
}

// ============================================================================
// JSON endpoint for sensor values
// ============================================================================
void handleData() {
  String json = "{";
  json += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  json += "\"temp\":" + String(latestTemp) + ",";
  json += "\"hum\":" + String(latestHum) + ",";
  json += "\"server_connected\":" + String(serverConnected ? "true" : "false");
  json += "}";
  server.send(200, "application/json", json);
}

// ============================================================================
// Live stream handler
// ============================================================================
void handleStream() {
  WiFiClient client = server.client();
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
  server.sendContent(response);

  while (client.connected()) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      break;
    }
    server.sendContent("--frame\r\n");
    server.sendContent("Content-Type: image/jpeg\r\n");
    server.sendContent("Content-Length: " + String(fb->len) + "\r\n\r\n");
    client.write(fb->buf, fb->len);
    server.sendContent("\r\n");
    esp_camera_fb_return(fb);
    updateSensorsAndOLED();
    delay(50);
  }
}

// ============================================================================
// Check backend server connectivity
// ============================================================================
bool pingServer() {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/iot/ping";
  http.begin(url);
  http.setTimeout(5000);

  int httpCode = http.GET();
  http.end();

  bool ok = (httpCode >= 200 && httpCode < 300);
  Serial.printf("🔗 Backend ping: %s (HTTP %d)\n", ok ? "OK" : "FAIL", httpCode);
  return ok;
}

// ============================================================================
// Upload sensor data + image to Backend (Backend saves to MongoDB Atlas)
// ============================================================================
bool uploadToBackend(float temp, float hum) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ Upload skipped: WiFi not connected");
    serverConnected = false;
    return false;
  }

  // Capture image
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Camera capture failed");
    return false;
  }

  HTTPClient http;
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/iot/esp32/data";
  http.begin(url);
  http.setTimeout(15000);

  // Build multipart form data
  String boundary = "----ESP32CAMBoundary";
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

  String bodyStart = "";
  bodyStart += "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
  bodyStart += String(DEVICE_ID) + "\r\n";
  bodyStart += "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"temp\"\r\n\r\n";
  bodyStart += String(temp, 2) + "\r\n";
  bodyStart += "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"hum\"\r\n\r\n";
  bodyStart += String(hum, 2) + "\r\n";

  String imageHeader = "--" + boundary + "\r\n";
  imageHeader += "Content-Disposition: form-data; name=\"image\"; filename=\"capture.jpg\"\r\n";
  imageHeader += "Content-Type: image/jpeg\r\n\r\n";

  String bodyEnd = "\r\n--" + boundary + "--\r\n";

  size_t totalLen = bodyStart.length() + imageHeader.length() + fb->len + bodyEnd.length();

  uint8_t *payload = (uint8_t *)malloc(totalLen);
  if (!payload) {
    Serial.println("❌ Memory allocation failed");
    esp_camera_fb_return(fb);
    return false;
  }

  size_t offset = 0;
  memcpy(payload + offset, bodyStart.c_str(), bodyStart.length());
  offset += bodyStart.length();
  memcpy(payload + offset, imageHeader.c_str(), imageHeader.length());
  offset += imageHeader.length();
  memcpy(payload + offset, fb->buf, fb->len);
  offset += fb->len;
  memcpy(payload + offset, bodyEnd.c_str(), bodyEnd.length());

  int httpCode = http.POST(payload, totalLen);
  String response = http.getString();

  free(payload);
  esp_camera_fb_return(fb);
  http.end();

  serverConnected = (httpCode >= 200 && httpCode < 300);
  Serial.printf("📤 Upload: HTTP %d - %s\n", httpCode, serverConnected ? "SUCCESS" : "FAILED");
  if (response.length() > 0) {
    Serial.println("📥 Response: " + response);
  }

  return serverConnected;
}

// ============================================================================
// Upload sensor data only (no image) - lightweight fallback
// ============================================================================
bool uploadSensorOnly(float temp, float hum) {
  if (WiFi.status() != WL_CONNECTED) {
    serverConnected = false;
    return false;
  }

  HTTPClient http;
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/iot/esp32/data";
  http.begin(url);
  http.setTimeout(10000);

  String boundary = "----ESP32Boundary";
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

  String body = "";
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
  body += String(DEVICE_ID) + "\r\n";
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"temp\"\r\n\r\n";
  body += String(temp, 2) + "\r\n";
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"hum\"\r\n\r\n";
  body += String(hum, 2) + "\r\n";
  body += "--" + boundary + "--\r\n";

  int httpCode = http.POST(body);
  http.end();

  serverConnected = (httpCode >= 200 && httpCode < 300);
  Serial.printf("📊 Sensor-only upload: HTTP %d\n", httpCode);
  
  return serverConnected;
}

// ============================================================================
// SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n========================================");
  Serial.println("  NEURAL ROOTS AI - ESP32 IOT DEVICE");
  Serial.println("========================================");

  // DHT start
  dht.begin();
  delay(2000);

  // OLED start
  Wire.begin(OLED_SDA, OLED_SCL);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED init failed");
    // Continue without OLED
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 20);
  display.println("Initializing...");
  display.display();

  // Camera start
  setupCamera();

  // WiFi connect
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");

  display.clearDisplay();
  display.setCursor(0, 20);
  display.println("Connecting WiFi...");
  display.display();

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 30) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected!");
    Serial.print("ESP32 IP: http://");
    Serial.println(WiFi.localIP());
    Serial.print("Backend: http://");
    Serial.print(SERVER_IP);
    Serial.print(":");
    Serial.println(SERVER_PORT);

    // Test backend connection
    serverConnected = pingServer();
  } else {
    Serial.println("WiFi connection FAILED");
  }

  // Web routes
  server.on("/", HTTP_GET, handleRoot);
  server.on("/stream", HTTP_GET, handleStream);
  server.on("/data", HTTP_GET, handleData);
  server.begin();

  Serial.println("Web server started");
  Serial.println("========================================");
  Serial.println("⏱️  Upload Interval: 30 seconds");
  Serial.println("📡 Target: http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/iot/esp32/data");
  Serial.println("🔑 Device ID: " + String(DEVICE_ID));
  Serial.println("========================================\n");

  // Upload immediately on startup (don't wait 30 seconds)
  lastUploadTime = millis() - UPLOAD_INTERVAL_MS;
}

// ============================================================================
// LOOP - Main execution
// ============================================================================
void loop() {
  updateSensorsAndOLED();
  server.handleClient();

  // Show countdown in serial monitor
  unsigned long timeLeft = UPLOAD_INTERVAL_MS - (millis() - lastUploadTime);
  if (timeLeft > UPLOAD_INTERVAL_MS) timeLeft = 0; // Handle overflow
  if (millis() % 5000 < 100) { // Print every 5 seconds
    Serial.printf("⏱️  Next upload in: %lu seconds\n", timeLeft / 1000);
  }

  // Upload to backend every interval (backend saves to MongoDB Atlas)
  if (millis() - lastUploadTime >= UPLOAD_INTERVAL_MS) {
    Serial.println("\n========================================");
    Serial.println("  📡 Uploading to Backend → MongoDB Atlas");
    Serial.println("========================================");
    
    // Try uploading with image first
    bool ok = uploadToBackend(latestTemp, latestHum);
    
    // If fails, try sensor-only (no image)
    if (!ok) {
      Serial.println("⚠️  Retrying without image...");
      ok = uploadSensorOnly(latestTemp, latestHum);
    }
    
    Serial.println(ok ? "✅ Upload SUCCESS" : "❌ Upload FAILED");
    Serial.println("========================================\n");
    
    lastUploadTime = millis();
  }
}
