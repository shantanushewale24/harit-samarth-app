# START_ALL.ps1
# Complete startup script for Harit Samarth Platform
# Starts all necessary components: Backend, Frontend, Sensor Generator, MQTT Broker

Write-Host "================================" -ForegroundColor Cyan
Write-Host "HARIT SAMARTH COMPLETE STARTUP" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Create multiple terminal windows/processes
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting all components..." -ForegroundColor Yellow
Write-Host ""

# 1. Start MySQL Server (if not running)
Write-Host "[1/5] Checking MySQL Database..." -ForegroundColor Green
# MySQL is typically a service, so we'll just verify connection
try {
    $connection = New-Object System.Data.Odbc.OdbcConnection("Driver={MySQL ODBC 8.0 Driver};Server=localhost;")
    $connection.Open()
    $connection.Close()
    Write-Host "✓ MySQL is running" -ForegroundColor Green
} catch {
    Write-Host "⚠ MySQL not accessible - please start manually" -ForegroundColor Yellow
}
Write-Host ""

# 2. Start Backend API (Flask)
Write-Host "[2/5] Starting Flask Backend API (Port 5000)..." -ForegroundColor Green
$backendPath = Join-Path $scriptPath "backend"
$backendProcess = Start-Process -FilePath "python" -ArgumentList "$backendPath\app.py" `
    -WorkingDirectory $backendPath `
    -NoNewWindow `
    -PassThru
Write-Host "✓ Backend API starting (PID: $($backendProcess.Id))" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 3

# 3. Start Sensor Data Generator
Write-Host "[3/5] Starting Sensor Data Generator..." -ForegroundColor Green
$generatorProcess = Start-Process -FilePath "python" -ArgumentList "$backendPath\sensor_generator.py" `
    -WorkingDirectory $backendPath `
    -NoNewWindow `
    -PassThru
Write-Host "✓ Sensor Generator starting (PID: $($generatorProcess.Id))" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# 4. Start MQTT Subscriber (if you want MQTT mode)
Write-Host "[4/5] Starting MQTT Subscriber..." -ForegroundColor Green
$subscriberProcess = Start-Process -FilePath "python" -ArgumentList "$backendPath\mqtt_sensor_subscriber.py" `
    -WorkingDirectory $backendPath `
    -NoNewWindow `
    -PassThru
Write-Host "✓ MQTT Subscriber starting (PID: $($subscriberProcess.Id))" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# 5. Start Frontend (Vite)
Write-Host "[5/5] Starting Frontend React App (Port 8080)..." -ForegroundColor Green
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" `
    -WorkingDirectory $scriptPath `
    -NoNewWindow `
    -PassThru
Write-Host "✓ Frontend starting (PID: $($frontendProcess.Id))" -ForegroundColor Green
Write-Host ""

# Display summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "ALL COMPONENTS STARTED" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 DASHBOARD ACCESS:" -ForegroundColor Yellow
Write-Host "   Frontend:    http://localhost:8080" -ForegroundColor Cyan
Write-Host "   Hardware:    http://localhost:8080/hardware" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔌 API ENDPOINTS:" -ForegroundColor Yellow
Write-Host "   Latest Data: http://localhost:5000/api/soil-health/latest" -ForegroundColor Cyan
Write-Host "   History:     http://localhost:5000/api/soil-health/history" -ForegroundColor Cyan
Write-Host "   Stats:       http://localhost:5000/api/soil-health/stats" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 RUNNING PROCESSES:" -ForegroundColor Yellow
Write-Host "   Backend API ........... PID: $($backendProcess.Id)" -ForegroundColor Cyan
Write-Host "   Sensor Generator ..... PID: $($generatorProcess.Id)" -ForegroundColor Cyan
Write-Host "   MQTT Subscriber ....... PID: $($subscriberProcess.Id)" -ForegroundColor Cyan
Write-Host "   Frontend (React) ...... PID: $($frontendProcess.Id)" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏹  To stop all services, close these windows or run:" -ForegroundColor Yellow
Write-Host "   Stop-Process -Id $($backendProcess.Id), $($generatorProcess.Id), $($subscriberProcess.Id), $($frontendProcess.Id)" -ForegroundColor Gray
Write-Host ""

# Wait for user to stop
Write-Host "Press any key to terminate all services..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Write-Host ""
Write-Host "Stopping all services..." -ForegroundColor Yellow
Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $generatorProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $subscriberProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
Write-Host "✓ All services stopped" -ForegroundColor Green
