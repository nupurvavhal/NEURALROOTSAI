# Connection Check Script for Neural Roots IoT System
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  NEURAL ROOTS - CONNECTION CHECK" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Backend API Check
Write-Host "1. Testing Backend API..." -ForegroundColor Yellow
try {
    $ping = Invoke-RestMethod -Uri http://localhost:8000/api/iot/ping -ErrorAction Stop
    Write-Host "   ✅ Backend Status: $($ping.status)" -ForegroundColor Green
    Write-Host "   ✅ Timestamp: $($ping.timestamp)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend OFFLINE - Start backend first!" -ForegroundColor Red
    Write-Host "      Run: F:\NEURALROOTSAI\backend\start_backend.bat`n" -ForegroundColor Yellow
    exit
}

# 2. MongoDB Connection Check
Write-Host "`n2. Testing MongoDB Connection..." -ForegroundColor Yellow
try {
    $devices = Invoke-RestMethod -Uri http://localhost:8000/api/iot/devices -ErrorAction Stop
    Write-Host "   ✅ MongoDB Connected" -ForegroundColor Green
    Write-Host "   ✅ Devices Registered: $($devices.devices.Count)" -ForegroundColor Green
    if ($devices.devices.Count -gt 0) {
        Write-Host "   📱 Devices:" -ForegroundColor Cyan
        foreach ($dev in $devices.devices) {
            Write-Host "      - $($dev.device_id) [$($dev.status)]" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   ❌ MongoDB Connection FAILED" -ForegroundColor Red
}

# 3. ESP32 Endpoint Check
Write-Host "`n3. Testing ESP32 Upload Endpoint..." -ForegroundColor Yellow
try {
    $esp32 = Invoke-RestMethod -Uri http://localhost:8000/api/iot/esp32/data -ErrorAction Stop
    Write-Host "   ✅ ESP32 Endpoint Ready" -ForegroundColor Green
    Write-Host "   📝 Required Fields: $($esp32.fields_required -join ', ')" -ForegroundColor White
    Write-Host "   📝 Optional Fields: $($esp32.fields_optional -join ', ')" -ForegroundColor White
} catch {
    Write-Host "   ❌ ESP32 Endpoint FAILED" -ForegroundColor Red
}

# 4. Network Configuration
Write-Host "`n4. Network Configuration Check..." -ForegroundColor Yellow
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "10.*" -or $_.IPAddress -like "192.168.*"}).IPAddress | Select-Object -First 1
if ($localIP) {
    Write-Host "   ✅ Local IP: $localIP" -ForegroundColor Green
    if ($localIP -eq "10.199.195.212") {
        Write-Host "   ✅ IP Matches ESP32 Config" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  IP Changed! Update ESP32 code:" -ForegroundColor Yellow
        Write-Host "      SERVER_IP = `"$localIP`"" -ForegroundColor White
    }
} else {
    Write-Host "   ❌ No Local IP Found" -ForegroundColor Red
}

# 5. ESP32 Configuration Summary
Write-Host "`n5. ESP32 Configuration:" -ForegroundColor Yellow
Write-Host "   📡 Target URL: http://10.199.195.212:8000/api/iot/esp32/data" -ForegroundColor White
Write-Host "   🔑 Device ID: esp32cam_01" -ForegroundColor White
Write-Host "   📶 WiFi SSID: vivo" -ForegroundColor White
Write-Host "   ⏱️  Upload Interval: 5 minutes" -ForegroundColor White

# 6. File Check
Write-Host "`n6. Project Files:" -ForegroundColor Yellow
if (Test-Path "F:\NEURALROOTSAI\backend\app\uploads") {
    Write-Host "   ✅ Uploads Directory: EXISTS" -ForegroundColor Green
} else {
    Write-Host "   ❌ Uploads Directory: MISSING" -ForegroundColor Red
}

if (Test-Path "F:\NEURALROOTSAI\backend\esp32_firmware\esp32_cam_iot.ino") {
    Write-Host "   ✅ ESP32 Firmware: READY" -ForegroundColor Green
} else {
    Write-Host "   ❌ ESP32 Firmware: MISSING" -ForegroundColor Red
}

# 7. Test Data Upload (Optional)
Write-Host "`n7. Test Data Upload..." -ForegroundColor Yellow
$choice = Read-Host "   Send test data? (y/n)"
if ($choice -eq "y") {
    try {
        $form = @{
            device_id = "test_connection"
            temp = 25.5
            hum = 60.0
        }
        $result = Invoke-RestMethod -Uri http://localhost:8000/api/iot/esp32/data -Method Post -Form $form -ErrorAction Stop
        Write-Host "   ✅ Test Upload SUCCESS" -ForegroundColor Green
        Write-Host "   📊 Response: $($result.message)" -ForegroundColor White
    } catch {
        Write-Host "   ❌ Test Upload FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CONNECTION CHECK COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
