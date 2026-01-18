# Quick ESP32 Status Check
Write-Host "`n=== ESP32 STATUS CHECK ===" -ForegroundColor Cyan

# Check devices
Write-Host "`nChecking ESP32 devices..." -ForegroundColor Yellow
$devices = Invoke-RestMethod http://localhost:8000/api/iot/devices

if ($devices.devices.Count -gt 0) {
    Write-Host "✅ ESP32 IS WORKING!" -ForegroundColor Green
    Write-Host "`nDevices found:" -ForegroundColor White
    foreach($d in $devices.devices) {
        Write-Host "  Device: $($d.device_id)" -ForegroundColor Cyan
        Write-Host "  Status: $($d.status)" -ForegroundColor $(if($d.status -eq "online"){"Green"}else{"Yellow"})
        Write-Host "  Last Temp: $($d.last_temp)°C" -ForegroundColor White
        Write-Host "  Last Humidity: $($d.last_hum)%" -ForegroundColor White
        Write-Host "  Total Readings: $($d.total_readings)" -ForegroundColor White
        Write-Host "  Last Seen: $($d.last_seen)`n" -ForegroundColor Gray
    }
    
    # Show recent readings
    Write-Host "Recent Readings:" -ForegroundColor Yellow
    $readings = Invoke-RestMethod "http://localhost:8000/api/iot/readings/esp32cam_01?limit=3"
    foreach($r in $readings.readings) {
        Write-Host "  $($r.timestamp) | Temp: $($r.temperature)°C | Hum: $($r.humidity)%" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  NO ESP32 DATA YET" -ForegroundColor Yellow
    Write-Host "`nPossible reasons:" -ForegroundColor Gray
    Write-Host "  1. ESP32 not powered on" -ForegroundColor White
    Write-Host "  2. ESP32 not connected to WiFi 'vivo'" -ForegroundColor White
    Write-Host "  3. ESP32 code not flashed yet" -ForegroundColor White
    Write-Host "  4. Wrong server IP in ESP32 code" -ForegroundColor White
    Write-Host "`nExpected: ESP32 should send data every 5 minutes" -ForegroundColor Gray
}

Write-Host "`n======================`n" -ForegroundColor Cyan
